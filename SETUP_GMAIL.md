# Gmail Setup Guide for Jobs-Dashboard

This guide helps you set up Gmail API access for the Jobs CLI, especially if your university Gmail account blocks API project creation.

## Problem: University Gmail Restrictions

Many university Google Workspace accounts don't allow students to create API projects in Google Cloud Console. If you see errors like "You don't have permission to create projects", follow this guide.

## Solution: Use Your Personal Gmail

You'll use your **personal Gmail account** to create the OAuth credentials, but LinkedIn job alerts can still go to either email (we recommend personal).

## Step-by-Step Setup

### 1. Create Google Cloud Project (Personal Gmail)

1. Sign in to [Google Cloud Console](https://console.cloud.google.com/) with your **personal Gmail**
2. Click "Select a project" → "New Project"
3. Name it something like "LinkedIn Jobs CLI"
4. Click "Create"

### 2. Enable Gmail API

1. Go to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for "Gmail API"
3. Click "Enable"

### 3. Create OAuth Credentials

1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: "LinkedIn Jobs CLI"
   - User support email: Your personal Gmail
   - Developer contact: Your personal Gmail
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add your email as a test user
   - Click "Save and Continue"
4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: "Jobs CLI"
   - Click "Create"
5. Click "Download JSON"
6. Rename the downloaded file to `credentials.json`

### 4. Install credentials.json

```bash
# Create the directory if it doesn't exist
mkdir -p ~/.linkedin_jobs_cli

# Move credentials.json there
mv ~/Downloads/credentials.json ~/.linkedin_jobs_cli/credentials.json
```

### 5. Set Up LinkedIn Job Alerts

1. Go to [LinkedIn Jobs](https://www.linkedin.com/jobs/)
2. Search for jobs you want (e.g., "Software Engineer", "Python Developer")
3. Click "Create job alert" or the bell icon
4. Configure:
   - Frequency: **Daily** (recommended)
   - Email: Your **personal Gmail** (the one with API access)
5. Click "Create"

### 6. First Run - Authorization

```bash
cd /path/to/Jobs-Dashboard
python jobs_cli.py fetch
```

What happens:
1. Browser opens automatically
2. Google asks you to sign in → **Choose your personal Gmail**
3. Google shows "LinkedIn Jobs CLI wants to access your Gmail" → Click "Allow"
4. Browser shows "The authentication flow has completed"
5. CLI starts fetching jobs!

A `token.json` file is created in `~/.linkedin_jobs_cli/` for future runs (no browser needed after this).

### 7. Verify It's Working

```bash
# View fetched jobs
python jobs_cli.py

# If you see jobs, you're done! 🎉
```

## Troubleshooting

### "credentials.json not found"
- Make sure the file is at `~/.linkedin_jobs_cli/credentials.json`
- Check the path: `ls -la ~/.linkedin_jobs_cli/`

### "No jobs found"
- Wait for LinkedIn to send you job alerts (can take a day)
- Verify alerts are going to your personal Gmail
- Check Gmail for "LinkedIn Job Alert" emails

### "Access blocked: This app's request is invalid"
- Your OAuth consent screen might not be configured correctly
- Make sure you added your email as a test user
- User Type should be "External"

### "Token has been expired or revoked"
- Delete the token: `rm ~/.linkedin_jobs_cli/token.json`
- Run `python jobs_cli.py fetch` again to re-authorize

## Privacy & Security

- **Read-only access**: The CLI can only READ your Gmail, not send or delete emails
- **Local storage**: All data stored locally in `~/.linkedin_jobs_cli/`
- **Your control**: You can revoke access anytime at https://myaccount.google.com/permissions

## Next Steps

Once setup is complete:
- Set up filters: `python jobs_cli.py settings add include_titles "senior"`
- Mark jobs as applied: `python jobs_cli.py apply <id>`
- See the main README.md for all commands
