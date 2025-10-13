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
