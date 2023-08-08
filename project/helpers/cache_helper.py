import os
import json
import hashlib

CACHE_DIR = "cache"


def stable_hash(url):
    """Generate a stable hash based on slug and URL of the RSS entry."""
    hash_input = f"{url}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def get_last_seen_id(slug, url):
    """
    Fetch the last seen ID for a given slug and URL combination from the cache.
    """
    cache_key = f"{slug}_{stable_hash(url)}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
            return data.get("last_seen_id")

    return None


def update_last_seen_id(slug, url, entry_id):
    """
    Update the last seen ID for a given slug and URL combination in the cache.
    """
    cache_key = f"{slug}_{stable_hash(url)}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    with open(cache_file, "w") as f:
        json.dump({"last_seen_id": entry_id}, f)
