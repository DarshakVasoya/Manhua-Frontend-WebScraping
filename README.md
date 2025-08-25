
# Manhua-Frontend-WebScraping: Full Project Documentation

---

## Project Overview
This project is designed to scrape manga data from kingofshojo.com, store and update it in MongoDB, and provide tools for data management, deduplication, and periodic background execution. It also includes scripts for generating sitemaps for SEO and indexing purposes.

---

## Table of Contents
1. [Setup & Installation](#setup--installation)
2. [MongoDB Connection](#mongodb-connection)
3. [Main Scripts](#main-scripts)
    - Scraping & Updating
    - Deduplication
    - Sitemap Generation
    - Background Execution
4. [How to Update & Restart Scripts](#how-to-update--restart-scripts)
5. [Linux Commands Reference](#linux-commands-reference)
6. [Troubleshooting](#troubleshooting)
7. [Customization](#customization)
8. [Chat History & Workflow](#chat-history--workflow)
9. [Contact](#contact)

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <repo-url>
cd Manhua-Frontend-WebScraping
```

### 2. Python Environment
Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## MongoDB Connection
- All scripts use `mongodb_connection.py` for authenticated access.
- Edit this file with your credentials if needed.

---

## Main Scripts

### Scraping & Updating
- **update_scrape_kingofshojo.py**
  - Scrapes manga and chapter data, updates MongoDB.
  - Handles duplicate chapters, updates only when new chapters are found.
  - Usage:
    ```bash
    source venv/bin/activate
    python update_scrape_kingofshojo.py
    ```

### Deduplication
- **remove_duplicate_chapters.py**
  - Removes duplicate chapters (by `chapternum`) in MongoDB.
  - Usage:
    ```bash
    source venv/bin/activate
    python remove_duplicate_chapters.py
    ```

### Sitemap Generation
- **sitemap_generator.py** (example name)
  - Generates `sitemap.xml` and `sitemap-index.xml` for SEO.
  - Usage:
    ```bash
    python sitemap_generator.py
    ```
  - Customizable for your domain and structure.

### Background Execution
- **run_update_scrape_kingofshojo.sh**
  - Runs the update script every 3 hours in a loop.
  - Usage:
    ```bash
    nohup bash run_update_scrape_kingofshojo.sh > update_scrape.log 2>&1 &
    ```
  - Output is logged to `update_scrape.log`.

---

## How to Update & Restart Scripts
1. Edit and save your changes to any Python script (e.g., `update_scrape_kingofshojo.py`).
2. Stop the running background process:
   ```bash
   ps aux | grep run_update_scrape_kingofshojo.sh
   kill <PID>
   ```
3. Restart the background job:
   ```bash
   nohup bash run_update_scrape_kingofshojo.sh > update_scrape.log 2>&1 &
   ```

---

## Linux Commands Reference
- `ps aux | grep scriptname` — Find running processes.
- `kill <PID>` — Stop a process.
- `pkill -f scriptname` — Kill all matching processes.
- `tail -f update_scrape.log` — View live log output.
- `source venv/bin/activate` — Activate Python environment.
- `deactivate` — Deactivate environment.
- `chmod +x script.sh` — Make a shell script executable.
- `crontab -e` — Edit cron jobs for scheduling.

---

## Troubleshooting
- **Authentication Error:** Ensure you use `get_mongo_client()` for MongoDB access.
- **Python Not Found:** Activate your virtual environment before running scripts.
- **Script Not Updating:** Stop and restart the background process after making changes.
- **Duplicate Chapters:** Use `remove_duplicate_chapters.py` to clean up your data.

---

## Customization
- Change the sleep interval in `run_update_scrape_kingofshojo.sh` to adjust how often the script runs.
- Edit MongoDB collection names in scripts as needed.
- Update domain and static pages in sitemap generator as required.

---

## Chat History & Workflow
This project was developed interactively with GitHub Copilot, including:
- Environment setup and dependency troubleshooting.
- Background execution and resource monitoring.
- MongoDB update/creation logic and preview scripts.
- Site structure adaptation and scraping logic refactoring.
- Deduplication and data cleaning scripts.
- Periodic execution via shell script and nohup.
- Sitemap generation for SEO.
- Documentation and workflow automation.

**Example Chat Highlights:**
- How to run scripts in the background and monitor them.
- How to update scripts and restart background jobs.
- How to deduplicate chapters in MongoDB.
- How to generate sitemaps for Google indexing.
- How to use Linux commands for process management.

---

## Contact
For issues or questions, contact the project maintainer or refer to this documentation for guidance.
