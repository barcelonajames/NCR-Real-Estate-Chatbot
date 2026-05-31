# steps/step3_searchapi.py
# PURPOSE: Searches the internet for real, live property data.
#
# HOW IT WORKS:
#   1. Takes search keywords from Step 2
#   2. Sends them to SearchAPI (which searches Google on our behalf)
#   3. Returns a clean list of results (titles, URLs, snippets, images)
#
# KEY FEATURE — 4-Key Rotation:
#   Each SearchAPI free account has 100 searches. With 4 team members,
#   we have 400 combined searches. The code tries Key 1 first.
#   If Key 1 is used up (HTTP 429 error), it automatically tries Key 2, etc.
#
# NO AI / NO LLM HERE — this step is purely fetching data from the web.
#
# API KEYS USED: SEARCHAPI_KEY_1 through SEARCHAPI_KEY_4
# WHO OWNS THIS FILE: Member 3 (Data Layer)

import requests          # For making HTTP web requests (like a browser in Python)
import os                # For reading environment variables
import pandas as pd      # For cleaning and deduplicating results
from dotenv import load_dotenv

# Load all environment variables (API keys) from the .env file
load_dotenv()

# ── LOAD ALL 4 SEARCHAPI KEYS ─────────────────────────────────────────────────
# We build a list of 4 keys from the .env file.
# os.getenv() returns None if a key isn't set — we handle that inside fetch_results().
# This list comprehension is a compact Python way to build a list in one line.
SEARCHAPI_KEYS = [
    os.getenv(f"SEARCHAPI_KEY_{i}") for i in range(1, 5)
    # This generates: [KEY_1, KEY_2, KEY_3, KEY_4]
]

# The SearchAPI endpoint URL — this is where we send our search requests
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"


def fetch_results(keywords: list, num_results: int = 8) -> list:
    """
    Searches Google via SearchAPI for each keyword and returns clean results.

    Parameters:
    - keywords: list of search terms (built by Step 2)
                Example: ["2BR condo for rent BGC Philippines under 35000"]
    - num_results: how many Google results to fetch per keyword (default: 8)

    Returns: a list of dicts, each representing one search result:
    [{"title": "...", "link": "...", "snippet": "...", "thumbnail": "..."}, ...]
    """
    all_results = []  # Collect results from all keywords here

    for keyword in keywords:
        # Skip empty or None keywords to avoid wasted API calls
        if not keyword:
            continue

        # ── TRY EACH KEY IN ORDER ─────────────────────────────────────────
        # Key 1 is tried first. If it's exhausted, we move to Key 2, etc.
        # The 'break' inside the loop stops trying once a key succeeds.
        for key in SEARCHAPI_KEYS:

            # Skip if this key wasn't set in the .env file
            if not key:
                continue

            # ── BUILD THE SEARCH REQUEST ──────────────────────────────────
            params = {
                "engine": "google",    # Use Google Search (SearchAPI supports others too)
                "q": keyword,          # The search query text
                "num": num_results,    # Number of results to return
                "gl": "ph",            # Geographic location = Philippines
                                       # This biases results toward Filipino websites
                "hl": "en",            # Language = English
                "api_key": key         # The SearchAPI authentication key
            }

            try:
                # ── SEND THE REQUEST ──────────────────────────────────────
                # requests.get() sends an HTTP GET request, like visiting a URL in a browser.
                # timeout=10 means: if no response in 10 seconds, give up.
                response = requests.get(SEARCHAPI_URL, params=params, timeout=10)

                if response.status_code == 200:
                    # 200 = HTTP "Success" — we got results!
                    # .json() converts the response text into a Python dict
                    data = response.json()
                    results = data.get("organic_results", [])
                    # 'organic_results' = real search results (not ads)

                    all_results.extend(results)
                    break  # This key worked! Stop trying other keys for this keyword.

                elif response.status_code == 429:
                    # 429 = HTTP "Too Many Requests" — this key hit its 100-search limit
                    # 'continue' moves to the next key in the loop automatically
                    continue

                else:
                    # Some other HTTP error — skip this key and try the next
                    continue

            except requests.exceptions.Timeout:
                # The request took more than 10 seconds — skip and try next key
                continue

            except requests.exceptions.RequestException:
                # Any other network error — skip and try next key
                continue

    # ── CLEAN THE RESULTS ────────────────────────────────────────────────
    # We use pandas to remove duplicate listings and keep only needed columns.
    # This makes the data cleaner before passing it to Step 4.
    if not all_results:
        # If no results at all, return an empty list — the app handles this gracefully
        return []

    # Convert the list of dicts to a pandas DataFrame (like a spreadsheet)
    df = pd.DataFrame(all_results)

    # Keep only the columns we actually use in the app
    # reindex() safely adds missing columns as empty (NaN) instead of crashing
    needed_columns = ["title", "link", "snippet", "thumbnail"]
    df = df.reindex(columns=needed_columns)

    # Remove rows with the same URL (same listing appearing in multiple results)
    # 'subset="link"' means: check for duplicates only in the "link" column
    df = df.drop_duplicates(subset="link")

    # Remove rows where the URL is empty (no link = useless result)
    df = df.dropna(subset=["link"])

    # Replace empty thumbnail values with empty string (not NaN/None)
    # This prevents errors when we try to display images later in Step 5
    df["thumbnail"] = df["thumbnail"].fillna("")

    # Convert back from DataFrame to a plain Python list of dicts
    return df.to_dict("records")
