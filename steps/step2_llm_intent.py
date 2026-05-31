# steps/step2_llm_intent.py
# PURPOSE: First Claude Haiku call — understand what the user wants.
#
# This step DOES NOT search the web. It only reads the question and:
#   1. Figures out the user's INTENT (what they want to know)
#   2. Generates SEARCH KEYWORDS to use in Step 3
#   3. Confirms what it understood back to the user
#
# Think of this like a receptionist who listens to your question
# and decides which department to route you to.
#
# API KEY USED: ANTHROPIC_API_KEY
# WHO OWNS THIS FILE: Member 2 (LLM Layer)

import anthropic    # Official library for talking to Claude Haiku
import json         # For converting between JSON strings and Python dicts
from dotenv import load_dotenv  # For loading the .env file with API keys

from config.prompts import INTENT_PROMPT

# Load the ANTHROPIC_API_KEY from the .env file.
# This must happen before we create the Anthropic client.
load_dotenv()

# Create ONE Anthropic client that the whole app reuses.
# anthropic.Anthropic() automatically reads ANTHROPIC_API_KEY from the environment.
# Think of this as "dialing in" to Claude Haiku once.
client = anthropic.Anthropic()


def extract_intent(query: str, preferences: dict, conversation_history: list) -> dict:
    """
    Sends the user's question to Claude Haiku to understand their intent
    and prepare search keywords for Step 3.

    Parameters:
    - query: what the user typed (already sanitized in Step 1)
    - preferences: the current sidebar filter settings
    - conversation_history: all previous messages (so Haiku remembers context)

    Returns: a dict like:
    {
        "intent": "find_listings",
        "search_keywords": ["2BR condo for rent BGC Philippines"],
        "preferences_confirmed": {...},
        "reaffirmation": "Looking for...",
        "response_type": "links"
    }
    """

    # ── SHORTCUT: Filter-generated queries ───────────────────────────────
    # If the query was built automatically from sidebar filters (not typed by the user),
    # we skip the Haiku call and build the intent directly.
    # This saves API tokens (= money) because the intent is already obvious.
    if query.startswith("FILTER_GENERATED:"):
        clean_query = query.replace("FILTER_GENERATED:", "").strip()
        return _build_intent_from_filters(clean_query, preferences)

    # ── PREPARE THE MESSAGE FOR HAIKU ────────────────────────────────────
    # We combine the user's question with their sidebar preferences.
    # This gives Haiku the full picture — both what was typed AND what was filtered.
    full_context = f"""User query: {query}

Current sidebar preferences:
- City: {preferences.get('city', 'Not specified')}
- Property type: {preferences.get('property_type', 'Not specified')}
- Offer type: {preferences.get('offer_type', 'Not specified')}
- Bedrooms: {preferences.get('bedrooms', 'Not specified')}
- Max monthly rent: ₱{preferences.get('budget_rent', 'Not set'):,}
- Works in: {preferences.get('workplace', 'Not specified')}
- Household type: {preferences.get('household_type', 'Not specified')}
- Solar priority: {preferences.get('solar_priority', False)}
- Work setup: {preferences.get('work_setup', 'Not specified')}"""

    # Build the full message list for Haiku.
    # We start with the conversation history (so Haiku remembers past messages)
    # and add the current message at the end.
    messages = list(conversation_history)  # Copy the history list
    messages.append({
        "role": "user",
        "content": full_context
    })

    # ── CALL CLAUDE HAIKU ────────────────────────────────────────────────
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # The specific Haiku model
            max_tokens=512,                      # Short response = just the JSON we need
            system=INTENT_PROMPT,               # Instructions from config/prompts.py
            messages=messages
        )

        # response.content[0].text is the raw text Haiku returned.
        # json.loads() converts the JSON string into a Python dictionary.
        raw_text = response.content[0].text.strip()
        return json.loads(raw_text)

    except json.JSONDecodeError:
        # If Haiku returned something that isn't valid JSON,
        # we fall back to a simple keyword search instead of crashing.
        return _build_intent_from_filters(query, preferences)

    except Exception:
        # Catch any other error (network issue, API down, etc.)
        return _build_intent_from_filters(query, preferences)


def _build_intent_from_filters(query: str, preferences: dict) -> dict:
    """
    Builds an intent dictionary DIRECTLY from sidebar preferences.
    Used as a fallback when Haiku isn't needed (filter-generated queries)
    or when there's an API error.

    No API call is made here — this is pure Python logic.
    """
    # Pull values from preferences, with sensible defaults if missing
    prop = preferences.get("property_type", "property").lower()
    city = preferences.get("city", "NCR").replace("Any city in NCR", "Metro Manila")
    offer = preferences.get("offer_type", "for rent").lower()
    budget = preferences.get("budget_rent", 30000)
    beds = preferences.get("bedrooms", "")

    # Build a natural Google search query from the filter values
    bed_part = f"{beds} " if beds and beds != "Any" else ""
    keyword = f"{bed_part}{prop} {offer} {city} Philippines under {budget:,}"

    return {
        "intent": "find_listings",
        "search_keywords": [keyword],
        "preferences_confirmed": preferences,
        "reaffirmation": query,
        "response_type": "links"
    }
