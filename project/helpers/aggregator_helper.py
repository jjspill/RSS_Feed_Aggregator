import helpers.cache.caching_helper as cacher
import xml.etree.ElementTree as ET
from dateutil.parser import parse
from datetime import datetime, timezone
import xml.dom.minidom
import feedparser
import yaml
import os
import re


def is_valid_atom_id(atom_id):
    # URI and URN format
    uri_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://.*$")
    urn_pattern = re.compile(r"^urn:[a-zA-Z0-9][a-zA-Z0-9-]{0,31}:.*$")

    return (
        uri_pattern.match(atom_id) is not None
        or urn_pattern.match(atom_id) is not None
    )


def is_atom_time(date_str):
    try:
        # Parse the string in RFC-3339 format
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def custom_timezone_parser(time_string):
    """Attempts to parse the time_string with timezone info."""
    tzinfo_map = {"UT": "UTC"}
    try:
        return parse(time_string)
    except ValueError:
        return parse(time_string, tzinfos=tzinfo_map)


def create_xml(entries, feed_data):
    """
    Create XML string from feed entries.
    """
    root = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")

    ET.SubElement(root, "title").text = feed_data["title"]
    ET.SubElement(root, "id").text = feed_data["id"]
    ET.SubElement(root, "updated").text = feed_data["updated"]

    for entry in entries:
        entry_element = ET.SubElement(root, "entry")

        # Handle Title
        if entry.get("title"):
            ET.SubElement(entry_element, "title").text = entry["title"]
        else:
            ET.SubElement(entry_element, "title").text = "No title"

        # Handle published
        if entry.get("published"):
            if is_atom_time(entry["published"]):
                ET.SubElement(entry_element, "published").text = entry[
                    "published"
                ]
            else:
                parsed_date = custom_timezone_parser(entry["published"])
                ET.SubElement(
                    entry_element, "published"
                ).text = parsed_date.replace(tzinfo=timezone.utc).isoformat()
        else:
            ET.SubElement(entry_element, "published").text = feed_data[
                "updated"
            ]

        # Handle updated
        if entry.get("updated"):
            if is_atom_time(entry["updated"]):
                ET.SubElement(entry_element, "updated").text = entry["updated"]
            else:
                parsed_date = custom_timezone_parser(entry["updated"])
                ET.SubElement(
                    entry_element, "updated"
                ).text = parsed_date.replace(tzinfo=timezone.utc).isoformat()
        else:
            ET.SubElement(entry_element, "updated").text = feed_data["updated"]

        # Handle ID
        if entry.get("id") and is_valid_atom_id(entry["id"]):
            ET.SubElement(entry_element, "id").text = entry["id"]
        else:
            ET.SubElement(entry_element, "id").text = f"urn:tag:{entry['id']}"

        # Handle summary
        summary_data = entry.get("summary")
        if summary_data:
            type_mapping = {
                "text/plain": "text",
                "text/html": "html",
                "application/xhtml+xml": "xhtml",
            }
            summary_type = type_mapping.get(
                entry.get("summary_detail", {}).get("type"), "text"
            )  # default to text

            ET.SubElement(
                entry_element, "summary", type=summary_type
            ).text = summary_data

        # Handle enclosures
        for enclosure in entry.get("enclosures", []):
            link_data = {
                "rel": "enclosure",
                "type": enclosure.get(
                    "type", "text/html"
                ),  # Default to "text/html"
                "length": str(
                    enclosure.get("length", "")
                ),  # Default to empty string
                "href": enclosure["href"],
            }
            ET.SubElement(entry_element, "link", **link_data)

        # Handle tags
        for tag in entry.get("tags", []):
            attrib_data = {
                "scheme": tag.get("scheme", ""),  # Default to empty
                "label": tag.get("label", ""),  # Default to empty
                "term": tag.get("term", ""),  # Default to empty
            }
            ET.SubElement(entry_element, "category", **attrib_data)

        # Handle link
        link_data = entry.get("link")
        if link_data:
            link_attributes = {
                "rel": entry.get("rel", "alternate"),  # default to alternate
                "type": entry.get(
                    "type", "text/html"
                ),  # default to "text/html"
                "href": link_data,
            }
            ET.SubElement(entry_element, "link", **link_attributes)
        else:
            ET.SubElement(
                entry_element,
                "link",
                rel="alternate",
                type="text/html",
                href="feed_data['id']",
            )

        # Handle author
        author = ET.SubElement(entry_element, "author")
        if feed_data["author"]:
            ET.SubElement(author, "name").text = feed_data["author"]
        else:
            ET.SubElement(author, "name").text = "Anonymous"

    xml_string = ET.tostring(
        root, encoding=feed_data["encoding"], method="xml"
    )
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ", encoding=feed_data["encoding"]).decode(
        feed_data["encoding"]
    )


