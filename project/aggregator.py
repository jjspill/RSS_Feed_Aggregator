import helpers.input_helpers.yaml_writer as generator
import helpers.output_helpers.yaml_parser as aggregator
import argparse


def run_(cache=False, entries_only=False):
    generator.generate_yaml()
    aggregator.process_yaml(cache, entries_only)


def cli_main():
    parser = argparse.ArgumentParser(description="RSS Feed Aggregator")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Enable caching to avoid processing old data",
    )
    parser.add_argument(
        "--entries-only",
        action="store_true",
        help="Print only the relevant entries without Atom formatting",
    )
    args = parser.parse_args()

    caching = args.cache
    entries_only = args.entries_only

    run_(caching, entries_only)


if __name__ == "__main__":
    cli_main()
