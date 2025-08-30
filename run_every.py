import os, time, subprocess, sys, signal

INTERVAL_SECONDS = int(os.getenv("UPDATE_INTERVAL_SECONDS", "10800"))  # default 3h
CMD = os.getenv("RUN_CMD", "python update_scrape_kingofshojo.py")
STOP = False

def _handle(_signum, _frame):
    global STOP
    STOP = True
    print("[runner] stop received", flush=True)

signal.signal(signal.SIGTERM, _handle)
signal.signal(signal.SIGINT, _handle)

def main():
    while not STOP:
        print(f"[runner] executing: {CMD}", flush=True)
        code = subprocess.call(CMD, shell=True)
        print(f"[runner] exit={code}, sleeping {INTERVAL_SECONDS}s", flush=True)
        for _ in range(INTERVAL_SECONDS):
            if STOP:
                break
            time.sleep(1)
    print("[runner] stopped", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())