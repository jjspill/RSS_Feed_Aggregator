import helpers.cache_helpers.cacher as cacher
import helpers.feed_helpers.feed_writer as writer
import helpers.feed_helpers.feed_parser as parser
import helpers.yaml_helpers.concurrency_helper as concurrency
from multiprocessing import Pool
import multiprocessing
import logging
import yaml


def load_yaml_config(filepath=None):
    """Load YAML configuration from a given file path or the default path."""
    default_path = "yaml-config/rss_config.yaml"

    filepath = filepath or default_path

    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"ERROR: File '{filepath}' not found.")
    except PermissionError:
        logging.error(
            f"ERROR: Permission denied when trying to read '{filepath}'."
        )
    except yaml.YAMLERROR as exc:
        logging.error(f"ERROR parsing YAML from '{filepath}': {exc}")
    exit(1)


def process_yaml(caching=False, entries_only=False, filepath=None):
    """
    Main function to process configuration from YAML and extract feeds.
    """
    logging.info("Starting to process configurations")
    logging.info("")
    if caching:
        cacher.setup_database()

    yaml_config = load_yaml_config(filepath)

    # Iterate over each configuration
    for config in yaml_config:
        logging.info(f"Processing configuration for slug: {config['slug']}")

        aggregated_entries = []
        feed_type = "atom"

        # Iterate over each URL in configuration
        for url in config["urls"]:
            result = parser.fetch_process_feed_url(config, url, caching)
            if not result[0]:
                continue

            filtered_entries, feed_data, feed_type = result

            aggregated_entries.extend(filtered_entries)

        # Output filtered entries to XML file
        logging.info(
            f"Found a total of {len(aggregated_entries)} new entries for {config['slug']}"
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
            logging.info(f"No new entries found for {config['slug']}")

        logging.info(
            f"Finished processing configuration for slug: {config['slug']}"
        )
        logging.info("")

    logging.info("Finished processing all configurations")


def process_yaml_concurrency(caching=False, entries_only=False, filepath=None):
    logging.info("Processing configurations with concurrency")

    if caching:
        cacher.setup_database()

    yaml_config = load_yaml_config(filepath)

    aggregated_results = []

    # (response status, config, url, response data, caching, cache_data)
    async_results = concurrency.async_run(yaml_config, caching)

    # Create a multiprocessing queue to store logs
    manager = multiprocessing.Manager()
    log_queue = manager.Queue()
    args_for_pool = [(log_queue, actual_arg) for actual_arg in async_results]

    logging.info("Parsing all configurations")
    logging.info("")

    # Start a listener process to log messages from the queue
    log_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(
        target=concurrency.listener_process, args=(log_queue,)
    )
    listener.start()

    with Pool() as pool:
        multi_results = pool.map(concurrency.parse, args_for_pool)

        logging.info("Finished parsing all configurations")
        logging.info("")

        aggregated_results = concurrency.reorganize_results(multi_results)

    # Stop the listener process
    log_queue.put_nowait(None)
    listener.join()

    args_list = []
    for result in aggregated_results:
        if result["aggregated_entries"]:
            logging.info(
                f'Found a total of {len(result["aggregated_entries"])} new entries for {result["slug"]}'
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
            logging.info(f"No new entries found for {result['slug']}")

    logging.info("")
    logging.info("Writing to XML files")
    with Pool() as pool:
        pool.map(writer.output_feed, args_list)

    logging.info("Finished writing to XML files")

    logging.info("")
    logging.info("Finished processing all configurations")
