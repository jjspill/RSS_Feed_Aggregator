import xml.etree.ElementTree as ET
import helpers.cache_helper as cacher
from xml.dom import minidom
import feedparser
import yaml


def create_entries_element(root, entries):
    """
    Create and add entry elements to root element.
    """
    # Iterate over each entry
    for entry in entries:
        # Create entry element
        entry_element = ET.SubElement(root, "entry")

        # Entry Title
        if "title" in entry:
            title = ET.SubElement(entry_element, "title")
            title.text = entry["title"]

        # Entry Links
        if "links" in entry:
            for link_data in entry["links"]:
                ET.SubElement(entry_element, "link", attrib=link_data)

        # Entry Summary
        if "summary" in entry:
            summary = ET.SubElement(
                entry_element, "summary", attrib={"type": "html"}
            )
            summary.text = entry["summary"]

        # Entry Updated
        if "updated" in entry:
            updated = ET.SubElement(entry_element, "updated")
            updated.text = entry["updated"]

        # Entry Tags/Categories
        if "tags" in entry:
            for tag in entry["tags"]:
                attrib = {
                    "scheme": tag.get("scheme"),
                    "label": tag.get("label"),
                    "term": tag.get("term"),
                }
                ET.SubElement(entry_element, "category", attrib=attrib)

        # Entry ID
        if "id" in entry:
            id_elem = ET.SubElement(entry_element, "id")
            id_elem.text = entry["id"]

    return root


def convert_all_to_xml(header, entries):
    """
    Convert header and entries data to XML.
    """
    root = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")

    # Convert and add feed metadata to XML root

    # Feed Title
    if "title" in header:
        title = ET.SubElement(root, "title")
        title.text = header["title"]

    # Feed Links
    if "links" in header:
        for link in header["links"]:
            ET.SubElement(root, "link", attrib=link)

    # Feed ID
    if "id" in header:
        id_elem = ET.SubElement(root, "id")
        id_elem.text = header["id"]

    # Feed Author
    if "author" in header:
        author = ET.SubElement(root, "author")
        if "name" in header["author"]:
            name = ET.SubElement(author, "name")
            name.text = header["author"]["name"]
        if "email" in header["author"]:
            email = ET.SubElement(author, "email")
            email.text = header["author"]["email"]

    # Feed Updated
    if "updated" in header:
        updated = ET.SubElement(root, "updated")
        updated.text = header["updated"]

    # Add entries to root element
    root = create_entries_element(root, entries)

    # Beautify XML for better readability
    xml_content = ET.tostring(
        root, encoding="ISO-8859-1", method="xml"
    ).decode("ISO-8859-1")
    dom = minidom.parseString(xml_content)
    pretty_xml = dom.toprettyxml(indent="  ", encoding="ISO-8859-1").decode(
        "ISO-8859-1"
    )

    return pretty_xml


def output_feeds(slug, header, entries):
    """
    Output XML feeds to files.
    """
    output_file = f"rss-feeds/{slug}-feed.xml"
    with open(output_file, "w") as f:
        xml_str = convert_all_to_xml(header, entries)
        f.write(xml_str)


def extract_header_data(feed):
    """
    Extract header details from feed metadata.
    """
    header_data = {}

    if hasattr(feed, "title"):
        header_data["title"] = feed.title
    if hasattr(feed, "links"):
        header_data["links"] = [
            {"rel": link.rel, "href": link.href} for link in feed.links
        ]
    if hasattr(feed, "id"):
        header_data["id"] = feed.id

    author_data = {}
    if hasattr(feed, "author_detail"):
        if hasattr(feed.author_detail, "name"):
            author_data["name"] = feed.author_detail.name
        if hasattr(feed.author_detail, "email"):
            author_data["email"] = feed.author_detail.email
    if author_data:
        header_data["author"] = author_data

    if hasattr(feed, "updated"):
        header_data["updated"] = feed.updated

    return header_data


def check_keywords(entry, match_keywords, exclude_keywords):
    """
    Check if entry matches a keyword and does not contain excluded keywords.
    """
    content_to_check = " ".join(
        [
            entry.get("title", ""),
            entry.get("link", ""),
            entry.get("description", ""),
            entry.get("author", ""),
            ",".join(entry.get("category", [])),
            entry.get("comments", ""),
            entry.get("guid", ""),
            entry.get("pubDate", ""),
            entry.get("source", {}).get("title", ""),
        ]
    )

    return any(
        keyword in content_to_check for keyword in match_keywords
    ) and not any(keyword in content_to_check for keyword in exclude_keywords)


def process_feed_url(config, url, last_seen_id, caching):
    """Process individual feed URL and return filtered entries."""
    config_filtered_entries = []
    parsed_header_data = {}
    match_keywords = config["match"]
    exclude_keywords = config["exclude"]

    print(f"==== Fetching and parsing URL: {url}")
    try:
        feed = feedparser.parse(url)

        # Extract header data from feed metadata
        parsed_header_data = extract_header_data(feed.feed)

        # Filter entries based on keywords (for each URL)
        for entry in feed.entries:
            # If entry ID matches last seen ID, stop processing
            if entry["id"] == last_seen_id and caching:
                print("==== Reached last seen entry. Skipping older entries.")
                break
            if check_keywords(entry, match_keywords, exclude_keywords):
                config_filtered_entries.append(entry)

        # After processing all the entries for this feed, update the last seen ID.
        if config_filtered_entries:
            print(
                f"==== Found {len(config_filtered_entries)} new entries for URL: {url}"
            )

            if caching:
                cacher.update_last_seen_id(
                    config["slug"], url, config_filtered_entries[0]["id"]
                )
                print(
                    f"==== Updated cache with latest entry ID for {config['slug']}."
                )

    except Exception as e:
        print(f"==== Error processing URL {url}: {e}")

    return parsed_header_data, config_filtered_entries


def process_yaml(caching):
    """
    Main function to process configuration from YAML and extract RSS feeds.
    """
    print("==== Starting to process configurations...")

    with open("yaml-config/rss_config.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)

    # Iterate over each configuration
    for config in yaml_config:
        print(f"==== Processing configuration for slug: {config['slug']}")

        aggregated_entries = []
        parsed_header_data = {}

        # Iterate over each URL in configuration
        for url in config["urls"]:
            last_seen_id = cacher.get_last_seen_id(config["slug"], url)
            if last_seen_id and caching:
                print(
                    f"==== Last seen entry ID for {config['slug']}: {last_seen_id}"
                )
            elif caching:
                print(f"==== No cached entry found for {config['slug']}")
            else:
                print("==== Caching disabled. Processing all entries.")

            parsed_data, filtered_entries = process_feed_url(
                config, url, last_seen_id, caching
            )
            aggregated_entries.extend(filtered_entries)
            if not parsed_header_data:
                parsed_header_data = parsed_data

        # Output filtered entries to XML file
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {config['slug']}."
        )
        output_feeds(config["slug"], parsed_header_data, aggregated_entries)

        print(
            f"==== Finished processing configuration for slug: {config['slug']}"
        )

    print("==== Finished processing all configurations.")
