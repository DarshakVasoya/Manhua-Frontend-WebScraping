#!/usr/bin/env bash
set -euo pipefail

TASK="${TASK:-oneshot}"
echo "[entrypoint] TASK=${TASK}"

case "$TASK" in
  updater)
    # Periodic updater loop (uses run_every.py from step 3)
    exec python run_every.py
    ;;
  ratings)
    # Gemini ratings (uses env like GEMINI_API_KEY, etc.)
    exec python set_gemini_ratings.py
    ;;

  oneshot)
    # Default no-op for container sanity checks
    exec python -c "print('Container ready. Set TASK to updater/ratings .')"
    ;;
  *)
    echo "[entrypoint] Unknown TASK=$TASK"
    exit 1
    ;;
esac