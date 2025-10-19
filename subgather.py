import argparse
import requests
import json
import dns.resolver
import dns.exception
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import time

console = Console()

def print_hacker_banner():
    banner = """
  ::::::::  :::    ::: :::::::::   ::::::::      ::: ::::::::::: :::    ::: :::::::::: :::::::::  
:+:    :+: :+:    :+: :+:    :+: :+:    :+:   :+: :+:   :+:     :+:    :+: :+:        :+:    :+: 
+:+        +:+    +:+ +:+    +:+ +:+         +:+   +:+  +:+     +:+    +:+ +:+        +:+    +:+ 
+#++:++#++ +#+    +:+ +#++:++#+  :#:        +#++:++#++: +#+     +#++:++#++ +#++:++#   +#++:++#:  
       +#+ +#+    +#+ +#+    +#+ +#+   +#+# +#+     +#+ +#+     +#+    +#+ +#+        +#+    +#+ 
#+#    #+# #+#    #+# #+#    #+# #+#    #+# #+#     #+# #+#     #+#    #+# #+#        #+#    #+# 
 ########   ########  #########   ########  ###     ### ###     ###    ### ########## ###    ### 
    """
    console.print(Panel(banner, style="bold green", border_style="cyan"))

def passive_enum(domain, progress, task_id):
    """
    Passive enumeration using crt.sh and certspotter.
    """
    subdomains = set()
    
    # crt.sh
    progress.console.print("[green]Hacking crt.sh for subdomains...[/green]")
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            for entry in data:
                name_value = entry.get('name_value', '').strip('*.')
                if name_value.endswith(domain) and name_value not in subdomains:
                    subdomains.add(name_value)
                    progress.console.print(f"[cyan][PASSIVE] Found: {name_value}[/cyan]")
                    progress.advance(task_id)
    except Exception as e:
        progress.console.print(f"[red]Error querying crt.sh: {e}[/red]")
    
    # certspotter
    progress.console.print("[green]Hacking certspotter for subdomains...[/green]")
    try:
        url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            for entry in data:
                for dns_name in entry.get('dns_names', []):
                    dns_name = dns_name.strip('*.')
                    if dns_name.endswith(domain) and dns_name not in subdomains:
                        subdomains.add(dns_name)
                        progress.console.print(f"[cyan][PASSIVE] Found: {dns_name}[/cyan]")
                        progress.advance(task_id)
    except Exception as e:
        progress.console.print(f"[red]Error querying certspotter: {e}[/red]")
    
    return subdomains

def resolve_subdomain(subdomain, progress, task_id):
    """
    Helper to resolve a subdomain to check if it exists.
    """
    try:
        answers = dns.resolver.resolve(subdomain, 'A')
        progress.console.print(f"[magenta][ACTIVE] Resolved: {subdomain}[/magenta]")
        progress.advance(task_id)
        return subdomain
    except dns.exception.DNSException:
        progress.advance(task_id)
        return None

def active_brute(domain, wordlist_path, max_threads, progress, task_id):
    """
    Active brute-force enumeration using DNS queries.
    """
    subdomains = set()
    if not os.path.exists(wordlist_path):
        progress.console.print(f"[red]Wordlist not found: {wordlist_path}[/red]")
        return subdomains
    
    with open(wordlist_path, 'r') as f:
        words = [line.strip() for line in f if line.strip()]
    
    candidates = [f"{word}.{domain}" for word in words]
    progress.update(task_id, total=len(candidates))
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(resolve_subdomain, cand, progress, task_id) for cand in candidates]
        for future in as_completed(futures):
            result = future.result()
            if result:
                subdomains.add(result)
    
    return subdomains

def generate_permutations(known_subs, perm_wordlist):
    """
    Simple permutation generation: append/prepend numbers, common words, hyphens.
    """
    permutations = set(known_subs)
    patterns = ['dev', 'test', 'stage', 'prod', 'api', 'admin', 'backup', 'mail', 'ftp']
    
    if perm_wordlist and os.path.exists(perm_wordlist):
        with open(perm_wordlist, 'r') as f:
            patterns.extend([line.strip() for line in f if line.strip()])
    
    for sub in list(known_subs):
        for pat in patterns:
            permutations.add(f"{pat}.{sub}")
            permutations.add(f"{sub}.{pat}")
            permutations.add(f"{sub}-{pat}")
            permutations.add(f"{pat}-{sub}")
        for i in range(10):
            permutations.add(f"{sub}{i}")
            permutations.add(f"{sub}-{i}")
            permutations.add(f"{i}-{sub}")
        if 'o' in sub:
            permutations.add(sub.replace('o', '0'))
    
    return permutations

