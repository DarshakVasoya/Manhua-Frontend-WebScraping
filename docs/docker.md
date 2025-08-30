Here’s how these pieces fit together and what each one does:

1) update_scrape_kingofshojo.py (business logic)
- What: One full “scrape-and-update MongoDB” run.
- Reads config from env (via mongodb_connection.py and your own os.getenvs).
- Prints progress to stdout (Docker captures this).

2) run_every.py (lightweight scheduler)
- What: A simple loop runner inside the container.
- Reads:
  - UPDATE_INTERVAL_SECONDS (default 10800 = 3 hours)
  - RUN_CMD (default "python update_scrape_kingofshojo.py")
- Does:
  - Runs RUN_CMD once, waits for it to finish, logs exit code
  - Sleeps UPDATE_INTERVAL_SECONDS (in 1s ticks to react to stop)
  - Repeats until container stops

3) entrypoint.sh (task switch)
- What: Decides which script to run when the container starts.
- Reads: TASK env
  - TASK=updater -> exec python run_every.py
  - TASK=ratings -> exec python set_gemini_ratings.py
  - TASK=sitemap -> exec python generate_sitemap.py
  - TASK=cleanup_dupes -> exec python remove_duplicate_chapters.py
  - TASK=oneshot (default) -> prints a ready message
- “exec” makes the chosen process PID 1 (good for signals/logging).

4) docker-compose.yml (orchestrator)
- What: Defines services and environment for containers.
- In your file:
  - Service updater:
    - build: . (builds the image from Dockerfile)
    - env_file: .env (injects all your config)
    - environment: TASK=updater, RUN_CMD=python update_scrape_kingofshojo.py
    - restart: unless-stopped (keeps it running)
  - Service ratings:
    - Uses same image
    - environment: TASK=ratings (one-shot to set Gemini ratings)
    - restart: "no" (exits after finishing)

How it runs together (updater service)
- docker compose up -d updater
- Container starts -> entrypoint.sh runs -> sees TASK=updater -> runs run_every.py
- run_every.py runs RUN_CMD (python update_scrape_kingofshojo.py)
- update_scrape_kingofshojo.py does a single scrape/update cycle, exits
- run_every.py sleeps for UPDATE_INTERVAL_SECONDS, then repeats
- All print() output is visible via:
  - docker compose logs -f updater

How to change behavior
- Change interval: edit .env UPDATE_INTERVAL_SECONDS and restart updater
- Change command: set RUN_CMD in compose (or .env) to a different script
- Switch task: set TASK=ratings (or sitemap/cleanup_dupes) for that service

Typical commands
- Build with latest code: docker compose build
- Start/Restart updater: docker compose up -d updater
- Logs: docker compose logs -f updater
- Run ratings once: docker compose run --rm ratings
- Stop all: docker compose down

Run the same image on another machine (no rebuild)
- Build the image here (source machine):
  - docker compose build
  - docker image ls manhua-scraper:latest
- Save to a tar file and transfer:
  - docker save -o manhua-scraper.tar manhua-scraper:latest
  - scp manhua-scraper.tar user@other-host:~/
- On the target machine, load the image and run with runtime compose:
  - docker load -i manhua-scraper.tar
  - git clone https://github.com/DarshakVasoya/Manhua-Frontend-WebScraping.git
  - cd Manhua-Frontend-WebScraping
  - create `.env` with your MONGO_URI (and GEMINI_API_KEY if needed)
  - docker compose -f docker-compose.runtime.yml up -d updater
  - docker compose -f docker-compose.runtime.yml logs -f updater

Notes
- The runtime compose file uses only the prebuilt `manhua-scraper:latest` image; it won’t try to build.
- Keep .env off git; it’s read at runtime on the target machine.

Common pitfalls
- Don’t leave the old nohup/bash loop running on the host (stop it to avoid duplicates).
- After code changes, rebuild the image (docker compose build), then restart the service.
- Keep all config in .env; avoid hard-coded values in code.
- Use print or logging to stdout; don’t write log files inside the container.

This structure gives you:
- A clean separation of concerns (logic vs scheduler vs entrypoint vs orchestration)
- One image for multiple tasks (set by TASK)
- Easy config via environment variables
- Proper logging and lifecycle handling in Docker