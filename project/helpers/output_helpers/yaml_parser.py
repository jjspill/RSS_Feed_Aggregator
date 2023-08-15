import helpers.cache_helpers.cacher as cacher
import helpers.output_helpers.feed_parser as parser
import helpers.output_helpers.feed_writer as writer
from multiprocessing import Pool
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
            result = parser.process_feed_url(config, url, caching)
            if not result[0]:
                continue

            filtered_entries, feed_data, feed_type = result

            aggregated_entries.extend(filtered_entries)

        # Output filtered entries to XML file
        print(
            f"==== Found a total of {len(aggregated_entries)} new entries for {config['slug']}"
        )

        if aggregated_entries:
            args_list = [
                config["slug"],
                aggregated_entries,
                feed_data,
                feed_type,
                caching,
                entries_only,
            ]
            writer.output_feed(args_list)
        else:
            print(f"==== No new entries found for {config['slug']}")

        print(
            f"==== Finished processing configuration for slug: {config['slug']}"
        )
        print("==== ")

    print("==== Finished processing all configurations")


def fetch_and_parse(args):
    url, config, caching = args
    print(f"==== Processing configuration for slug: {config['slug']}")
    print(f"==== Processing URL: {url}")

    try:
        result = parser.process_feed_url(config, url, caching)

        if not result[0]:
            return None

        result_dict = {
            "filtered_entries": result[0],
            "feed_data": result[1],
            "feed_type": result[2],
        }

        print(f"==== Finished processing URL: {url}")

        return (args, result_dict)

    except Exception as e:
        print(f"==== Error processing URL: {url}")
        print(e)


def reorganize_results(results):
    reorganized_results = {}

    for result in results:
        if not result:
            continue

        args, result_dict = result
        url, config, caching = args
        slug = config["slug"]

        if slug not in reorganized_results:
            reorganized_results[slug] = {
                "slug": slug,
                "aggregated_entries": [],
                "feed_data": result_dict["feed_data"],
                "feed_type": result_dict["feed_type"],
            }

        reorganized_results[slug]["aggregated_entries"].extend(
            result_dict["filtered_entries"]
        )

    return reorganized_results.values()


def process_yaml_multiprocessing(caching, entries_only):
    print("==== Starting to process configurations using multiprocessing")
    print("==== ")

    if caching:
        cacher.setup_database()

    with open("yaml-config/rss_config.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)

    aggregated_results = []

    with Pool() as pool:
        args_list = [
            (url, config, caching)
            for config in yaml_config
            for url in config["urls"]
        ]
        results = pool.map(fetch_and_parse, args_list)

        print("==== Finished processing all configurations")

        aggregated_results = reorganize_results(results)

    args_list = []
    for result in aggregated_results:
        if result["aggregated_entries"]:
            print(
                f'==== Found a total of {len(result["aggregated_entries"])} new entries for {result["slug"]}'
            )
            result_List = [
                result["slug"],
                result["aggregated_entries"],
                result["feed_data"],
                result["feed_type"],
                caching,
                entries_only,
            ]
            args_list.append(result_List)

        else:
            print(f"==== No new entries found for {result['slug']}")

    with Pool() as pool:
        pool.map(writer.output_feed, args_list)

    print("==== Finished processing all configurations")
