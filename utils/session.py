# utils/session.py
# PURPOSE: Manages the chat conversation history.
#
# FIX APPLIED (v1.1):
#   append_message() now accepts an optional response_data parameter.
#   For assistant messages, we store the FULL structured response
#   (not just the text content). This means maps, listing cards,
#   comparison tables, and TMC charts can be re-rendered when Streamlit
#   reruns the page — they no longer disappear on scroll or interaction.
#
# WHY STREAMLIT RERUNS:
#   Streamlit re-executes the entire script on every user interaction
#   (every keystroke, scroll, button click). Without storing the full
#   response, visual components would vanish after every rerun.

import streamlit as st

MAX_TURNS = 10  # Keep the last 10 exchanges in memory (20 messages total)


def init_session():
    """
    Sets up session state on first load.
    Does nothing if the session already has data.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "preferences" not in st.session_state:
        st.session_state.preferences = {}


def get_history() -> list:
    """
    Returns all chat messages as a list.
    Each message is a dict with at least 'role' and 'content'.
    Assistant messages may also have 'response_data' (the full JSON response).
    """
    return st.session_state.get("messages", [])


def append_message(role: str, content: str, response_data: dict = None):
    """
    Adds a message to the conversation history.

    Parameters:
    - role: "user" or "assistant"
    - content: the plain text of the message (used for AI context window)
    - response_data: (assistant only) the full structured response dict.
      When provided, the full response is stored so maps, cards, and
      charts can be re-drawn on Streamlit page reruns.

    WHY WE STORE response_data:
      Streamlit reruns the entire script on every interaction. The plain
      text content is enough for the AI to follow the conversation, but
      the visual components (Folium maps, listing cards, etc.) need the
      full structured data to be re-rendered correctly.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    message = {
        "role": role,
        "content": content
    }

    # For assistant messages, also store the full response so we can
    # re-render visual components (maps, cards, charts) on page rerun
    if role == "assistant" and response_data is not None:
        message["response_data"] = response_data

    st.session_state.messages.append(message)
    _trim_history()


def _trim_history():
    """
    Removes oldest messages if the conversation exceeds MAX_TURNS.
    Keeps the conversation fast and the API costs low.
    """
    max_messages = MAX_TURNS * 2

    if len(st.session_state.messages) > max_messages:
        # Keep only the most recent messages
        st.session_state.messages = st.session_state.messages[-max_messages:]


def clear_history():
    """
    Clears all conversation history. Called by the Clear button.
    """
    st.session_state.messages = []
