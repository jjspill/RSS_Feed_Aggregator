import helpers.input_helpers.yaml_writer as generator
import helpers.output_helpers.yaml_parser as aggregator
import argparse


def run_(
    cache=False,
    entries_only=True,
    multiprocessing=True,
    parsing=True,
    filepath=None,
):
    if not filepath:
        generator.generate_yaml()

    if multiprocessing and parsing:
        aggregator.process_yaml_multiprocessing(cache, entries_only, filepath)
    elif parsing:
        aggregator.process_yaml(cache, entries_only, filepath)


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
        "-nm",
        "--no_multiprocessing",
        action="store_true",
        dest="no_multiprocessing",
        help="Enable multiprocessing to speed up parsing",
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
    multiprocessing = not args.no_multiprocessing
    filepath = args.yaml
    parsing = not args.no_parsing

    run_(caching, entries_only, multiprocessing, parsing, filepath)


if __name__ == "__main__":
    cli_main()
