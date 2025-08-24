# Manhua-Frontend-WebScraping Documentation

## Overview
This project scrapes manga data from kingofshojo.com and stores/updates it in MongoDB. It includes scripts for scraping, updating, deduplication, and background scheduling.

---

## Setup

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

### 4. MongoDB Connection
Edit `mongodb_connection.py` with your MongoDB credentials if needed. The project uses `get_mongo_client()` for authenticated access.

---

## Main Scripts

### Scraping and Updating
- **update_scrape_kingofshojo.py**
  - Scrapes manga and chapter data, updates MongoDB.
  - Usage:
    ```bash
    source venv/bin/activate
    python update_scrape_kingofshojo.py
    ```

### Remove Duplicate Chapters
- **remove_duplicate_chapters.py**
  - Removes duplicate chapters (by `chapternum`) in MongoDB.
  - Usage:
    ```bash
    source venv/bin/activate
    python remove_duplicate_chapters.py
    ```

### Background Scheduling
- **run_update_scrape_kingofshojo.sh**
  - Runs the update script every 3 hours in a loop.
  - Usage:
    ```bash
    nohup bash run_update_scrape_kingofshojo.sh > update_scrape.log 2>&1 &
    ```
  - Output is logged to `update_scrape.log`.

---

## Updating the Script
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

## Useful Linux Commands
- `ps aux | grep scriptname` — Find running processes.
- `kill <PID>` — Stop a process.
- `pkill -f scriptname` — Kill all matching processes.
- `tail -f update_scrape.log` — View live log output.
- `source venv/bin/activate` — Activate Python environment.
- `deactivate` — Deactivate environment.

---

## Troubleshooting
- **Authentication Error:** Ensure you use `get_mongo_client()` for MongoDB access.
- **Python Not Found:** Activate your virtual environment before running scripts.
- **Script Not Updating:** Stop and restart the background process after making changes.

---

## Customization
- Change the sleep interval in `run_update_scrape_kingofshojo.sh` to adjust how often the script runs.
- Edit MongoDB collection names in scripts as needed.

---

## Contact
For issues or questions, contact the project maintainer.
