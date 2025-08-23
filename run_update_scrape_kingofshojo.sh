#!/bin/bash
while true; do
    source /root/Manhua-Frontend-WebScraping/venv/bin/activate
    python /root/Manhua-Frontend-WebScraping/update_scrape_kingofshojo.py
    deactivate
    sleep 10800 # 3 hours in seconds
done
