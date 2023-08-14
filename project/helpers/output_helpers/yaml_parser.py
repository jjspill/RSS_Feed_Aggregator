import helpers.cache_helpers.cacher as cacher
import helpers.output_helpers.feed_parser as parser
import helpers.output_helpers.feed_writer as writer
from collections import defaultdict
from multiprocessing import Pool
import requests
import yaml


def process_yaml(caching=False, entries_only=False):
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
        feed_type = "atom"

        # Iterate over each URL in configuration
        for url in config["urls"]:
            filtered_entries, feed_data, feed_type = parser.process_feed_url(
                config, url, caching
            )
            aggregated_entries.extend(filtered_entries)

        # Output filtered entries to XML file
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {config['slug']}"
        )

        if aggregated_entries:
            writer.output_feed(
                config["slug"],
                aggregated_entries,
                feed_data,
                feed_type,
                caching,
                entries_only,
            )
        else:
            print(f"==== No new entries found for {config['slug']}")

        print(
            f"==== Finished processing configuration for slug: {config['slug']}"
        )
        print("==== ")

    print("==== Finished processing all configurations")


def fetch_and_parse(args):
    url, config, caching = args
    print(f"Starting to fetch data from URL: {url}")
    response = requests.get(url)
    data = response.text
    print(f"Finished fetching data from URL: {url}. Now parsing...")
    parsed_data = parser.process_feed_url(config, data, caching)
    print(f"Completed parsing data from URL: {url}")
    return config["slug"], parsed_data


def process_yaml_with_multiprocessing(caching):
    print("Starting to process configurations using multiprocessing...")

    if caching:
        cacher.setup_database()

    with open("yaml-config/rss_config.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)

    with Pool() as pool:
        args_list = [
            (url, config, caching)
            for config in yaml_config
            for url in config["urls"]
        ]
        results = pool.map(fetch_and_parse, args_list)

    # Group results by config slug
    grouped_results = defaultdict(list)
    for slug, result in results:
        grouped_results[slug].append(result)

    # Process grouped results
    for config in yaml_config:
        slug = config["slug"]
        aggregated_entries = []

        for filtered_entries, feed_data in grouped_results[slug]:
            aggregated_entries.extend(filtered_entries)

        print(f"==== Processing configuration for slug: {slug}")
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {slug}"
        )

        if aggregated_entries:
            writer.output_feed(slug, aggregated_entries, feed_data, caching)
        else:
            print(f"==== No new entries found for {slug}")

        print(f"==== Finished processing configuration for slug: {slug}")
        print("==== ")

    print("==== Finished processing all configurations")
