from helpers.feed_helpers.feed_writer_class import (
    FeedProcessorET,
    FeedProcessorSTR,
)


def output_feed(args_list):
    """
    Output XML feeds to respective files.
    """

    slug, entries, feed_data, feed_type, caching, entries_only = args_list[0]
    output_folder = args_list[1]

    output_file = f"rss_feeds/{output_folder}/{slug}_feed.xml"

    # If no entries or feed_data, then don't write to filex
    if not entries or not feed_data:
        if not caching:
            with open(output_file, "w") as f:
                pass
        return None

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
