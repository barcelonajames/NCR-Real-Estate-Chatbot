# app.py
# PURPOSE: The main file that runs the entire chatbot application.
#
# FIX APPLIED (v1.1) — Two bugs fixed:
#
#   BUG 1 FIXED (raw JSON showing in chat):
#     step4_llm_match.py now uses a robust JSON extractor that strips
#     markdown code fences and stray text before parsing. The raw JSON
#     should no longer appear in the chat window.
#
#   BUG 2 FIXED (maps/cards/charts disappearing on page rerun):
#     We now store the FULL response dict (not just the text content)
#     in session state. When displaying chat history, assistant messages
#     that have stored response_data are fully re-rendered using
#     route_and_display() — so maps, cards, and charts persist.
#
# ── HOW TO RUN ───────────────────────────────────────────────────────────────
#   pip install -r requirements.txt
#   Copy .env.example → .env and fill in your API keys
#   streamlit run app.py
#   Opens at: http://localhost:8501
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from dotenv import load_dotenv

from steps.step1_input import render_sidebar, sanitize_input
from steps.step2_llm_intent import extract_intent
from steps.step3_searchapi import fetch_results
from steps.step4_llm_match import match_and_format
from steps.step5_display import route_and_display
from utils.session import init_session, get_history, append_message, clear_history

load_dotenv()

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NCR Real Estate Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session()


# ─────────────────────────────────────────────────────────────────────────────
# CORE PIPELINE FUNCTION
# Runs Steps 2 → 3 → 4 → 5 for any incoming query.
# Called whether the query came from the chat input or the sidebar button.
# ─────────────────────────────────────────────────────────────────────────────

def process_query(query: str, prefs: dict):
    """
    Runs the full 5-step pipeline for a given user query and displays the result.

    Parameters:
    - query: the user's message (already sanitized)
    - prefs: current sidebar filter settings
    """

    with st.spinner("Searching for the best answer…"):

        # ── STEP 2: Understand the question ───────────────────────────────
        history_without_last = get_history()[:-1]
        intent_data = extract_intent(
            query=query,
            preferences=prefs,
            conversation_history=history_without_last
        )

        # ── STEP 3: Fetch live data from the web ──────────────────────────
        keywords = intent_data.get("search_keywords", [query])
        search_results = fetch_results(keywords)

        # ── STEP 4: Match results to preferences + format response ─────────
        response = match_and_format(
            query=query,
            preferences=prefs,
            search_results=search_results,
            intent_data=intent_data
        )

    # ── STEP 5: Display the answer ────────────────────────────────────────
    # This runs OUTSIDE the spinner so the UI renders correctly.
    with st.chat_message("assistant"):
        route_and_display(response)

    # ── SAVE TO HISTORY ───────────────────────────────────────────────────
    # FIX (Bug 2): Store the FULL response dict, not just the text content.
    # This means maps, cards, and charts will re-render on page rerun.
    append_message(
        role="assistant",
        content=response.get("content", ""),
        response_data=response          # Full response stored here
    )


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: RENDER THE SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

preferences, generate_clicked = render_sidebar()
st.session_state.preferences = preferences


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CHAT AREA
# ─────────────────────────────────────────────────────────────────────────────

col_title, col_clear = st.columns([6, 1])

with col_title:
    st.title("NCR Real Estate Assistant")
    st.caption(
        "Ask about properties, rental prices, commute costs, utilities, "
        "or use the filters on the left to start."
    )

with col_clear:
    if st.button("Clear", key="clear_btn", help="Start a new conversation"):
        clear_history()
        st.rerun()

st.divider()


# ── DISPLAY EXISTING CHAT HISTORY ─────────────────────────────────────────────
# FIX (Bug 2): When re-drawing chat history, check if an assistant message
# has stored response_data. If it does, use route_and_display() to fully
# re-render the response (map, cards, chart, etc.) — not just the text.
for message in get_history():
    with st.chat_message(message["role"]):

        if message["role"] == "assistant" and "response_data" in message:
            # Re-render the full structured response
            # This restores maps, listing cards, comparison tables, and charts
            route_and_display(message["response_data"])

        else:
            # User messages (and any assistant messages without stored data)
            # just show the plain text
            st.markdown(message["content"])


# ── HANDLE "GENERATE FROM FILTERS" BUTTON ─────────────────────────────────────
if generate_clicked:

    # Build a natural language question from the current sidebar preferences
    prop  = preferences.get("property_type", "property")
    city  = preferences.get("city", "NCR").replace("Any city in NCR", "Metro Manila")
    offer = preferences.get("offer_type", "for rent").lower()
    budget = preferences.get("budget_rent", 30000)
    beds   = preferences.get("bedrooms", "")
    workplace = preferences.get("workplace", "")
    commute   = preferences.get("max_commute_mins", 45)
    household = preferences.get("household_type", "")
    solar     = preferences.get("solar_priority", False)
    work_setup = preferences.get("work_setup", "")

    parts = []
    if beds and beds != "Any":
        parts.append(beds)
    parts.append(f"{prop.lower()} {offer}")
    if city != "Metro Manila":
        parts.append(f"in {city}")
    else:
        parts.append("anywhere in NCR")
    if offer == "for rent":
        parts.append(f"with a max budget of ₱{budget:,}/month")
    if workplace and "remote" not in workplace.lower():
        parts.append(f"within {commute} minutes commute to {workplace}")
    if solar:
        parts.append("with solar panel eligibility")
    if household:
        parts.append(f"for a {household.lower()} household")
    if "wfh" in work_setup.lower() or "remote" in work_setup.lower():
        parts.append("(WFH setup prioritized)")

    # Tag so Step 2 knows to skip the Haiku intent call and go straight to Step 3
    generated_query = "FILTER_GENERATED: I'm looking for a " + ", ".join(parts) + ". What do you recommend?"
    display_query   = "I'm looking for a " + ", ".join(parts) + ". What do you recommend?"

    with st.chat_message("user"):
        st.markdown(display_query)
    append_message("user", display_query)

    process_query(generated_query, preferences)


# ── CHAT INPUT ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me about NCR real estate…"):

    clean_query, is_safe = sanitize_input(prompt)

    if not is_safe:
        st.warning(
            "That message can't be processed. "
            "Please ask about Metro Manila real estate."
        )
    else:
        with st.chat_message("user"):
            st.markdown(clean_query)

        append_message("user", clean_query)
        process_query(clean_query, preferences)
