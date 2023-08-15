import helpers.input_helpers.yaml_writer as generator
import helpers.output_helpers.yaml_parser as aggregator
import argparse


def run_(cache=False, entries_only=True, multiprocessing=True):
    if multiprocessing:
        generator.generate_yaml()
        aggregator.process_yaml_multiprocessing(cache, entries_only)
    else:
        generator.generate_yaml()
        aggregator.process_yaml(cache, entries_only)


def cli_main():
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
        "-n",
        "--no_multiprocessing",
        action="store_true",
        help="Enable multiprocessing to speed up parsing",
    )
    args = parser.parse_args()

    caching = args.cache
    entries_only = not args.valid_rss
    multiprocessing = not args.no_multiprocessing

    run_(caching, entries_only, multiprocessing)


if __name__ == "__main__":
    cli_main()
