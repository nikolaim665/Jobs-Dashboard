<<<<<<< HEAD
# Jobs-Dashboard

A terminal CLI for tracking LinkedIn job offers via email! Fetch jobs from Gmail alerts, filter by your preferences, and track which ones you've applied to.

## Features

- **Gmail Integration** - Fetch LinkedIn job alerts from your personal Gmail
- **Smart Filtering** - Filter by title, company, location, and job age
- **Application Tracking** - Mark jobs as applied, seen, or ignored
- **Clean Terminal UI** - Beautiful output powered by Rich
- **University Account Workaround** - Use personal Gmail when university blocks API access

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gmail API (Use Personal Gmail!)

**Important:** If your university Gmail blocks API project creation, use your personal Gmail account instead.

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth Client ID (Desktop app)
5. Download `credentials.json`
6. Place it in `~/.linkedin_jobs_cli/credentials.json`

### 3. Set Up LinkedIn Job Alerts

1. Go to LinkedIn Jobs and search with your preferred filters
2. Click "Create job alert" or the bell icon
3. Set frequency to "Daily" (recommended)
4. **Make sure alerts go to your personal Gmail** (not university email)

### 4. First Run

```bash
python jobs_cli.py fetch
```

Your browser will open asking you to authorize Gmail access. **Choose your personal Gmail account** (not university).

### 5. View Jobs

```bash
python jobs_cli.py
```

## Usage

```bash
# List new jobs (default command)
python jobs_cli.py

# Fetch new jobs from Gmail (default source)
python jobs_cli.py fetch

# Fetch with more results
python jobs_cli.py fetch --max-results 100

# Mark a job as applied
python jobs_cli.py apply 5

# Open a job in browser
python jobs_cli.py open 5

# View all jobs (including applied)
python jobs_cli.py all

# View current filter settings
python jobs_cli.py settings show

# Add filters
python jobs_cli.py settings add include_titles "senior"
python jobs_cli.py settings add include_locations "remote"
python jobs_cli.py settings add exclude_companies "Meta"

# Set max age (hide jobs older than N days)
python jobs_cli.py settings set max_age_days 14
```

## Alternative: RSS Feeds

**Note:** LinkedIn's native RSS has been deprecated, but you can use RSS feeds from other job boards:

```bash
# Add RemoteOK RSS feed
python jobs_cli.py settings add rss_feeds "https://remoteok.com/remote-dev-jobs.rss"

# Fetch from RSS instead of Gmail
python jobs_cli.py fetch --source rss

# Or fetch from both
python jobs_cli.py fetch --source both
```

## Advanced

### Make it a Shell Command

```bash
# Make executable
chmod +x jobs_cli.py

# Option A: Symlink to PATH
ln -s "$(pwd)/jobs_cli.py" ~/.local/bin/jobs

# Option B: Shell alias
echo 'alias jobs="python /full/path/to/jobs_cli.py"' >> ~/.bashrc
```

Now just type `jobs` to see your list!
=======
# 💼 LinkedIn Jobs CLI  
**Type `jobs` to list NEW & UNAPPLIED roles — right in your terminal.**

---

### ⚡️ Overview  
**LinkedIn Jobs CLI** helps you manage your job search without brittle scraping.  
Instead of violating LinkedIn’s ToS or relying on unstable HTML parsing, this CLI securely reads your **LinkedIn Job Alert emails** via the **Gmail API**, extracts job data, and stores it locally.  

You’ll get a clean, bullet-point list of new roles you haven’t marked as applied — all from the command line.

---

### 🧠 Features  
- 🔍 **List new, unseen, and unapplied jobs** directly in your terminal  
- 📬 **Fetch** new job alerts automatically from Gmail  
- 🗂 **Mark jobs** as applied, seen, or ignored  
- 🌐 **Open** job postings in your browser  
- ⚙️ **Manage filters** to control which jobs are displayed  
- 🧹 **Reset** your local database anytime  

---

### 💻 Commands  

| Command | Description |
|----------|-------------|
| `jobs` | List new + unapplied jobs *(default command)* |
| `fetch` | Pull latest job alerts from Gmail and store them locally |
| `apply <id>` | Mark a job as applied (hides it from the default list) |
| `seen <id>` | Mark a job as seen (but not applied) |
| `ignore <id>` | Hide a job without marking as applied |
| `all` | List everything (including applied/ignored) |
| `open <id>` | Open the job posting in your browser |
| `reset` | Wipe local database *(use with caution)* |
| `settings ...` | Manage filters for displayed jobs |

---

### ⚙️ Setup (One-Time)

#### 1️⃣ Install dependencies
It’s recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
>>>>>>> e1064a3e209a2482bba57699f0e394180f7898d5
