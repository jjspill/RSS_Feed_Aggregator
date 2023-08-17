import helpers.yaml_helpers.concurrency_helper as concurrency
import helpers.feed_helpers.feed_writer as writer
import helpers.feed_helpers.feed_parser_class as parser
from multiprocessing import Pool
import logging
import yaml


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
        logging.error(f"Error: File '{filepath}' not found.")
    except PermissionError:
        logging.error(
            f"Error: Permission denied when trying to read '{filepath}'."
        )
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing YAML from '{filepath}': {exc}")
    except Exception as e:
        logging.error(f"Error loading YAML from '{filepath}': {e}")
    exit(1)


def process_yaml(caching=False, entries_only=False, filepath=None):
    """
    Process YAML by fetching, parsing, and writing to XML files.
    """

    logging.info("Processing configurations with concurrency")

    yaml_config = load_yaml_config(filepath)

    aggregated_results = []

    # (response status, config, url, response data, caching, cache_data)
    async_results = concurrency.async_run(yaml_config, caching)

    logging.info("Parsing all configurations")

    with Pool() as pool:
        multi_results = pool.map(
            parser.FeedProcessor.process_feed_wrapper, async_results
        )

        logging.info("Finished parsing all configurations")
        logging.info("")

        aggregated_results = concurrency.reorganize_results(multi_results)

    # Write to XML files
    writer_args_list = []
    for result in aggregated_results:
        if result["aggregated_entries"]:
            logging.info(
                f'FOUND a total of {len(result["aggregated_entries"])} new entries for {result["slug"]}'
            )
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
            logging.info(f"No new entries found for {result['slug']}")

    logging.info("")
    logging.info("Writing to XML files")
    with Pool() as pool:
        pool.map(writer.output_feed, writer_args_list)

    logging.info("Finished writing to XML files")

    logging.info("")
    logging.info("Finished processing all configurations")
