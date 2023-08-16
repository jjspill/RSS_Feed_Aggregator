import helpers.feed_helpers.feed_parser as parser
import helpers.cache_helpers.cacher as cacher
import logging.handlers
import logging
import aiohttp
import asyncio


def parse(args):
    """
    Parse a URL.
    """
    log_queue = args[0]

    (
        response_status,
        config,
        url,
        feed_text,
        caching,
        cache_data,
    ) = args[1]

    worker_configurer(log_queue)
    logging.info(f"Parsing slug: {config['slug']}, URL: {url}")

    try:
        result = parser.only_process_feed(
            response_status, config, url, feed_text, caching, cache_data
        )

        if not result[0]:
            return None

        result_dict = {
            "filtered_entries": result[0],
            "feed_data": result[1],
            "feed_type": result[2],
        }

        logging.info(f"Finished parsing URL: {url}")
        logging.info("")

        return (args[1], result_dict)

    except Exception as e:
        logging.error(f"Error processing URL: {url}")
        logging.info(f"slug: {config['slug']}")
        logging.error(f"Error: {e}")
        logging.info("")


def reorganize_results(results):
    """
    Reorganize results from multiprocess processing.
    """

    reorganized_results = {}

    for result in results:
        if not result:
            continue

        args, result_dict = result
        config = args[1]
        slug = config["slug"]

        if slug not in reorganized_results:
            reorganized_results[slug] = {
                "slug": slug,
                "aggregated_entries": [],
                "feed_data": result_dict["feed_data"],
                "feed_type": result_dict["feed_type"],
            }

        reorganized_results[slug]["aggregated_entries"].extend(
            result_dict["filtered_entries"]
        )

    return reorganized_results.values()


async def fetch_url(config, url, caching=False):
    """
    Fetch URL and return status code and data.
    """
    logging.info(f"Fetching URL: {url}")
    slug_url = config["slug"] + url
    cache_data = cacher.fetch_cache(slug_url) if caching else None
    last_seen_id, etag_value, last_modified_value = cache_data or (
        None,
        None,
        None,
    )

    if cache_data and caching:
        logging.info("Cached entry found")
    elif not cache_data and caching:
        logging.info("No cached entry found")

    headers = {}
    if etag_value:
        headers["If-None-Match"] = etag_value
    if last_modified_value:
        headers["If-Modified-Since"] = last_modified_value

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 304:
                    logging.info(
                        "Feed has not been modified since the last request"
                    )
                    return None
                elif response.status == 404:
                    logging.error(f"Error: URL {url} not found.")
                    return None
                elif caching and not cache_data:
                    logging.info("No cached entry found for:", url)
                data = await response.text()
                return (
                    response.status,
                    config,
                    url,
                    data,
                    caching,
                    cache_data,
                )

    except aiohttp.ClientError as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None


async def fetch_all_urls(yaml_config, caching=False):
    """
    Fetch all URLs with async.
    """
    tasks = [
        fetch_url(config, url, caching)
        for config in yaml_config
        for url in config["urls"]
    ]

    logging.info("Fetching all URLs")
    logging.info("")
    results = await asyncio.gather(*tasks)
    logging.info("")
    logging.info("Finished fetching all URLs")
    return [result for result in results if result is not None]


def async_run(yaml_config, caching=False):
    """
    Run async fetch for all URLs.
    """
    return asyncio.run(fetch_all_urls(yaml_config, caching))


def listener_configurer():
    """
    Configure logging for listener process.
    """
    root = logging.getLogger()
    h = logging.StreamHandler()
    f = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    h.setFormatter(f)
    root.addHandler(h)


def listener_process(queue):
    """
    Process logs from queue.
    """
    listener_configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            pass


def worker_configurer(queue):
    """
    Configure logging for worker process.
    """
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.INFO)
