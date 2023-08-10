import helpers.input_helpers.yaml_writer as generator
import helpers.output_helpers.yaml_parser as aggregator
import argparse


def run_(caching=False):
    generator.generate_yaml()
    aggregator.process_yaml(caching)


def cli_main():
    parser = argparse.ArgumentParser(description="RSS Feed Aggregator")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Enable caching to avoid processing old data",
    )
    args = parser.parse_args()

    caching = args.cache

    run_(caching)


if __name__ == "__main__":
    cli_main()
