import os
import re
import time
import json
from datetime import datetime
from typing import Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import google.generativeai as genai
from mongodb_connection import get_mongo_client

# Configuration via environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
BATCH_LIMIT = int(os.getenv("RATING_BATCH_LIMIT", "0"))  # 0 = no limit
SLEEP_SECONDS = float(os.getenv("RATING_SLEEP_SECONDS", "0.0"))  # default faster
MAX_RETRIES = int(os.getenv("RATING_MAX_RETRIES", "3"))
OVERWRITE = os.getenv("RATING_OVERWRITE", "true").lower() in {"1", "true", "yes", "y"}
COLLECTION_NAME = os.getenv("RATING_COLLECTION", "manhwa")
CONCURRENCY = int(os.getenv("RATING_CONCURRENCY", "8"))  # increase for more speed

if not GEMINI_API_KEY:
    raise SystemExit("GEMINI_API_KEY environment variable is required.")


def _configure_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)


def _build_prompt(doc: dict) -> str:
    name = doc.get("name") or "Unknown"
    description = doc.get("description") or ""
    genres = doc.get("genres") or []
    views = doc.get("views") or ""
    last_chapter = doc.get("last_chapter") or ""
    released = doc.get("released") or ""
    status = doc.get("status") or ""

    prompt = f"""
You are a strict manhwa rating assistant. Calibrate your 1.0-10.0 scale so that:
- Solo Leveling (as a modern, highly popular, high-quality benchmark) would be 9.9.
- 9.5-10.0: exceptional, genre-defining, mass appeal and execution.
- 8.5-9.4: outstanding, highly recommended.
- 7.0-8.4: good/solid, recommended.
- 5.0-6.9: average/mixed.
- 3.0-4.9: weak.
- 1.0-2.9: very poor.

Rate strictly as a single float 1.0-10.0 (decimals allowed) using only the info provided (don't assume missing facts). Consider: clarity/originality of premise, likely character depth, narrative potential, genre fit, and popularity hints (views/trends).

Return only this JSON object (no backticks, no extra text):
{{"rating": <float 1.0-10.0>, "reason": "<short reason>"}}

Manga Name: {name}
Genres: {", ".join(genres) if genres else "N/A"}
Released: {released}
Last Chapter: {last_chapter}
Views: {views}
Description: {description}
"""
    return prompt


def _parse_rating(text: str) -> Tuple[Optional[float], Optional[str]]:
    """Try to parse JSON, else fallback to regex for a float 1-10."""
    try:
        data = json.loads(text)
        rating = float(data.get("rating"))
        reason = data.get("reason")
        if 1.0 <= rating <= 10.0:
            return rating, reason
    except Exception:
        pass

    # Fallback: find first float in range 1-10
    m = re.search(r"\b(10(?:\.0+)?|[1-9](?:\.[0-9]+)?)\b", text)
    if m:
        try:
            rating = float(m.group(1))
            if 1.0 <= rating <= 10.0:
                return rating, None
        except Exception:
            pass
    return None, None


def _rate_with_retries(model, prompt: str) -> Tuple[Optional[float], Optional[str]]:
    delay = 1.0
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = model.generate_content(prompt)
            text = resp.text or ""
            rating, reason = _parse_rating(text)
            if rating is not None:
                return rating, reason
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"Gemini error after {attempt} attempts: {e}")
                return None, None
        time.sleep(delay)
        delay = min(delay * 2, 10)
    return None, None


_thread_local = threading.local()


def _thread_model():
    if not hasattr(_thread_local, "model"):
        _thread_local.model = _configure_gemini()
    return _thread_local.model


def _process_one(doc: dict, collection) -> Tuple[bool, str]:
    # Skip if not overwriting and rating exists
    if not OVERWRITE and doc.get("rating") is not None:
        return False, doc.get("name") or doc.get("url") or str(doc.get("_id"))

    model = _thread_model()
    prompt = _build_prompt(doc)
    rating, reason = _rate_with_retries(model, prompt)
    if SLEEP_SECONDS > 0:
        time.sleep(SLEEP_SECONDS)

    if rating is None:
        return False, doc.get("name") or doc.get("url") or str(doc.get("_id"))

    rating = max(1.0, min(10.0, float(rating)))
    rating = round(rating, 1)

    update = {
        "rating": rating,
        "rating_source": "gemini",
        "rating_reason": reason,
        "rating_updated_at": datetime.utcnow(),
    }
    collection.update_one({"_id": doc["_id"]}, {"$set": update})
    return True, f"{doc.get('name') or doc.get('url')}: {rating}"


def main():
    client = get_mongo_client()
    db = client.admin
    collection = db[COLLECTION_NAME]

    query = {} if OVERWRITE else {"rating": {"$exists": False}}
    cursor = collection.find(query, no_cursor_timeout=True)

    # Load docs to submit (respect batch limit)
    docs: List[dict] = []
    try:
        for doc in cursor:
            docs.append(doc)
            if BATCH_LIMIT and len(docs) >= BATCH_LIMIT:
                break
    finally:
        cursor.close()

    if not docs:
        client.close()
        print("No documents to process.")
        return

    processed = 0
    updated = 0

    with ThreadPoolExecutor(max_workers=max(1, CONCURRENCY)) as executor:
        futures = [executor.submit(_process_one, d, collection) for d in docs]
        for fut in as_completed(futures):
            ok, msg = fut.result()
            processed += 1
            if ok:
                updated += 1
                print(f"Updated: {msg}")
            else:
                print(f"Skipped/Failed: {msg}")

    client.close()
    print(f"Done. Processed={processed}, Updated={updated}")


if __name__ == "__main__":
    main()
