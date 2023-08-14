# RSS Feed Aggregator

The RSS Feed Aggregator is a Python tool that fetches, aggregates, and filters RSS feed data. It's built to provide an efficient way of gathering specific information from various sources as per the configured filters.

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
2. **Navigate to the project directory**
    ```bash
    cd /path/to/RSS_Feed_Aggregator/project
    ```

3. **Run the Aggregator without Caching:** (default mode)  
    This mode fetches and processes all RSS feed entries regardless of whether they've been processed previously.
    ```bash
    python3 project/aggregator.py
    ```

    aggregator.py can also be imported and called directly. The default value is without caching.
    ```python
    import aggregator

    aggregator.run()
    aggregator.run(cache=False)
    ```
    

4. **Run the Aggregator with Caching:**
    ```bash
    python3 project/aggregator.py --cache
    ```
    With the `--cache` flag, the Aggregator uses caching to improve speed. Before fetching new data, it first checks the ETag and Last-Modified headers to identify any changes since the last fetch. If no changes are detected, previously processed entries are skipped, ensuring that the Aggregator only processes new or updated entries.

    To import and call with caching, call with a True parameter.
    ```python
    import aggregator

    aggregator.run(cache=True)
    ```

5. **Alter the output of the Aggregator:**
    ```bash
    python3 project/aggregator.py --entries-only
    ```
    With the `--entries-only` flag, the Aggregator ouputs the relevant entries only in the format of the feed inputted. Only the `<entry>` or `<item>` tags and the data within them will be outputted.

    To import and call with entries_only, call with a True parameter.
    ```python
    import aggregator

    aggregator.run(entries_only=True)
    ```

5. **The results will be saved in the `project/rss-feeds` directory as XML files, categorized by their respective slugs**

## Notes
- **The default way the Aggregator runs is without caching and without the entries_only flag (so it produces valid Atom feeds).**
- **The Aggregator can handle both RSS and Atom feeds as inputs, but it will always output a valid Atom feed if entries_only is False.**
- **The Aggregator and cache will work with both entries_only = True or False, just keep in mind switching this field will cause problems with how the cached feeds / entries are merged with the new ones.**
- **All possible ways to run the aggregator are below:**
```python
    import aggregator

    aggregator.run(cache=True, entries_only=True)
    aggregator.run(cache=True, entries_only=False)
    aggregator.run(cache=False, entries_only=True)
    aggregator.run(cache=False, entries_only=False)
```