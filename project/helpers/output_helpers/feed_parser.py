import helpers.cache_helpers.cacher as cacher
from datetime import datetime
import feedparser


def process_feed_metadata(feed, url):
    """
    Process feed metadata and return feed_data.
    Mainly to help convert RSS feeds to Atom feeds by saving / creating relevate metadata.
    Feed is not passed to feed_writer to avoid having to re-parse the feed.
    """

    feed_data = {
        "encoding": None,
        "title": None,
        "id": None,
        "updated": None,
        "author": None,
    }

    if feed.encoding:
        feed_data["encoding"] = feed.encoding
    else:
        # Default to utf-8
        feed_data["encoding"] = "utf-8"

    # Default title to "Latest Updates"
    feed_data["title"] = "Latest Updates"

    if feed.feed.get("id"):
        feed_data["id"] = feed.feed.get("id")
    else:
        # Default to URL
        feed_data["id"] = url

    # Default updated to current time
    feed_data["updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    if feed.feed.get("author_detail"):
        if feed.feed.get("author_detail").get("name"):
            feed_data["author"] = feed.feed.get("author_detail").get("name")
    else:
        # Default author to "Anonymous"
        feed_data["author"] = "Anonymous"

    return feed_data


def check_keywords(entry, match_keywords, exclude_keywords):
    """
    Check if entry matches a keyword and does not contain excluded keywords.
    """
    entry_string = str(entry).lower()
    if not match_keywords:
        return not any(
            keyword.lower() in entry_string for keyword in exclude_keywords
        )

    return any(
        keyword.lower() in entry_string for keyword in match_keywords
    ) and not any(
        keyword.lower() in entry_string for keyword in exclude_keywords
    )


def filter_feed_entries(
    feed, match_keywords, exclude_keywords, last_seen_id, caching
):
    """
    Filters feed entries based on provided keywords and stops processing once reaching last_seen_id
    """
    print("==== Filtering feed entries")
    entries = []
    for entry in feed.entries:
        if entry.get("id") and caching and entry["id"] == last_seen_id:
            print("==== Reached last seen entry. Skipping older entries")
            break
        if check_keywords(entry, match_keywords, exclude_keywords):
            entries.append(entry)
    return entries


def process_feed_url(config, url, caching=False):
    print(f"==== Fetching and parsing URL: {url}")
    slug_url = config["slug"] + url
    # Attempt to get cache data if caching is enabled
    cache_data = cacher.fetch_cache(slug_url) if caching else None
    last_seen_id, etag_value, last_modified_value = cache_data or (
        None,
        None,
        None,
    )

    if cache_data and caching:
        print("==== Cached entry found")
    elif not cache_data and caching:
        print("==== No cached entry found")

    try:
        print("==== Initiating feed fetch and parse")
        feed = feedparser.parse(
            url, etag=etag_value, modified=last_modified_value
        )

        # Check for unmodified feed
        if caching and hasattr(feed, "status") and feed.status == 304:
            print("==== Feed has not been modified since the last request")
            return {}, [], None

        elif caching and cache_data:
            print("==== Cannot determine if feed has been modified")

        # Check for feed type
        feed_type = "rss" if feed.version.startswith("rss") else "atom"

        match_keywords = config.get("match", [])
        exclude_keywords = config.get("exclude", [])

        config_filtered_entries = filter_feed_entries(
            feed, match_keywords, exclude_keywords, last_seen_id, caching
        )

        feed_data = process_feed_metadata(feed, url)

        if config_filtered_entries:
            print(
                f"==== Found {len(config_filtered_entries)} new entries for URL: {url}"
            )
        else:
            print(f"==== No new entries found for URL: {url}")

        # Update cache if there's a change and if caching is enabled
        if caching:
            if feed.entries[0].get("id"):
                new_last_seen_id = (
                    feed.entries[0]["id"] if feed.entries else None
                )
            else:
                new_last_seen_id = (
                    feed.entries[0]["link"] if feed.entries else None
                )

            new_etag = getattr(feed, "etag", None)
            new_last_modified = getattr(feed, "modified", None)
            cacher.update_cache(
                slug_url, new_last_seen_id, new_etag, new_last_modified
            )
            print(f"==== Updated cache for {url}")

        return config_filtered_entries, feed_data, feed_type

    except Exception as e:
        print(f"==== ERROR processing URL {url}: {e}")
        return {}, []
