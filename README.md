# RSS Feed Aggregator

The RSS Feed Aggregator is a Python tool that fetches, aggregates, and filters RSS feed data. It's built to provide an efficient way of gathering specific information from various sources as per the configured filters.

## Installation & Setup

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/jjspill/RSS_Feed_Aggregator.git
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd /path/to/RSS_Feed_Aggregator
    ```

3. **Set Up a Virtual Environment** (Recommended):
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

4. **Install Dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```

## Running the Aggregator

1. **Activate the virtual environment if you've set it up**:
    ```bash
    source env/bin/activate
    ```

2. **Run the Aggregator without Caching** (default mode):
    ```bash
    python3 project/main.py
    ```
    This mode fetches and processes all RSS feed entries regardless of whether they've been processed previously.

3. **Run the Aggregator with Caching**:
    ```bash
    python3 main.py --cache
    ```
    With the `--cache` flag, the aggregator uses caching to improve speed. Entries that have been processed during previous runs will be skipped, ensuring that only new or updated entries are processed.

4. **The results will be saved in the `rss-feeds` directory as XML files, categorized by their respective slugs**