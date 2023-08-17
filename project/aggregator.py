import helpers.yaml_helpers.yaml_writer as generator
import helpers.yaml_helpers.yaml_processor as aggregator
import helpers.cache_helpers.cacher as cacher
import argparse
import logging


def run_(
    caching=False,
    entries_only=True,
    parsing=True,
    filepath=None,
):
    """
    Run the RSS Feed Aggregator.
    """

    logging.basicConfig(
        filename="main_log.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )

    logging.info("")
    logging.info("Starting RSS Feed Aggregator")
    logging.info("")

    cacher.setup_database()

    if not filepath:
        generator.generate_yaml()

    if parsing:
        aggregator.process_yaml(caching, entries_only, filepath)

    logging.info("")
    logging.info("Finished RSS Feed Aggregator")
    logging.info("")


def cli_main():
    """
    Run the RSS Feed Aggregator from the command line.
    """

    parser = argparse.ArgumentParser(description="RSS Feed Aggregator")
    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        dest="cache",
        help="Enable caching to avoid processing old data",
    )
    parser.add_argument(
        "-v",
        "--valid_css",
        action="store_true",
        dest="valid_rss",
        help="Print only the relevant entries without Atom formatting",
    )
    parser.add_argument(
        "-y",
        "--yaml",
        type=str,
        default=None,
        action="store",
        dest="yaml",
        help="Specify the yaml configuration",
    )
    parser.add_argument(
        "-np",
        "--no_parsing",
        action="store_true",
        dest="no_parsing",
        help="Disable parsing and only write the yaml file",
    )

    args = parser.parse_args()

    caching = args.cache
    entries_only = not args.valid_rss
    filepath = args.yaml
    parsing = not args.no_parsing

    run_(caching, entries_only, parsing, filepath)


if __name__ == "__main__":
    cli_main()
