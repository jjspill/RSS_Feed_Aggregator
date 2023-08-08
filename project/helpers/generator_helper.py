from dotenv import load_dotenv
from pyairtable import Api
import os
import yaml

# Constants
TABLE_NAME = "RSS FEED Aggregator"
TABLE_FIELDS = ["name", "slug", "urls", "match", "exclude"]


def auth():
    """
    Authenticate and return API instance for Airtable.
    """
    load_dotenv("../tokens.env")
    return Api(os.getenv("AIRTABLE_API_KEY"))


def fetch_table_data(api, table_name):
    """
    Fetch specified fields from Airtable table.
    """
    table = api.table(os.getenv("AIRTABLE_BASE_ID"), table_name)
    return [record["fields"] for record in table.all(fields=TABLE_FIELDS)]


def process_table_data(data):
    """
    Strip whitespace from list items in table data.
    """
    for field, value in data.items():
        if isinstance(value, list):
            data[field] = [item.strip() for item in value]
    return data


def generate_yaml():
    """
    Fetch data from Airtable, process, and save as a YAML file.
    """
    # Authenticate
    api = auth()

    # Fetch data from Airtable
    processed_data = [
        process_table_data(data) for data in fetch_table_data(api, TABLE_NAME)
    ]

    # Save data as YAML file
    with open("yaml-config/rss_config.yaml", "w") as f:
        f.write(
            yaml.dump(
                processed_data, sort_keys=False, indent=4, allow_unicode=True
            )
        )
