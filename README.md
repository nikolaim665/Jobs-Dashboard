# 💼 LinkedIn Jobs CLI

**Type `jobs` to list NEW & UNAPPLIED roles — right in your terminal.**

A terminal CLI for tracking LinkedIn job offers via Gmail! Fetch jobs from Gmail alerts, filter by your preferences, and track which ones you've applied to.

---

## ✨ Features

- 📬 **Gmail Integration** - Fetch LinkedIn job alerts from your personal Gmail
- 🔍 **Smart Filtering** - Filter by title, company, location, and job age
- ✅ **Application Tracking** - Mark jobs as applied, seen, or ignored
- 🎨 **Clean Terminal UI** - Beautiful output powered by Rich
- 🎓 **University Account Workaround** - Use personal Gmail when university blocks API access

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd Jobs-Dashboard

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Gmail API (Use Personal Gmail!)

**Important:** If your university Gmail blocks API project creation, use your personal Gmail account instead.

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing one
3. **Enable Gmail API** (very important!)
4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: "LinkedIn Jobs CLI" (or whatever you want)
5. Download `credentials.json`
6. Place it in the project directory or `~/.linkedin_jobs_cli/`:
   ```bash
   mv ~/Downloads/credentials.json ~/.linkedin_jobs_cli/credentials.json
   ```

### 3. Set Up LinkedIn Job Alerts

1. Go to [LinkedIn Jobs](https://www.linkedin.com/jobs/)
2. Search with your preferred filters
3. Click "Create job alert" or the bell icon
4. Set frequency to "Daily" (recommended)
5. **Make sure alerts go to your personal Gmail** (not university email)

### 4. First Run - Authorize the App

```bash
python jobs_cli.py fetch
```

Your browser will open asking you to authorize Gmail access. **Choose your personal Gmail account** (not university).

### 5. View Your Jobs

```bash
python jobs_cli.py
```

---

## 🔧 Make it a Global CLI Command

Instead of typing `python jobs_cli.py fetch` every time, you can set it up so you just type `jobs fetch` from anywhere!

### Option 1: Shell Wrapper Script (Recommended - Works from Anywhere)

This creates a wrapper script that automatically activates your venv:

```bash
# Create the wrapper script
cat > ~/.local/bin/jobs << 'EOF'
#!/bin/bash
source "$HOME/development/Jobs-Dashboard/.venv/bin/activate"
python "$HOME/development/Jobs-Dashboard/jobs_cli.py" "$@"
deactivate
EOF

# Make it executable
chmod +x ~/.local/bin/jobs
```

**Make sure `~/.local/bin` is in your PATH**. Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option 2: Shell Alias (Simpler, but requires venv activation)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias jobs='source ~/development/Jobs-Dashboard/.venv/bin/activate && python ~/development/Jobs-Dashboard/jobs_cli.py'
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option 3: Direct Symlink (Advanced - Requires shebang)

```bash
# Make the script executable
chmod +x ~/development/Jobs-Dashboard/jobs_cli.py

# Create symlink
ln -s ~/development/Jobs-Dashboard/jobs_cli.py ~/.local/bin/jobs
```

**Note:** This only works if your venv packages are globally accessible or you modify the script's shebang.

### ✅ Test It Works

From any directory:

```bash
jobs              # List new jobs
jobs fetch        # Fetch from Gmail
jobs apply 5      # Mark job 5 as applied
jobs settings show  # View settings
```

---

## 📖 Usage

### Basic Commands

```bash
# List new jobs (default command)
jobs

# Fetch new jobs from Gmail
jobs fetch

# Fetch with more results
jobs fetch --max-results 100

# Mark a job as applied
jobs apply 5

# Mark as seen (but not applied)
jobs seen 5

# Hide a job without marking applied
jobs ignore 5

# Open a job in browser
jobs open 5

# View all jobs (including applied/ignored)
jobs all
```

### Filter Management

```bash
# View current filter settings
jobs settings show

# Add filters
jobs settings add include_titles "senior"
jobs settings add include_titles "engineer"
jobs settings add include_locations "remote"
jobs settings add exclude_companies "Meta"
jobs settings add exclude_companies "Amazon"

# Set max age (hide jobs older than N days)
jobs settings set max_age_days 14

# Remove a filter
jobs settings remove exclude_companies "Meta"

# Clear all filters
jobs settings reset --confirm
```

---

## 🔄 Alternative: RSS Feeds

**Note:** LinkedIn's native RSS has been deprecated, but you can use RSS feeds from other job boards:

```bash
# Add RemoteOK RSS feed
jobs settings add rss_feeds "https://remoteok.com/remote-dev-jobs.rss"

# Add Remotive RSS feed
jobs settings add rss_feeds "https://remotive.com/remote-jobs/software-dev/feed"

# Fetch from RSS instead of Gmail
jobs fetch --source rss

# Or fetch from both sources
jobs fetch --source both
```

---

## 🛠 Troubleshooting

### "credentials.json not found"
Make sure the file is at `~/.linkedin_jobs_cli/credentials.json`:
```bash
ls -la ~/.linkedin_jobs_cli/
```

### "Gmail API has not been used in project"
You need to enable the Gmail API:
1. Go to https://console.cloud.google.com/apis/library
2. Search "Gmail API"
3. Click "Enable"

### "Access blocked: This app's request is invalid" (403 error)
Add yourself as a test user:
1. Go to https://console.cloud.google.com/apis/credentials/consent
2. Scroll to "Test users"
3. Click "+ ADD USERS"
4. Add your personal Gmail
5. Delete `~/.linkedin_jobs_cli/token.json` and try again

### "No jobs found"
- Wait for LinkedIn to send job alerts (can take up to 24 hours)
- Verify alerts are going to your personal Gmail
- Check Gmail for "LinkedIn Job Alert" emails

### Command not found: jobs
Make sure `~/.local/bin` is in your PATH:
```bash
echo $PATH | grep ".local/bin"
```

If not, add to `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## 📂 Project Structure

```
Jobs-Dashboard/
├── jobs_cli.py          # Main CLI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── SETUP_GMAIL.md      # Detailed Gmail setup guide
└── ~/.linkedin_jobs_cli/  # User data directory
    ├── credentials.json   # OAuth credentials
    ├── token.json        # Access token (auto-generated)
    ├── settings.json     # Your filters
    └── jobs.db          # SQLite database
```

---

## 🔒 Privacy & Security

- **Read-only access**: The CLI can only READ your Gmail, not send or delete emails
- **Local storage**: All data stored locally in `~/.linkedin_jobs_cli/`
- **Your control**: Revoke access anytime at https://myaccount.google.com/permissions
- **No tracking**: No analytics, no data sent anywhere

---

## 📝 License

This project is open source. Feel free to use, modify, and distribute!

---

## 🙋 Need Help?

See `SETUP_GMAIL.md` for detailed Gmail API setup instructions, especially if you're dealing with university account restrictions.