def output_feeds(slug, entries, feed_data, caching):
    """
    Output XML feeds to files.
    """
    output_file = f"rss-feeds/{slug}-feed.xml"
    xml = create_xml(entries, feed_data)

    if not caching:
        with open(output_file, "w") as f:
            f.write(xml)
        return

    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            with open("newfile.txt", "w") as f2:
                f2.write(xml)
                f2.write(f.read())
        os.remove(output_file)
    else:
        with open("newfile.txt", "w") as f2:
            f2.write(xml)

    os.rename("newfile.txt", output_file)


def check_keywords(entry, match_keywords, exclude_keywords):
    """
    Check if entry matches a keyword and does not contain excluded keywords.
    """
    entry_string = str(entry).lower()
    return any(
        keyword.lower() in entry_string for keyword in match_keywords
    ) and not any(
        keyword.lower() in entry_string for keyword in exclude_keywords
    )


def filter_feed_entries(feed, match_keywords, exclude_keywords, last_seen_id):
    """
    Filters feed entries based on provided keywords and stops processing once reaching last_seen_id
    """
    print("==== Filtering feed entries")
    entries = []
    for entry in feed.entries:
        if entry["id"] == last_seen_id:
            print("==== Reached last seen entry. Skipping older entries")
            break
        if check_keywords(entry, match_keywords, exclude_keywords):
            entries.append(entry)
    return entries


def process_feed_url(config, url, caching=True):
    print(f"==== Fetching and parsing URL: {url}")

    # Attempt to get cache data once if caching is enabled
    cache_data = cacher.fetch_cache(url) if caching else None
    last_seen_id, etag_value, last_modified_value = cache_data or (
        None,
        None,
        None,
    )

    if cache_data:
        print("==== Cached entry found")
    else:
        print("==== No cached entry found")

    try:
        print("==== Initiating feed fetch and parse")
        feed = feedparser.parse(
            url, etag=etag_value, modified=last_modified_value
        )
        print(f"==== Cached etag: {etag_value}")
        print(f"==== Cached last modified: {last_modified_value}")

        # Check for unmodified feed
        if hasattr(feed, "status") and feed.status == 304:
            print("==== Feed has not been modified since the last request")
            return {}, []

        else:
            print("==== Feed has been modified since the last request")

        match_keywords = config["match"]
        exclude_keywords = config["exclude"]
        config_filtered_entries = filter_feed_entries(
            feed, match_keywords, exclude_keywords, last_seen_id
        )

        # Data for return RSS feed
        # only acquire if feed has not been parsed before
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
            feed_data["id"] = url

        feed_data["updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if feed.feed.get("author_detail"):
            if feed.feed.get("author_detail").get("name"):
                feed_data["author"] = feed.feed.get("author_detail").get(
                    "name"
                )
        else:
            feed_data["author"] = "Anonymous"

        if config_filtered_entries:
            print(
                f"==== Found {len(config_filtered_entries)} new entries for URL: {url}"
            )
        else:
            print(f"==== No new entries found for URL: {url}")

        # Update cache if there's a change and if caching is enabled
        if caching:
            new_last_seen_id = feed.entries[0]["id"] if feed.entries else None
            new_etag = getattr(feed, "etag", None)
            new_last_modified = getattr(feed, "modified", None)
            print(f"==== New etag: {new_etag}")
            print(f"==== New last modified: {new_last_modified}")
            cacher.update_cache(
                url, new_last_seen_id, new_etag, new_last_modified
            )
            print(f"==== Updated cache for {url}")

        return config_filtered_entries, feed_data

    except Exception as e:
        print(f"==== Error processing URL {url}: {e}")
        return {}, []


def process_yaml(caching):
    """
    Main function to process configuration from YAML and extract RSS feeds.
    """
    print("==== Starting to process configurations")
    if caching:
        cacher.setup_database()

    with open("yaml-config/rss_config.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)

    # Iterate over each configuration
    for config in yaml_config:
        print(f"==== Processing configuration for slug: {config['slug']}")

        aggregated_entries = []

        # Iterate over each URL in configuration
        for url in config["urls"]:
            filtered_entries, feed_data = process_feed_url(
                config, url, caching
            )
            aggregated_entries.extend(filtered_entries)

        # Output filtered entries to XML file
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {config['slug']}"
        )
        output_feeds(config["slug"], aggregated_entries, feed_data, caching)

        print(
            f"==== Finished processing configuration for slug: {config['slug']}"
        )
        print("==== ")

    print("==== Finished processing all configurations")
