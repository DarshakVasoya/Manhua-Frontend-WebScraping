# Main Scripts

## Scraping & Updating
- **update_scrape_kingofshojo.py**
  - Scrapes manga and chapter data, updates MongoDB.
  - Handles duplicate chapters, updates only when new chapters are found.
  - Usage:
    ```bash
    source venv/bin/activate
    python update_scrape_kingofshojo.py
    ```

## Deduplication
- **remove_duplicate_chapters.py**
  - Removes duplicate chapters (by `chapternum`) in MongoDB.
  - Usage:
    ```bash
    source venv/bin/activate
    python remove_duplicate_chapters.py
    ```

## Sitemap Generation
- **sitemap_generator.py** (example name)
  - Generates `sitemap.xml` and `sitemap-index.xml` for SEO.
  - Usage:
    ```bash
    python sitemap_generator.py
    ```
  - Customizable for your domain and structure.

## Background Execution
- **run_update_scrape_kingofshojo.sh**
  - Runs the update script every 3 hours in a loop.
  - Usage:
    ```bash
    nohup bash run_update_scrape_kingofshojo.sh > update_scrape.log 2>&1 &
    ```
  - Output is logged to `update_scrape.log`.
