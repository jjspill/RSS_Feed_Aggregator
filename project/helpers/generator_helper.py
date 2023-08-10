from pyairtable import Api
import yaml
import json


def get_airtable_data():
    """
    Read JSON file and return data.
    """
    try:
        print("==== Reading Airtable config file")
        with open("airtable-config/airtable_config.json", "r") as f:
            return json.load(f)

    except Exception as e:
        print(f"==== Error reading JSON file: {e}")
        return None


def auth(airtable_data):
    """
    Authenticate and return API instance for Airtable.
    """
    try:
        print("==== Authenticating with Airtable")
        return Api(airtable_data["AIRTABLE_API_KEY"])

    except Exception as e:
        print(f"==== Error authenticating with Airtable: {e}")
        return None


def fetch_table_data(api, airtable_data, fields):
    """
    Fetch specified fields from Airtable table.
    """
    try:
        print("==== Fetching table data from Airtable")
        table = api.table(
            airtable_data["AIRTABLE_BASE_ID"],
            airtable_data["AIRTABLE_TABLE_NAME"],
        )
        return [record["fields"] for record in table.all(fields=fields)]

    except Exception as e:
        print(f"==== Error fetching table data from Airtable: {e}")
        return None


def process_table_data(data):
    """
    Strip whitespace from list items in table data.
    """
    try:
        print("==== Processing table data")
        for field, value in data.items():
            if isinstance(value, list):
                data[field] = [item.strip() for item in value]
        return data

    except Exception as e:
        print(f"==== Error processing table data: {e}")
        return None


def generate_yaml():
    """
    Fetch data from Airtable, process, and save as a YAML file.
    """

    # Read JSON file
    airtable_data = get_airtable_data()

    # Authenticate
    api = auth(airtable_data)

    # Specify fields to fetch from Airtable
    TABLE_FIELDS = ["name", "slug", "urls", "match", "exclude"]

    # Fetch data from Airtable
    processed_data = [
        process_table_data(data)
        for data in fetch_table_data(api, airtable_data, TABLE_FIELDS)
    ]

    if not processed_data:
        print("==== No data found in Airtable. Exiting")
        return

    else:
        print("==== Data found in Airtable. Processing")
        # Save data as YAML file
        with open("yaml-config/rss_config.yaml", "w") as f:
            f.write(
                yaml.dump(
                    processed_data,
                    sort_keys=False,
                    indent=4,
                    allow_unicode=True,
                )
            )
