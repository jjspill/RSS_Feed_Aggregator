# RSS Feed Aggregator

The RSS Feed Aggregator is a Python tool that fetches, aggregates, and filters RSS feed data. It's built to provide an efficient way of gathering specific information from various sources as per the configuration filters.

## Installation & Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/jjspill/RSS_Feed_Aggregator.git
    ```

2. **Navigate to the Repository:**
    ```bash
    cd /path/to/RSS_Feed_Aggregator
    ```

3. **Set Up and Start a Virtual Environment:** (Highly Recommended)
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

4. **Install Dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

5. **Add Airtable Configuration File:**  
    Create a new file in the `project/airtable-config` directory and name it `airtable_config.json`.
    Open the new file in a text editor.
    Add the following lines to the file, replacing `<...>` with your actual values:
    ```json
    {
	    "AIRTABLE_API_KEY":"<Your Airtable API Key>",
	    "AIRTABLE_BASE_ID":"<Your Base ID>",
	    "AIRTABLE_TABLE_NAME":"<Your Airtable Table Name>",
	    "AIRTABLE_VIEW_NAME":"<Your Airtable Grid Name>"
    }
    ```

## Running the RSS Aggregator

1. **Activate the Virtual Environment:** (it might be active already)
    ```bash
    source env/bin/activate
    ```
2. **Navigate to the project directory:**
    ```bash
    cd /path/to/RSS_Feed_Aggregator/project
    ```

3. **Run the Aggregator in default mode:**
    ```bash
    python3 aggregator.py
    ```
    Default mode means that the Aggregator will output entries only and will use concurrency to fetch, parse, and write to files.

4. **The results will be saved in the `project/rss-feeds` directory as XML files, categorized by their respective slugs**  

5. **Logs are written to `main_log.log`**

6. **Other Flags**
- Use `--cache` or `-c` to enable caching of past URLs.
- Use `--valid_rss` or `-v` to output a valid atom feed.
- Use `--no_concurrency` or `-nc` to disable concurrency.
- Use `--no_parsing` or `-np` to disable parsing and only create a configuration YAML.
- Use `--yaml` or `-y` to disable YAML creation and use an already created configuration YAML.

## Notes
- **valid_rss (-v) Clarification: This means that header data (namespace, encoding, ...) will be at the top of the `.xml` file and the output will be a valid Atom feed.**
- **The Aggregator can handle both RSS and Atom feeds as inputs, but it will always output a valid Atom feed if valid_rss is enabled.**
- **The Aggregator and cache will work with any flags just keep in mind changing the cache or valid_rss flags in between consecutive runs will cause problems with how the cached feeds / entries are merged with the new ones.**