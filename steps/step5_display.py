# steps/step5_display.py
# PURPOSE: Routes the formatted response from Step 4 to the right display component.
#
# This step reads the 'type' field in the JSON response and decides
# which component file to call:
#   "text"       → plain chat message (no special component needed)
#   "map"        → components/map_view.py (Folium interactive map)
#   "tmc"        → components/tmc_display.py (True Monthly Cost breakdown)
#   "comparison" → components/comparison.py (side-by-side table)
#   "links"      → components/link_cards.py (property listing cards)
#   "chart"      → components/charts.py (Plotly price trend chart)
#
# Think of this like a waiter who reads the order ticket and routes it
# to the right station in the kitchen.
#
# NO API KEYS NEEDED — pure Streamlit display logic.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import streamlit as st

# Import each display component
from components.map_view import render_map
from components.tmc_display import render_tmc
from components.comparison import render_comparison
from components.link_cards import render_links
from components.charts import render_chart


def route_and_display(response: dict):
    """
    Reads the 'type' field and calls the right display function.

    Parameters:
    - response: the JSON dict from Step 4.
      Always has 'type' and 'content'.
      May also have 'markers', 'breakdown', 'items', 'listings', or 'chart_data'.
    """

    # Read what type of response this is
    response_type = response.get("type", "text")

    # Every response type has a 'content' text field.
    # We always display this first as the conversational reply.
    content_text = response.get("content", "Here's what I found.")
    st.markdown(content_text)

    # ── ROUTE TO THE CORRECT COMPONENT ────────────────────────────────────
    # Based on 'type', call the matching render function below the text.

    if response_type == "map":
        # Show an interactive Folium map with property pins
        markers = response.get("markers", [])
        if markers:
            render_map(markers)
        else:
            st.info("No map coordinates were returned for this query.")

    elif response_type == "tmc":
        # Show the True Monthly Cost breakdown with metrics and bar chart
        breakdown = response.get("breakdown", {})
        if breakdown:
            render_tmc(breakdown)

    elif response_type == "comparison":
        # Show a side-by-side property comparison
        items = response.get("items", [])
        if items:
            render_comparison(items)

    elif response_type == "links":
        # Show clickable property listing cards with images
        listings = response.get("listings", [])
        if listings:
            render_links(listings)

    elif response_type == "chart":
        # Show a Plotly price trend line chart
        chart_data = response.get("chart_data", {})
        if chart_data:
            render_chart(chart_data)

    # If type is "text", we already showed the content above — nothing more to do.
