# How to Update & Restart Scripts

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
