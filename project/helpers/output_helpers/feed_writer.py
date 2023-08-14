from helpers.output_helpers.feed_writer_class import (
    FeedProcessorET,
    FeedProcessorSTR,
)
import os


def output_feed(slug, entries, feed_data, feed_type, caching, entries_only):
    """
    Output XML feeds to respective files.
    """
    if not entries or not feed_data:
        print("==== No entries or feed data found")
        return None

    if not os.path.exists("rss-feeds"):
        os.makedirs("rss-feeds")

    output_file = f"rss-feeds/{slug}-feed.xml"

    xml_output = ""
    if entries_only:
        process_ET = FeedProcessorSTR(
            entries, feed_data, feed_type, output_file
        )
        process_ET.process_all()

        if caching:
            process_ET.cache()

        xml_output = process_ET.get_xml()

    else:
        process_STR = FeedProcessorET(entries, feed_data, output_file)
        process_STR.process_all()

        if caching:
            process_STR.cache()

        xml_output = process_STR.get_xml()

    with open(output_file, "w") as f:
        f.write(xml_output)