def active_permutation(domain, known_subs_path, perm_wordlist, max_threads, progress, task_id):
    """
    Permutation-based enumeration: Generate and resolve permutations of known subdomains.
    """
    if not os.path.exists(known_subs_path):
        progress.console.print(f"[red]Known subs file not found: {known_subs_path}[/red]")
        return set()
    
    with open(known_subs_path, 'r') as f:
        known_subs = {line.strip().rstrip(f".{domain}").strip() for line in f if line.strip()}
    
    candidates = generate_permutations(known_subs, perm_wordlist)
    full_candidates = {f"{cand}.{domain}" if not cand.endswith(domain) else cand for cand in candidates}
    progress.update(task_id, total=len(full_candidates))
    
    subdomains = set()
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(resolve_subdomain, cand, progress, task_id) for cand in full_candidates]
        for future in as_completed(futures):
            result = future.result()
            if result:
                subdomains.add(result)
    
    return subdomains

def show_results(passive_subs, active_subs, perm_subs, output_file, elapsed_time):
    """
    Display final results in a colorful table.
    """
    total_subs = len(passive_subs | active_subs | perm_subs)
    table = Table(title="[bold green]Subdomain Enumeration Results[/bold green]", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Count", style="green")
    table.add_column("Details", style="cyan")
    
    table.add_row("Passive", str(len(passive_subs)), "From crt.sh, certspotter")
    table.add_row("Active", str(len(active_subs)), "Brute-forced via DNS")
    table.add_row("Permutation", str(len(perm_subs)), "Generated variations")
    table.add_row("Total Unique", str(total_subs), f"Saved to {output_file}")
    table.add_row("Time Taken", f"{elapsed_time:.2f} seconds", "Enumeration duration")
    
    console.print(table)
    if total_subs > 0:
        console.print(f"[bold green]Success! {total_subs} subdomains saved to {output_file}[/bold green]")
    else:
        console.print("[red]No subdomains found. Check your inputs or network.[/red]")

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Subdomain Enumerator with Hacker Vibe")
    parser.add_argument("--domain", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("--output", default="subdomains.txt", help="Output file for sorted unique subdomains")
    parser.add_argument("--passive", action="store_true", help="Enable passive enumeration (crt.sh, certspotter)")
    parser.add_argument("--active", action="store_true", help="Enable active brute-force (requires --brute-wordlist)")
    parser.add_argument("--brute-wordlist", help="Path to wordlist for brute-force")
    parser.add_argument("--permutation", action="store_true", help="Enable permutation enumeration (requires --known-subs)")
    parser.add_argument("--known-subs", help="Path to file with known subdomains for permutations")
    parser.add_argument("--perm-wordlist", help="Path to wordlist for permutations")
    parser.add_argument("--threads", type=int, default=50, help="Max threads for active/permutation (default: 50)")
    
    # Check if no arguments or --help is provided
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Validate arguments after showing help
    if not (args.passive or args.active or args.permutation):
        console.print("[red]Error: At least one method must be enabled (--passive, --active, or --permutation)[/red]")
        sys.exit(1)
    
    if args.active and not args.brute_wordlist:
        console.print("[red]Error: --active requires --brute-wordlist[/red]")
        sys.exit(1)
    
    if args.permutation and not args.known_subs:
        console.print("[red]Error: --permutation requires --known-subs[/red]")
        sys.exit(1)
    
    # Show banner only after valid arguments
    print_hacker_banner()
    
    start_time = time.time()
    passive_subs = set()
    active_subs = set()
    perm_subs = set()
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console
    ) as progress:
        if args.passive:
            task = progress.add_task("[green]Passive Enumeration[/green]", total=100)  # Arbitrary total for passive
            passive_subs = passive_enum(args.domain, progress, task)
        
        if args.active:
            console.print("[green]Starting active brute-force...[/green]")
            task = progress.add_task("[magenta]Active Brute-Force[/magenta]", total=0)
            active_subs = active_brute(args.domain, args.brute_wordlist, args.threads, progress, task)
        
        if args.permutation:
            console.print("[green]Starting permutation enumeration...[/green]")
            task = progress.add_task("[magenta]Permutation Enumeration[/magenta]", total=0)
            perm_subs = active_permutation(args.domain, args.known_subs, args.perm_wordlist, args.threads, progress, task)
    
    # Dedup, sort, write to file
    all_subdomains = passive_subs | active_subs | perm_subs
    sorted_subs = sorted(all_subdomains)
    with open(args.output, 'w') as f:
        for sub in sorted_subs:
            f.write(f"{sub}\n")
    
    elapsed_time = time.time() - start_time
    show_results(passive_subs, active_subs, perm_subs, args.output, elapsed_time)

if __name__ == "__main__":
    main()
