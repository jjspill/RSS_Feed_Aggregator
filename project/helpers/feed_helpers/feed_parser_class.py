import helpers.cache_helpers.cacher as cacher
from datetime import datetime
import feedparser


class FeedProcessor:
    def __init__(self, args):
        self.args = args
        (
            self.response_status,
            self.config,
            self.url,
            self.feed_text,
            self.caching,
            self.cache_data,
        ) = args

    @staticmethod
    def process_feed_wrapper(args):
        """
        Wrapper for process_feed to allow for multiprocessing.
        """

        processor = FeedProcessor(args)
        return processor.process_feed()

    def process_feed_metadata(self, feed):
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
            feed_data["encoding"] = "utf-8"

        feed_data["title"] = "Latest Updates"

        if feed.feed.get("id"):
            feed_data["id"] = feed.feed.get("id")
        else:
            feed_data["id"] = self.url

        feed_data["updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if feed.feed.get("author_detail"):
            if feed.feed.get("author_detail").get("name"):
                feed_data["author"] = feed.feed.get("author_detail").get(
                    "name"
                )
        else:
            feed_data["author"] = "Anonymous"

        return feed_data

    @staticmethod
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

    def filter_feed_entries(self, feed):
        """
        Filters feed entries based on provided keywords and stops processing once reaching last_seen_id
        """

        entries = []
        match_keywords = self.config.get("match", [])
        exclude_keywords = self.config.get("exclude", [])

        last_id = self.cache_data[0] if self.cache_data else None

        for entry in feed.entries:
            if entry.get("id") and self.caching and entry["id"] == last_id:
                break
            if FeedProcessor.check_keywords(
                entry, match_keywords, exclude_keywords
            ):
                entries.append(entry)
        return entries

    def process_feed(self):
        """
        Parse and process a fetched URL.
        """

        try:
            slug_url = self.config["slug"] + self.url

            feed = feedparser.parse(self.feed_text)

            feed_type = "rss" if feed.version.startswith("rss") else "atom"

            config_filtered_entries = self.filter_feed_entries(feed)

            feed_data = self.process_feed_metadata(feed)

            if self.caching:
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

            result_dict = {
                "filtered_entries": config_filtered_entries,
                "feed_data": feed_data,
                "feed_type": feed_type,
            }

            return (self.config, result_dict)

        except Exception as e:
            print(f"Error: {e}")
            print("")
            return (self.config, None)
