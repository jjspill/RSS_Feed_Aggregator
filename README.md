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
    Create a new file in the `project/airtable_config` directory and name it `airtable_config.json`
    Open the new file in a text editor
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
    Default mode means that the Aggregator will output entries only, use caching, and use concurrency to fetch, parse, and write to files

4. **Generated YAMLS will be saved to the `RSS_Feed_Aggregator/project/yaml_config` directory**

5. **The results will be saved in the `RSS_Feed_Aggregator/project/rss_feeds` directory as XML files, categorized by their respective slugs**  

6. **Logs are saved to the `RSS_Feed_Aggregator/project/logs` directory**

7. **Flags**
- Use `--caching` or `-c` to enable caching of aggregated entries for each configuration (when scheduling, caching is always used)
- Use `--valid_rss` or `-v` to output a valid atom feed for each configuration instead of only relevant entries
- Use `--no_parsing` or `-np` to disable parsing and only create a configuration YAML
- Use `--yaml <filepath>` or `-y <filepath>` to disable YAML creation and use an already created configuration YAML
- Use `--scheduler <total_time> <interval_time>` or `-s <total_time> <interval_time>` to run the Aggregator at regular intervals for a specific amount of time (this only works on MacOS)

## Airtable Setup
- A valid input Airtable table consists of five columns: name, slug, urls, match, exclude
    - name: a name for the record
    - slug: a URL-friendly version of the name
    - urls: a list of URLs to parse
    - match: a list of keywords to match (at least keyword one must match for the entry to be valid)
    - exclude: a list of keywords to exclude (one matching exclude keyword invalidates the entry)

## Notes
- valid_rss (-v) Clarification: This means that header data (namespace, encoding, ...) will be at the top of the `.xml` file and the output will be a valid Atom fee
- The Aggregator can handle both RSS and Atom feeds as inputs, but it will always output a valid Atom feed if valid_rss is enabled
- The Aggregator and cache will work with any flags just keep in mind changing the cache or valid_rss flags in between consecutive runs will cause problems with how the cached feeds / entries are merged with the new ones; if this problem occurs, delete the cache.db file in the cache_helpers directory
- When using the scheduler, if a YAML is not provided, the Airtable is parsed once before the first run and all other runs use the same `rss_config.yaml` file

## File Explanations
- aggregator.py: Serves as the main entry point, managing the command-line interface and overall orchestration
- yaml_writer.py: Interfaces with Airtable, and exports data to a YAML format located at `project/yaml_config/`
- yaml_processor.py: Interprets and processes configurations from the YAML file, delegating tasks to other modules as needed
- concurrency_helper.py: Provides utilities to streamline asynchronous tasks and manage multiprocessing for enhanced performance
- feed_parser_class.py: Handles the parsing of each URL and collects all relevant entries
- feed_writer_class.py: Dictates the format and structure of each entry, item, (or feed if --valid_rss is activated)
- feed_writer.py: Finalizes and writes processed data to designated output files
- cacher.py: Administers the caching mechanisms
- scheduler.py: Uses caffeinate to keep MacOS awake and dictates the total / interval timing