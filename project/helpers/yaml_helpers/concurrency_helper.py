import helpers.cache_helpers.cacher as cacher
import logging.handlers
import logging
import aiohttp
import asyncio


def reorganize_results(results):
    """
    Reorganize results from multiprocess processing.
    """

    reorganized_results = {}
    total_num_entries = 0

    # result = (config, result_dict)
    for result in results:
        if not result:
            continue

        (config, result_dict, num_entries_parsed) = result
        slug = config["slug"]

        if not result_dict:
            logging.error(f"Error processing {slug}")
            continue

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

        total_num_entries += num_entries_parsed

    return reorganized_results.values(), total_num_entries


async def fetch_url(config, url, caching=False):
    """
    Fetch URL and return status code and data.
    """

    logging.info(f"Fetching {config['slug']} URL: {url}")
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
    logging.info("")
    return [result for result in results if result is not None]


def async_run(yaml_config, caching=False):
    """
    Run async fetch for all URLs.
    """

    return asyncio.run(fetch_all_urls(yaml_config, caching))
