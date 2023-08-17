from pyairtable import Api
import logging
import yaml
import json
import os

# import requests


class MyDumper(yaml.Dumper):
    """
    Custom YAML dumper to force indentation of lists.
    """

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def fetch_last_modified(table):
    """
    Fetch last modified timestamp from Airtable.
    """
    records = table.all(
        sort=[{"field": "Last Modified", "direction": "desc"}], page_size=1
    )

    if records:
        return records[0]["fields"].get("Last Modified")
    return None


def get_airtable_config():
    """
    Read JSON file and return data.
    """
    try:
        logging.info("Reading Airtable config file")
        with open("airtable-config/airtable_config.json", "r") as f:
            return json.load(f)

    except Exception as e:
        logging.error(f"Error reading JSON file: {e}")
        return None


def auth(airtable_data):
    """
    Authenticate and return API instance for Airtable.
    """
    try:
        logging.info("Authenticating with Airtable")
        return Api(airtable_data["AIRTABLE_API_KEY"])

    except Exception as e:
        logging.error(f"Error authenticating with Airtable: {e}")
        return None


def fetch_table_data(api, airtable_data, fields):
    """
    Fetch specified fields from Airtable table.
    """
    try:
        logging.info("Fetching table data from Airtable")
        table = api.table(
            airtable_data["AIRTABLE_BASE_ID"],
            airtable_data["AIRTABLE_TABLE_NAME"],
        )

        # Fetch last modified timestamp from Airtable
        """
        current_timestamp = fetch_last_modified(table)
        _, _, cached_timestamp = cacher.fetch_cache("airtable_last_modified")

        if cached_timestamp and current_timestamp == cached_timestamp:
            logging.info("No new data found in Airtable, using same YAML")
            return None, "no_new_data"

        cacher.update_cache(
            "airtable_last_modified", None, None, current_timestamp
        )
        """

        return [
            record["fields"] for record in table.all(fields=fields)
        ], "success"

    except Exception as e:
        logging.error(f"Error fetching table data from Airtable: {e}")
        return None, "error"


def process_table_data(data):
    """
    Strip whitespace from list items in table data.
    """
    try:
        if not data:
            return None
        for field, value in data.items():
            if isinstance(value, list):
                data[field] = [item.strip() for item in value]
        return data

    except Exception as e:
        logging.error(f"Error processing table data: {e}")
        return None


def validate(data):
    """
    Validate data from Airtable.
    """
    required_fields = ["name", "slug", "urls"]
    filtered_data = []

    # Filter out records that do not have all required fields
    for d in data:
        if all(key in d for key in required_fields):
            filtered_data.append(d)
        else:
            logging.error(f"Record does not have all required fields: {d}")

    return filtered_data  # move to bottom if uncommenting below

    # Validate URLs
    # Commenting because bad URLs are checked after feed is parsed
    """
    for d in filtered_data:
        urls_to_remove = []
        for url in d["urls"]:
            try:
                response = requests.get(url, timeout=5)
                if not (200 <= response.status_code < 300):
                    print(
                        f"Error validating URL {url}: {response.status_code}"
                    )
                    urls_to_remove.append(url)
            except Exception as e:
                logging.error(f"Error validating URL {url}: {e}")
                urls_to_remove.append(url)

        # Remove problematic URLs
        for url in urls_to_remove:
            logging.info(f"Removing URL {url} from record {d['name']}")
            d["urls"].remove(url)

        # Remove records that have no valid URLs
        if not d["urls"]:
            print(
                f"Removing record {d['name']} because it has no valid URLs"
            )
            filtered_data.remove(d)
    """


def generate_yaml():
    """
    Fetch data from Airtable, process, and save as a YAML file.
    """

    # Read JSON file
    airtable_data = get_airtable_config()

    # Authenticate
    api = auth(airtable_data)

    # Specify fields to fetch from Airtable
    TABLE_FIELDS = ["name", "slug", "urls", "match", "exclude"]

    # Fetch data from Airtable
    table_data, status = fetch_table_data(api, airtable_data, TABLE_FIELDS)

    if status == "no_new_data":
        logging.info("Airtable data has not changed. Using same YAML.")
        return

    elif not table_data or status != "success":
        logging.info(
            "No data found in Airtable or an error occurred. Exiting."
        )
        exit(1)

    processed_data = [
        processed
        for data in table_data
        if (processed := process_table_data(data)) is not None
    ]

    # Validate data
    processed_data = validate(processed_data)

    logging.info("Data found in Airtable, writing to YAML file")
    logging.info("")
    # Save data as YAML file

    if not os.path.exists("yaml-config"):
        os.makedirs("yaml-config")

    with open("yaml-config/rss_config.yaml", "w") as f:
        f.write(
            yaml.dump(
                processed_data,
                sort_keys=False,
                indent=4,
                allow_unicode=True,
                Dumper=MyDumper,
            )
        )
