import helpers.generator_helper as generator
import helpers.aggregator_helper as aggregator
import argparse

# import cProfile


def main():
    parser = argparse.ArgumentParser(description="RSS Feed Aggregator")
    parser.add_argument(
        "--cache",
        action="store_true",
        help="Enable caching to avoid processing old data",
    )
    args = parser.parse_args()

    caching = args.cache

    generator.generate_yaml()
    aggregator.process_yaml(caching)


if __name__ == "__main__":
    # cProfile.run("main()", "profile_results.prof")
    main()
