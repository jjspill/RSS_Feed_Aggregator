import sqlite3
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILEPATH = os.path.join(BASE_DIR, "cache.db")

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS cache (
        slug_url TEXT PRIMARY KEY,
        last_seen_id TEXT,
        etag TEXT,
        last_modified TEXT
    );
"""


def setup_database():
    # Check if database file exists
    if not os.path.exists(DATABASE_FILEPATH):
        # Create database
        with sqlite3.connect(DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()

            # Table setup
            try:
                cursor.execute(CREATE_TABLE_SQL)
            except sqlite3.error as e:
                logging.error(f"Error: {e}")

            logging.info("Database set up complete")
    else:
        logging.info("Database exists")


def update_cache_etag_last(slug_url, etag=None, last_modified=None):
    # Connect to database
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()

        # Insert or update etag / last_ modified cache entry
        cursor.execute(
            """
            INSERT OR IGNORE INTO cache (slug_url)
            VALUES (?)
            """,
            (slug_url,),
        )

        cursor.execute(
            """
            UPDATE cache
            SET etag=?, last_modified=?
            WHERE slug_url=?
            """,
            (etag, last_modified, slug_url),
        )


def update_cache_id(slug_url, last_seen_id=None):
    # Connect to database
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()

        # Insert or update id cache entry
        cursor.execute(
            """
            INSERT OR IGNORE INTO cache (slug_url)
            VALUES (?)
            """,
            (slug_url,),
        )

        cursor.execute(
            """
            UPDATE cache
            SET last_seen_id=?
            WHERE slug_url=?
            """,
            (last_seen_id, slug_url),
        )


def fetch_cache(slug_url):
    # Connect to database
    with sqlite3.connect(DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()

        # Fetch cache entry
        cursor.execute(
            "SELECT last_seen_id, etag, last_modified FROM cache WHERE slug_url=?",
            (slug_url,),
        )
        result = cursor.fetchone()

    return None if result is None else result
