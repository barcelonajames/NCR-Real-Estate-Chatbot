# steps/step4_llm_match.py
# PURPOSE: Second (and final) Claude Haiku call — match results and format answer.
#
# FIX APPLIED (v1.1):
#   Haiku sometimes wraps its JSON response in markdown code fences
#   (```json ... ```). The old extraction code didn't always strip these
#   reliably, causing the raw JSON to appear in the chat as a code block.
#   We now use a more robust _extract_json() helper that finds the actual
#   JSON object regardless of what surrounds it.
#
# API KEY USED: ANTHROPIC_API_KEY
# WHO OWNS THIS FILE: Member 2 (LLM Layer)

import anthropic
import json
from dotenv import load_dotenv

from config.prompts import MATCH_PROMPT

load_dotenv()

client = anthropic.Anthropic()


def _extract_json(raw_text: str) -> str:
    """
    Pulls the JSON object out of Haiku's raw response text.

    WHY THIS IS NEEDED:
    Haiku sometimes adds extra text around the JSON, like:
      - Markdown code fences:  ```json { ... } ```
      - Explanation text:      "Here is the response: { ... }"
    This function finds the actual JSON object ( { ... } ) and
    returns just that, ignoring everything else.
    """
    text = raw_text.strip()

    # Step 1: Remove markdown code fences if present
    # Haiku sometimes returns ```json { ... } ``` instead of just { ... }
    if "```" in text:
        # Split on ``` and take the content between the first pair
        parts = text.split("```")
        for part in parts:
            # Skip the "json" label line and empty parts
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            # If this part contains a JSON object, use it
            if cleaned.startswith("{"):
                text = cleaned
                break

    # Step 2: Find the outermost { ... } — ignore any text before or after
    # This handles cases like: "Here is the JSON: { ... } Let me know..."
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]

    return text.strip()


def match_and_format(
    query: str,
    preferences: dict,
    search_results: list,
    intent_data: dict
) -> dict:
    """
    Sends user preferences + live search results to Haiku for matching and formatting.

    Parameters:
    - query: the user's original question
    - preferences: current sidebar filter settings (from Step 1)
    - search_results: list of results from SearchAPI (from Step 3)
    - intent_data: what Haiku understood in Step 2

    Returns: a typed JSON dict. Examples:
      {"type": "text",  "content": "Here is what I found..."}
      {"type": "links", "content": "...", "listings": [...]}
      {"type": "tmc",   "content": "...", "breakdown": {...}}
    """

    # Bundle everything into one package to send to Haiku (RAG pattern)
    context = {
        "user_query": query,
        "user_preferences": preferences,
        "expected_response_type": intent_data.get("response_type", "text"),
        "search_results": search_results[:8]   # Limit to 8 to keep it focused
    }

    context_str = json.dumps(context, ensure_ascii=False)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=MATCH_PROMPT,
            messages=[{
                "role": "user",
                "content": context_str
            }]
        )

        raw_text = response.content[0].text

        # Use the robust extractor to get clean JSON
        # regardless of how Haiku formatted its output
        json_text = _extract_json(raw_text)

        result = json.loads(json_text)

        # Safety check: make sure the result has the required 'type' and 'content' fields
        # If Haiku returned something unexpected, convert it to a safe text response
        if not isinstance(result, dict) or "type" not in result:
            return {
                "type": "text",
                "content": str(result)
            }

        return result

    except json.JSONDecodeError:
        # JSON parsing failed even after our extraction attempt.
        # Return a clean error message — NOT the raw text — so the user
        # sees a friendly message instead of code.
        return {
            "type": "text",
            "content": (
                "I understood your question but had trouble formatting the answer. "
                "Could you try rephrasing it? For example: "
                "\"What is the average rent for a 2BR condo in BGC?\""
            )
        }

    except Exception:
        # Catch any other errors (network timeout, API issue, etc.)
        return {
            "type": "text",
            "content": "I'm having trouble connecting right now. Please try again in a moment."
        }
