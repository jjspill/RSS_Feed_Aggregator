import helpers.yaml_helpers.yaml_writer as generator
import helpers.yaml_helpers.yaml_processor as aggregator
import helpers.cache_helpers.cacher as cacher
import helpers.scheduler_helpers.scheduler as scheduler
import argparse
import logging
import time
import os


def config_logging():
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"log_{current_time}.log"
    log_folder = "logs"
    log_path = os.path.join(log_folder, log_filename)

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )


def scheduler_run(
    total_time,
    interval_time,
    caching=True,
    entries_only=True,
    parsing=True,
    filepath=None,
):
    """
    Run the RSS Feed Aggregator at a set interval.
    """
    config_logging()

    # Scheduler always using caching
    caching = True
    start_time_formatted = time.strftime("%Y-%m-%d_%H-%M-%S")

    logging.info(f"Starting Scheduler at {start_time_formatted}")
    database_path = "helpers/cache_helpers/cache.db"

    # Clear database
    if caching and os.path.exists(database_path):
        os.remove(database_path)

    output_folder = f"schedule_{start_time_formatted}"
    output_folder_path = os.path.join("rss_feeds", output_folder)

    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    wait_schedule = scheduler.scheduler(total_time, interval_time)

    if not filepath:
        logging.info("")
        generator.generate_yaml()
        filepath = "yaml_config/rss_config.yaml"

    running = True
    while running:
        try:
            run_(caching, entries_only, parsing, filepath, output_folder)
            logging.info("")
            logging.info("")
            logging.info(f"Sleeping for {interval_time} seconds")
            logging.info("")
            logging.info("")
            running = next(wait_schedule)

        except StopIteration:
            running = False

    logging.info(f"Ending Scheduler at {time.strftime('%Y-%m-%d_%H-%M-%S')}")


def run_(
    caching=False,
    entries_only=True,
    parsing=True,
    filepath=None,
    output_folder=None,
):
    """
    Run the RSS Feed Aggregator.
    """
    start_time = time.time()
    start_time_formatted = time.strftime("%Y-%m-%d_%H-%M-%S")

    output_folder_path = output_folder
    if not output_folder:
        output_folder = f"run_{start_time_formatted}"
        output_folder_path = os.path.join("rss_feeds", output_folder)

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

    logging.info("")
    logging.info(f"Starting RSS Feed Aggregator at {start_time_formatted}")
    logging.info("")

    cacher.setup_database()

    yaml_generation_time = None
    if not filepath:
        yaml_generation_start_time = time.time()

        generator.generate_yaml()

        yaml_generation_end_time = time.time()
        yaml_generation_time = (
            yaml_generation_end_time - yaml_generation_start_time
        )

    if parsing:
        aggregator.process_yaml(
            caching,
            entries_only,
            filepath,
            yaml_generation_time,
            output_folder,
        )

    endtime = time.time()
    duration = endtime - start_time
    logging.info(f"Duration of run:      {duration: .2f} seconds")

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
        "--caching",
        default=False,
        action="store_true",
        dest="cache",
        help="Enable caching to avoid processing old data",
    )
    parser.add_argument(
        "-v",
        "--valid_rss",
        default=True,
        action="store_false",
        dest="valid_rss",
        help="Print only the relevant entries without Atom formatting",
    )
    parser.add_argument(
        "-y",
        "--yaml",
        type=str,
        default=False,
        action="store",
        dest="yaml",
        help="Specify the yaml configuration",
    )
    parser.add_argument(
        "-np",
        "--no_parsing",
        default=True,
        action="store_false",
        dest="no_parsing",
        help="Disable parsing and only write the yaml file",
    )
    parser.add_argument(
        "-s",
        "--scheduler",
        nargs=2,
        type=int,
        dest="scheduler",
        default=False,
        help="Schedule aggregator to run at a set interval. -s <total_time> <interval_time>",
    )

    args = parser.parse_args()

    if args.yaml and not os.path.exists(args.yaml):
        print(f"Error: The provided yaml file '{args.yaml}' does not exist.")
        return

    # Default is not to cache
    caching = args.cache

    # Default is to print only the relevant entries
    entries_only = args.valid_rss

    # Default is default yaml filepath
    filepath = args.yaml

    # Default is to parse
    parsing = args.no_parsing

    # Default is to not schedule
    scheduling = args.scheduler

    if scheduling:
        total_time = scheduling[0]
        interval_time = scheduling[1]
        scheduler_run(
            total_time,
            interval_time,
            caching,
            entries_only,
            parsing,
            filepath,
        )
        return

    config_logging()

    run_(caching, entries_only, parsing, filepath)


if __name__ == "__main__":
    cli_main()
