#!/usr/bin/env python3
"""
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

"""
from __future__ import annotations

import base64
import json
import os
import re
import sqlite3
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

app = typer.Typer(add_completion=False, no_args_is_help=False)
settings_app = typer.Typer(help="Manage filters that decide which jobs appear.")
console = Console()

# Gmail API scope: read-only
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

APP_DIR = Path(os.environ.get("JOBS_HOME", Path.home() / ".linkedin_jobs_cli"))
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "jobs.db"
CRED_PATH = APP_DIR / "credentials.json"  # copy your OAuth creds here
TOKEN_PATH = APP_DIR / "token.json"
SETTINGS_PATH = APP_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "include_titles": [],
    "exclude_titles": [],
    "include_companies": [],
    "exclude_companies": [],
    "include_locations": [],
    "exclude_locations": [],
    "max_age_days": 30,
}

LINKEDIN_JOB_RE = re.compile(r"https?://(www\.)?linkedin\.com/jobs/view/([^/?#]+)")
GENERIC_JOB_RE = re.compile(r"https?://[^\s\"]+")

# --------------------------- SETTINGS LAYER --------------------------------

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text())
        except json.JSONDecodeError:
            console.print("[red]Invalid settings.json, falling back to defaults.[/red]")
            data = {}
    else:
        data = {}

    merged = DEFAULT_SETTINGS.copy()
    for key, value in data.items():
        if key not in DEFAULT_SETTINGS:
            continue
        merged[key] = value

    # Normalize types
    for key in DEFAULT_SETTINGS:
        if key.endswith("titles") or key.endswith("companies") or key.endswith("locations"):
            merged[key] = [v for v in merged.get(key, []) if isinstance(v, str) and v.strip()]
        elif key == "max_age_days":
            try:
                merged[key] = int(merged.get(key, DEFAULT_SETTINGS[key]))
            except (TypeError, ValueError):
                merged[key] = DEFAULT_SETTINGS[key]
            merged[key] = max(0, merged[key])
    return merged


def save_settings(data: dict) -> None:
    filtered = {k: data.get(k, DEFAULT_SETTINGS[k]) for k in DEFAULT_SETTINGS}
    SETTINGS_PATH.write_text(json.dumps(filtered, indent=2, sort_keys=True))
    console.print(f"[green]Saved settings to {SETTINGS_PATH}[/green]")


