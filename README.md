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
