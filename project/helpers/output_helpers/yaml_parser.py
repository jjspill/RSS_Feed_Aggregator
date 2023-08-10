import helpers.cache_helpers.cacher as cacher
import helpers.output_helpers.feed_parser as parser
import helpers.output_helpers.feed_writer as writer

import yaml


def process_yaml(caching):
    """
    Main function to process configuration from YAML and extract feeds.
    """
    print("==== Starting to process configurations")
    print("==== ")
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
            filtered_entries, feed_data = parser.process_feed_url(
                config, url, caching
            )
            aggregated_entries.extend(filtered_entries)

        # Output filtered entries to XML file
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {config['slug']}"
        )

        if aggregated_entries:
            writer.output_feed(
                config["slug"], aggregated_entries, feed_data, caching
            )
        else:
            print(f"==== No new entries found for {config['slug']}")

        print(
            f"==== Finished processing configuration for slug: {config['slug']}"
        )
        print("==== ")

    print("==== Finished processing all configurations")
