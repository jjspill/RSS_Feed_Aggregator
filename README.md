# RSS Feed Aggregator

The RSS Feed Aggregator is a Python tool that fetches, aggregates, and filters RSS feed data. It's built to provide an efficient way of gathering specific information from various sources as per the configured filters.

## Installation & Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/jjspill/RSS_Feed_Aggregator.git
    ```

2. **Navigate to the Project Directory:**
    ```bash
    cd /path/to/RSS_Feed_Aggregator
    ```

3. **Set Up a Virtual Environment:** (Highly Recommended)
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

1. **Activate the Virtual Environmentp:**
    ```bash
    source env/bin/activate
    ```

3. **Run the Aggregator without Caching:** (default mode)
    ```bash
    python3 project/main.py
    ```
    This mode fetches and processes all RSS feed entries regardless of whether they've been processed previously.

4. **Run the Aggregator with Caching:**
    ```bash
    python3 project/main.py --cache
    ```
    With the `--cache` flag, the aggregator uses caching to improve speed. Before fetching new data, it first checks the ETag and Last-Modified headers to identify any changes since the last fetch. If no changes are detected, previously processed entries are skipped, ensuring that the aggregator only processes new or updated entries.

5. **The results will be saved in the `project/rss-feeds` directory as XML files, categorized by their respective slugs**

## Notes
- **Input Feeds**
    - The Aggregator can take both RSS and Atom feeds as input, but it will always output a valid Atom feed.