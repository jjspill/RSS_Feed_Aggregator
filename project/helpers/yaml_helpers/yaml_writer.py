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


def get_airtable_config():
    """
    Read JSON file and return data.
    """
    try:
        logging.info("Reading Airtable config file")
        with open("airtable-config/airtable_config.json", "r") as f:
            return json.load(f)

    except Exception as e:
        logging.error(f"ERROR reading JSON file: {e}")
        return None


def auth(airtable_data):
    """
    Authenticate and return API instance for Airtable.
    """
    try:
        logging.info("Authenticating with Airtable")
        return Api(airtable_data["AIRTABLE_API_KEY"])

    except Exception as e:
        logging.error(f"ERROR authenticating with Airtable: {e}")
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
        return [record["fields"] for record in table.all(fields=fields)]

    except Exception as e:
        logging.error(f"ERROR fetching table data from Airtable: {e}")
        return None


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
        logging.error(f"ERROR processing table data: {e}")
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
            logging.info(f"Record does not have all required fields: {d}")

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
                        f"ERROR validating URL {url}: {response.status_code}"
                    )
                    urls_to_remove.append(url)
            except Exception as e:
                logging.error(f"ERROR validating URL {url}: {e}")
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
    processed_data = [
        processed
        for data in fetch_table_data(api, airtable_data, TABLE_FIELDS)
        if (processed := process_table_data(data)) is not None
    ]

    if not processed_data:
        logging.info("No data found in Airtable. Exiting")
        exit(1)

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