# --------------------------- DB LAYER --------------------------------------

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            link TEXT UNIQUE,
            source TEXT,
            posted_at TEXT,
            created_at TEXT NOT NULL,
            seen_at TEXT,
            applied INTEGER DEFAULT 0,
            ignored INTEGER DEFAULT 0
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link);
        """
    )
    return conn


# --------------------------- GMAIL AUTH ------------------------------------

def gmail_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CRED_PATH.exists():
                console.print(
                    f"[red]Missing {CRED_PATH} — place your Gmail OAuth credentials there.[/red]"
                )
                raise typer.Exit(code=1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CRED_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# --------------------------- EMAIL PARSING ---------------------------------

LINKEDIN_SUBJECT_PATTERNS = (
    "LinkedIn Job Alert",
    "Jobs you may be interested in",
    "New jobs for",
)


def _is_job_alert_subject(subj: str) -> bool:
    s = subj.lower()
    return any(p.lower() in s for p in LINKEDIN_SUBJECT_PATTERNS)


def _extract_links_from_html(html: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html5lib")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "linkedin.com/jobs" in href:
            yield href
        elif any(d in href for d in ["lever.co", "greenhouse.io", "workable.com", "ashbyhq.com"]):
            yield href


def _guess_title_company_from_anchor(a_tag) -> tuple[Optional[str], Optional[str]]:
    text = a_tag.get_text(" ", strip=True)
    if " at " in text:
        t, c = text.split(" at ", 1)
        return t.strip() or None, c.strip() or None
    return text or None, None


def _guess_location(a_tag) -> Optional[str]:
    parent = a_tag.parent
    if not parent:
        return None
    for candidate in parent.find_all(string=True):
        if candidate and candidate.strip():
            text = candidate.strip()
            if any(sep in text for sep in [",", " - ", " · ", "•"]):
                if len(text.split()) <= 10 and not text.lower().startswith("apply"):
                    return text
    return None


def parse_email_payload_to_jobs(html: str, source: str = "LinkedIn") -> list[dict]:
    soup = BeautifulSoup(html, "html5lib")
    jobs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not (
            "linkedin.com/jobs" in href
            or any(d in href for d in ["lever.co", "greenhouse.io", "workable.com", "ashbyhq.com"])
        ):
            continue
        title, company = _guess_title_company_from_anchor(a)
        location = _guess_location(a)
        jobs.append(
            dict(
                title=title,
                company=company,
                location=location,
                link=href.split("?")[0],
                source=source,
                posted_at=None,
            )
        )
    return jobs


# --------------------------- FETCH FROM GMAIL -------------------------------

def fetch_from_gmail(max_results: int = 50):
    service = gmail_service()
    q = " OR ".join([f"subject:{p}" for p in LINKEDIN_SUBJECT_PATTERNS])
    results = (
        service.users()
        .messages()
        .list(userId="me", q=q, maxResults=max_results)
        .execute()
    )
    messages = results.get("messages", [])

    total_new = 0
    with db() as conn:
        for m in messages:
            full = service.users().messages().get(userId="me", id=m["id"]).execute()
            headers = {h["name"].lower(): h["value"] for h in full.get("payload", {}).get("headers", [])}
            subject = headers.get("subject", "(no subject)")
            if not _is_job_alert_subject(subject):
                continue

            payload = full.get("payload", {})
            html_payload = None

            parts = payload.get("parts", [])
            for p in parts:
                if p.get("mimeType") == "text/html":
                    html_payload = p.get("body", {}).get("data")
                    break
                if p.get("mimeType") == "multipart/alternative":
                    for pp in p.get("parts", []):
                        if pp.get("mimeType") == "text/html":
                            html_payload = pp.get("body", {}).get("data")
                            break
                if html_payload:
                    break
            if not html_payload and payload.get("mimeType") == "text/html":
                html_payload = payload.get("body", {}).get("data")
            if not html_payload:
                continue

            html = base64.urlsafe_b64decode(html_payload).decode("utf-8", errors="ignore")
            jobs = parse_email_payload_to_jobs(html, source="LinkedIn Email")

            for j in jobs:
                try:
                    conn.execute(
                        """
                        INSERT INTO jobs (title, company, location, link, source, posted_at, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            j.get("title"),
                            j.get("company"),
                            j.get("location"),
                            j.get("link"),
                            j.get("source"),
                            j.get("posted_at"),
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    total_new += 1
                except sqlite3.IntegrityError:
                    pass
    return total_new


# --------------------------- FILTERING -------------------------------------

def _normalize(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def job_matches_filters(row: sqlite3.Row, filters: dict, include_all: bool) -> bool:
    if include_all:
        return True

    title = _normalize(row["title"])
    company = _normalize(row["company"])
    location = _normalize(row["location"])

    include_titles = [_normalize(v) for v in filters["include_titles"]]
    if include_titles and not any(t in title for t in include_titles):
        return False

    exclude_titles = [_normalize(v) for v in filters["exclude_titles"]]
    if exclude_titles and any(t in title for t in exclude_titles):
        return False

    include_companies = [_normalize(v) for v in filters["include_companies"]]
    if include_companies and not any(c in company for c in include_companies):
        return False

    exclude_companies = [_normalize(v) for v in filters["exclude_companies"]]
    if exclude_companies and any(c in company for c in exclude_companies):
        return False

    include_locations = [_normalize(v) for v in filters["include_locations"]]
    if include_locations and not any(loc in location for loc in include_locations):
        return False

    exclude_locations = [_normalize(v) for v in filters["exclude_locations"]]
    if exclude_locations and any(loc in location for loc in exclude_locations):
        return False

    max_age_days = filters.get("max_age_days", 0)
    if max_age_days:
        created_at = row["created_at"]
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - created_dt > timedelta(days=max_age_days):
                    return False
            except ValueError:
                pass

    return True


# --------------------------- DISPLAY ---------------------------------------

def format_row(row: sqlite3.Row) -> str:
    title = row["title"] or "(Job)"
    company = row["company"] or "(Company)"
    loc = f" — {row['location']}" if row["location"] else ""
    return (
        f"• [bold]{title}[/bold] at [italic]{company}[/italic]{loc}\n"
        f"  [link={row['link']}]Open[/link]  · id={row['id']}"
    )


def list_jobs(show_all: bool = False, limit: int = 50, apply_filters: bool = True):
    filters = load_settings() if apply_filters else DEFAULT_SETTINGS
    include_all = show_all or not apply_filters

    sql = "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?"
    params = (limit,)
    if not show_all:
        sql = (
            "SELECT * FROM jobs WHERE applied=0 AND ignored=0 "
            "ORDER BY created_at DESC LIMIT ?"
        )
    with db() as conn:
        rows = conn.execute(sql, params).fetchall()

    if apply_filters:
        rows = [r for r in rows if job_matches_filters(r, filters, include_all)]
    else:
        rows = list(rows)

    if not rows:
        console.print("[green]No jobs to show.[/green]")
        return

    for r in rows:
        console.print(Markdown(format_row(r)))


# --------------------------- COMMAND HELPERS -------------------------------

def _update_job(job_id: int, **fields):
    timestamp = datetime.now(timezone.utc).isoformat()
    if "seen_at" not in fields:
        fields["seen_at"] = timestamp
    with db() as conn:
        cur = conn.execute("SELECT id FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not cur:
            console.print(f"[red]No job with id {job_id}[/red]")
            raise typer.Exit(1)
        assignments = ", ".join(f"{col}=?" for col in fields)
        conn.execute(
            f"UPDATE jobs SET {assignments} WHERE id=?",
            (*fields.values(), job_id),
        )
    console.print(f"[green]Updated job {job_id}.[/green]")


# --------------------------- COMMANDS --------------------------------------

@app.command()
def fetch(max_results: int = typer.Option(50, help="Maximum job alert emails to pull.")):
    """Fetch latest job alerts from Gmail and store them."""
    n = fetch_from_gmail(max_results=max_results)
    console.print(f"[cyan]{n}[/cyan] new job(s) saved.")


@app.command("jobs")
@app.command(name="list")
def _list(
    limit: int = typer.Option(50, help="Max jobs to display."),
    no_filter: bool = typer.Option(False, help="Do not apply saved filters."),
):
    """List new & unapplied jobs."""
    list_jobs(show_all=False, limit=limit, apply_filters=not no_filter)


@app.command()
def all(
    limit: int = typer.Option(100, help="Max jobs to display."),
    no_filter: bool = typer.Option(False, help="Disable filters even in all view."),
):
    """List all stored jobs (including applied/ignored)."""
    list_jobs(show_all=True, limit=limit, apply_filters=not no_filter)


@app.command()
def apply(job_id: int):
    """Mark a job as applied (hides it from default list)."""
    _update_job(job_id, applied=1)


@app.command()
def seen(job_id: int):
    """Mark a job as seen (but not applied)."""
    _update_job(job_id, seen_at=datetime.now(timezone.utc).isoformat())


@app.command()
def ignore(job_id: int):
    """Hide a job without marking as applied."""
    _update_job(job_id, ignored=1)


@app.command()
def open(job_id: int):
    """Open a job in your default browser."""
    with db() as conn:
        row = conn.execute("SELECT link FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        console.print(f"[red]No job with id {job_id}[/red]")
        raise typer.Exit(1)
    opened = webbrowser.open(row["link"])
    if not opened:
        console.print("[yellow]Browser did not report success; open the link manually.[/yellow]")


@app.command()
def reset(confirm: bool = typer.Option(False, help="Confirm database wipe")):
    """Wipe the local database (irreversible)."""
    if not confirm:
        console.print("[red]Refusing to reset without --confirm[/red]")
        raise typer.Exit(1)
    if DB_PATH.exists():
        DB_PATH.unlink()
    console.print("[yellow]Database removed.[/yellow]")


# --------------------------- SETTINGS COMMANDS -----------------------------

FIELD_HELP = {
    "include_titles": "Only show jobs whose title includes one of these terms.",
    "exclude_titles": "Hide jobs whose title includes any of these terms.",
    "include_companies": "Only show jobs from companies containing one of these terms.",
    "exclude_companies": "Hide jobs from companies containing any of these terms.",
    "include_locations": "Only show jobs whose location includes one of these terms.",
    "exclude_locations": "Hide jobs whose location includes any of these terms.",
    "max_age_days": "Hide jobs older than this many days (0 disables the check).",
}


def _ensure_list_field(field: str):
    if field not in DEFAULT_SETTINGS:
        console.print(f"[red]Unknown field '{field}'.[/red]")
        console.print("Allowed fields: " + ", ".join(DEFAULT_SETTINGS))
        raise typer.Exit(1)
    if field == "max_age_days":
        console.print("[red]Use `settings set max_age_days <number>` for that field.[/red]")
        raise typer.Exit(1)


@settings_app.command("show")
def settings_show():
    """Display current filter settings."""
    settings = load_settings()
    table = Table(title="Job Filters")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Hint", style="green")
    for field, hint in FIELD_HELP.items():
        value = settings[field]
        if isinstance(value, list):
            rendered = ", ".join(value) or "(empty)"
        else:
            rendered = str(value)
        table.add_row(field, rendered, hint)
    console.print(table)


@settings_app.command("add")
def settings_add(field: str, value: str = typer.Argument(..., help="Value to append.")):
    """Append a value to a list filter field."""
    _ensure_list_field(field)
    settings = load_settings()
    current = settings[field]
    if value in current:
        console.print("[yellow]Value already present.[/yellow]")
        return
    current.append(value)
    save_settings(settings)


@settings_app.command("remove")
def settings_remove(field: str, value: str = typer.Argument(..., help="Value to remove.")):
    """Remove a value from a list filter field."""
    _ensure_list_field(field)
    settings = load_settings()
    current = settings[field]
    try:
        current.remove(value)
    except ValueError:
        console.print("[yellow]Value not present; nothing to do.[/yellow]")
        return
    save_settings(settings)


@settings_app.command("set")
def settings_set(field: str, values: Optional[str] = typer.Argument(None)):
    """Set a field to the provided value(s)."""
    if field not in DEFAULT_SETTINGS:
        console.print(f"[red]Unknown field '{field}'.[/red]")
        console.print("Allowed fields: " + ", ".join(DEFAULT_SETTINGS))
        raise typer.Exit(1)

    settings = load_settings()
    if field == "max_age_days":
        if values is None:
            console.print("[red]Pass an integer value.[/red]")
            raise typer.Exit(1)
        try:
            days = int(values)
        except ValueError:
            console.print("[red]max_age_days must be an integer.[/red]")
            raise typer.Exit(1)
        settings[field] = max(0, days)
    else:
        if values is None:
            settings[field] = []
        else:
            items = [v.strip() for v in values.split(",") if v.strip()]
            settings[field] = items
    save_settings(settings)


@settings_app.command("reset")
def settings_reset(confirm: bool = typer.Option(False, help="Confirm reset to defaults.")):
    """Reset settings to defaults."""
    if not confirm:
        console.print("[red]Refusing to reset without --confirm[/red]")
        raise typer.Exit(1)
    save_settings(DEFAULT_SETTINGS.copy())


@settings_app.callback()
def settings_main():
    """Manage filter settings used to decide which jobs to show."""
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2, sort_keys=True))


app.add_typer(settings_app, name="settings")


# Default behavior: `python jobs_cli.py` -> list jobs
if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_jobs(show_all=False, limit=50, apply_filters=True)
    else:
        app()
