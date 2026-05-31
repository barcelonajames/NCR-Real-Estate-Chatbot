# components/map_view.py
# PURPOSE: Draws an interactive map of NCR with property pins.
#
# Uses Folium — a Python library that generates Leaflet.js maps.
# The map is embedded directly in the Streamlit page as HTML.
#
# Each pin on the map shows:
#   - Property name (tooltip on hover)
#   - Price and type (popup on click)
#   - A link to the actual listing
#
# NO API KEYS NEEDED — Folium works offline.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import folium                                    # Map creation library
import streamlit.components.v1 as components     # Embeds HTML in Streamlit
import streamlit as st

# NCR center coordinates — the map opens centered on Metro Manila
NCR_CENTER = [14.5995, 120.9842]

# Map pin colors by property type
# Folium uses named colors from the Font Awesome icon library
PIN_COLORS = {
    "condo": "blue",
    "house": "green",
    "house_and_lot": "green",
    "townhouse": "orange",
    "commercial": "red",
}


def render_map(markers: list):
    """
    Draws a Folium map with a pin for each property in the markers list.

    Parameters:
    - markers: list of dicts, each with:
      name (str), lat (float), lng (float), price (str), type (str), url (str)

    Example marker:
    {"name": "Avida Towers BGC", "lat": 14.5476, "lng": 121.0553,
     "price": "₱38,000/mo", "type": "condo", "url": "https://..."}
    """

    # ── CREATE THE BASE MAP ────────────────────────────────────────────────
    # location = the starting center of the map (NCR coordinates)
    # zoom_start = initial zoom level (12 = city level, good for NCR overview)
    # tiles = the map style ("CartoDB positron" = light, minimal, modern look)
    m = folium.Map(
        location=NCR_CENTER,
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # ── ADD A PIN FOR EACH PROPERTY ───────────────────────────────────────
    for marker in markers:
        lat = marker.get("lat")
        lng = marker.get("lng")

        # Skip this marker if coordinates are missing
        # (Haiku might not always have exact coordinates for every listing)
        if not lat or not lng:
            continue

        # Choose pin color based on property type
        prop_type = marker.get("type", "condo").lower()
        color = PIN_COLORS.get(prop_type, "blue")  # Default to blue if type unknown

        # ── BUILD THE POPUP CARD (shown when pin is clicked) ──────────────
        # This is an HTML mini-card that appears when the user clicks a pin.
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 210px; padding: 6px;">
            <b style="font-size: 13px; color: #1a1a2e;">
                {marker.get('name', 'Property')}
            </b>
            <br>
            <span style="color: #FF4B4B; font-weight: bold; font-size: 14px;">
                {marker.get('price', 'Price not listed')}
            </span>
            <br>
            <span style="color: #666; font-size: 11px; text-transform: capitalize;">
                {marker.get('type', '').replace('_', ' ')}
            </span>
            <br><br>
            <a href="{marker.get('url', '#')}" target="_blank"
               style="color: #1a73e8; font-size: 12px; text-decoration: none;">
                View listing ↗
            </a>
        </div>
        """

        # ── ADD PIN TO MAP ─────────────────────────────────────────────────
        # folium.Marker() places a clickable pin at the given coordinates.
        # 'popup' = the card shown when clicked
        # 'tooltip' = text shown when hovering (before clicking)
        # 'icon' = the pin style (color + icon symbol)
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=230),
            tooltip=marker.get("name", "Property"),
            icon=folium.Icon(color=color, icon="home", prefix="fa")
        ).add_to(m)

    # ── DISPLAY THE MAP IN STREAMLIT ──────────────────────────────────────
    # Folium generates an HTML string that contains the full map.
    # streamlit.components.v1.html() embeds any HTML directly in the page.
    # height=420 sets the map container height in pixels.
    st.subheader("Property locations on map")
    st.caption("Click any pin to see property details and listing link.")
    components.html(m._repr_html_(), height=420)
