import helpers.yaml_helpers.concurrency_helper as concurrency
import helpers.feed_helpers.feed_writer as writer
import helpers.feed_helpers.feed_parser_class as parser
from multiprocessing import Pool
import logging
import time
import yaml
import os


def load_yaml_config(filepath=None):
    """
    Load YAML configuration from a given file path or the default path.
    """

    default_path = "yaml_config/rss_config.yaml"

    filepath = filepath or default_path

    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Error File '{filepath}' not found.")
    except PermissionError:
        logging.error(
            f"Error: Permission denied when trying to read '{filepath}'."
        )
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing YAML from '{filepath}': {exc}")
    except Exception as e:
        logging.error(f"Error loading YAML from '{filepath}': {e}")
    exit(1)


def process_yaml(
    caching=False,
    entries_only=True,
    filepath=None,
    yaml_generation_time=None,
    output_folder=None,
):
    """
    Process YAML by fetching, parsing, and writing to XML files.
    """

    logging.info("Processing configurations with concurrency")

    yaml_config = load_yaml_config(filepath)

    aggregated_results = []
    multi_results = []
    async_start_time = time.time()
    # (response status, config, url, response data, caching, cache_data)
    url_data, async_results, all_304_slugs = concurrency.async_run(
        yaml_config, caching
    )
    async_end_time = time.time()

    logging.info("Parsing all configurations")
    parser_start_time = time.time()
    with Pool() as pool:
        multi_results = pool.map(
            parser.FeedProcessor.process_feed_wrapper, async_results
        )

    aggregated_results, total_num_entries = concurrency.reorganize_results(
        multi_results
    )

    logging.info("Finished parsing all configurations")
    logging.info("")
    parser_end_time = time.time()

    # Write to XML files
    writer_args_list = []
    total_entries_found = 0
    writer_start_time = time.time()

    if not os.path.exists("rss_feeds"):
        os.makedirs("rss_feeds")

    for result in aggregated_results:
        if result["aggregated_entries"]:
            logging.info(
                f'Found: {str(len(result["aggregated_entries"])).ljust(3)} entries for {result["slug"]}'
            )

            total_entries_found += len(result["aggregated_entries"])

            result_List = [
                result["slug"],
                result["aggregated_entries"],
                result["feed_data"],
                result["feed_type"],
                caching,
                entries_only,
            ]
            writer_args_list.append(result_List)

        else:
            logging.info(f'Found: 0   entries for {result["slug"]}')

            result_List = [
                result["slug"],
                None,
                None,
                None,
                caching,
                entries_only,
            ]

    for slug in all_304_slugs:
        logging.info(f"Found: 0   entries for {slug}")

    logging.info("")
    logging.info("Writing to XML files")

    writer_args_folder = [(args, output_folder) for args in writer_args_list]

    with Pool() as pool:
        pool.map(writer.output_feed, writer_args_folder)

    logging.info("Finished writing to XML files")
    writer_end_time = time.time()

    logging.info("")
    logging.info("Finished processing all configurations")
    logging.info("")

    logging.info("Summary:")
    logging.info("URL Fetching data:")
    logging.info(f"Number URLs: {url_data[0]}")
    logging.info(f"Success:     {(url_data[1])}")
    logging.info(
        f"Failed:      {(url_data[0]) - (url_data[1]) - (url_data[2])}"
    )
    logging.info(f"Cached:      {(url_data[2])}")
    logging.info("")
    logging.info("Feed Parsing data:")
    logging.info(f"Total entries parsed: {total_num_entries}")
    logging.info(f"Total entries found:  {total_entries_found}")
    logging.info("")
    logging.info("Time Profile:")

    async_duration = async_end_time - async_start_time
    parser_duration = parser_end_time - parser_start_time
    writer_duration = writer_end_time - writer_start_time

    if yaml_generation_time:
        logging.info(
            f"Duration of YAML gen: {yaml_generation_time: .2f} seconds"
        )
    logging.info(f"Duration of fetching: {async_duration: .2f} seconds")
    logging.info(f"Duration of parsing:  {parser_duration: .2f} seconds")
    logging.info(f"Duration of writing:  {writer_duration: .2f} seconds")
