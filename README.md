LinkedIn Jobs CLI — type `jobs` to list NEW & UNAPPLIED roles in your terminal

Overview
--------
This CLI avoids brittle LinkedIn scraping (which violates ToS and breaks often)
by reading your **email job alerts** (e.g., "LinkedIn Job Alert") via the
Gmail API, extracting job cards, and storing them locally. You get a clean
bullet-point list of new roles you haven't marked as applied.

Commands
--------
  jobs                 # List new + unapplied jobs (default command)
  fetch                # Pull latest job alerts from Gmail and store them
  apply <id>           # Mark a job as applied (hides it from the default list)
  seen <id>            # Mark a job as seen (but not applied)
  ignore <id>          # Hide a job without marking as applied
  all                  # List everything (including applied/ignored)
  open <id>            # Open the job in your browser
  reset                # Wipe local database (careful)
  settings ...         # Manage filters that decide which jobs are shown

Setup (one-time)
----------------
1) Python packages (create a venv if you like):
   pip install -r requirements.txt

2) Gmail API credentials:
   • Go to https://console.cloud.google.com/apis/credentials
   • Create OAuth Client ID (Desktop app). Download `credentials.json` to the
     same folder as this script.
   • On first `python jobs_cli.py fetch`, your browser will ask to authorize
     Gmail read access; this creates `token.json` locally.

3) Make it a shell command named `jobs`:
   chmod +x jobs_cli.py
   # Option A: symlink into a folder on your PATH (e.g., ~/.local/bin)
   ln -s "$(pwd)/jobs_cli.py" ~/.local/bin/jobs
   # Option B: add an alias to your shell rc file
   alias jobs="python /full/path/to/jobs_cli.py"

Notes
-----
• Source of truth is email alerts (e.g., "LinkedIn Job Alert"). You can extend
  the parser to handle other sources (Lever/Greenhouse/Muse/Adzuna).
• "Applied" status is tracked locally; you mark it via the `apply` command.
• This script **does not** scrape LinkedIn directly.

requirements.txt
----------------
rich
typer
beautifulsoup4
google-auth-oauthlib
google-auth
google-api-python-client
html5lib
