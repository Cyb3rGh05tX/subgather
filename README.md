#subgather




Subdomain Hacker is a modular, high-octane subdomain enumeration tool built for security researchers and pentesters. With a neon-drenched, hacker vibe, it combines passive (API-driven), active (DNS brute-force), and permutation enumeration to find every subdomain possible. Real-time monitoring, colorful output, and a sleek result table make it a joy to use. Designed for extensibility, it’s ready for future modules like real IP finding, tech detection, and CVE scanning.

---

🚀 Features

Cyberpunk Flair: Neon-green ASCII art, vibrant terminal output, and progress bars.

Live Monitoring: Real-time subdomain discovery with dynamic progress updates.



#Enumeration Modes:


Passive: Scrapes crt.sh and certspotter without touching the target.

Active: Brute-forces subdomains via DNS with your wordlist.

Permutation: Generates and resolves variations (e.g., dev-api, mail-1).

Results: Deduplicated, sorted subdomains saved to a file, with a detailed summary table.

Modular Core: Easy to extend with new recon features.

---

🛠️ Setup


*Clone the repo:*

```
git clone https://github.com/your-username/subdomain-hacker.git
cd subdomain-hacker
```


*Install dependencies:*
```
pip install -r requirements.txt
```

*Grab wordlists:*


Brute-force: SecLists (subdomains-top1million-5000.txt recommended).





Known Subdomains: Create known_subs.txt:

Dependencies

Install with:
```
pip install -r requirements.txt
```

Python 3.8+ required.

🔧 Usage

Command:
```

python subgather.py --domain <domain> [--output <file>] [--passive] [--active --brute-wordlist <path>] [--permutation --known-subs <path> [--perm-wordlist <path>]] [--threads <num>]
```

Options



```
--domain: Target domain (e.g., example.com).

```

--output: Output file (default: subdomains.txt).

```

--passive: Use passive sources (crt.sh, certspotter).

```

--active: Brute-force with DNS (needs --brute-wordlist).

```

--brute-wordlist: Path to brute-force wordlist.

```

--permutation: Generate variations (needs --known-subs).

```

--known-subs: Path to known subdomains file.
```


--perm-wordlist: Path to permutation wordlist (optional).

```

--threads: Threads for active/permutation (default: 50).
```


#Examples


*Passive scan:*
```
python subgather.py --domain example.com --passive
```


*Active brute-force:*
```
python subgather.py --domain example.com --active --brute-wordlist subdomains-top1million-5000.txt
```


*Permutation scan:*
```
python subgather.py --domain example.com --permutation --known-subs known_subs.txt --perm-wordlist perm_list.txt

```

*Full power:*
```
python subgather.py --domain example.com --passive --active --brute-wordlist subdomains-top1million-5000.txt --permutation --known-subs known_subs.txt
```


*Help:*
```
python subgather.py --help
```
📡 Output
```

Live: Neon-colored updates (e.g., [PASSIVE] Found: api.example.com) with progress bars.

File: Sorted, unique subdomains in subdomains.txt.

Summary: Table with counts, total subdomains, and runtime.
```
Example:
```
┌──[📊 Results]──
┌───────────────┬───────┬──────────────────────────┐
│ Category      │ Count │ Details                  │
├───────────────┴───────┴──────────────────────────┤
│ Passive       │ 12    │ crt.sh, certspotter      │
│ Active        │ 8     │ DNS brute-force          │
│ Permutation   │ 5     │ Generated variations      │
│ Total Unique  │ 22    │ Saved to subdomains.txt  │
│ Time Taken    │ 15.67 │ Seconds                  │
└───────────────┴───────┴──────────────────────────┘
Hacked! 22 subdomains saved.
```
📚 Wordlists




Brute-Force: SecLists:

subdomains-top1million-5000.txt (fast)

subdomains-top1million-110000.txt (deep)

bitquark-subdomains-top100000.txt

Permutation: perm_list.txt with prefixes (e.g., dev, api).

Known Subdomains: known_subs.txt from passive scans or manual input.



⚠️ Ethical Use

Legal: Only scan domains you own or have permission for. Unauthorized use may violate laws.

Rate Limits: Keep --threads low (e.g., 50) to avoid DNS server issues.

Test Safely: Use on controlled environments first.



🔮 Future Plans


Real IP discovery (bypassing CDNs).

Tech detection (wappalyzer, beautifulsoup4).

CVE scanning (NVD API).

More passive sources (VirusTotal, SecurityTrails).

Integration with tools like subfinder.

🤝 Contributing




Open a PR.

See CONTRIBUTING.md.

📜 License

MIT License

📩 Contact

File issues or PRs on GitHub.

Hack the planet, responsibly! 🌌
