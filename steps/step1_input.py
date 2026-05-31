# steps/step1_input.py
# PURPOSE: Builds the left sidebar with all 7 filter sections (covering 9 data layers).
# Also checks user messages for safety before sending them to the AI.
#
# WHO OWNS THIS FILE: Member 1 (Frontend)
# NO API KEYS NEEDED — this is pure Streamlit UI code.

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# SAFETY CHECK — Prompt Sanitization
# ─────────────────────────────────────────────────────────────────────────────

# These are phrases that bad actors use to "trick" an AI into ignoring its rules.
# We check for these BEFORE sending the user's message to Claude Haiku.
# This is called "prompt injection defense."
INJECTION_FLAGS = [
    "ignore your instructions",
    "pretend you are",
    "forget your role",
    "you are now",
    "jailbreak",
    "bypass your",
    "act as chatgpt",
    "act as gemini",
    "disregard your",
    "override your",
]


def sanitize_input(query: str) -> tuple:
    """
    Checks if a user's message is safe to send to the AI.

    Parameters:
    - query: the raw text the user typed

    Returns: (cleaned_query, is_safe)
    - cleaned_query: the message with extra whitespace removed
    - is_safe: True = safe to process, False = block this message
    """
    # Remove leading/trailing spaces
    q = query.strip()

    # Reject if message is too short to be meaningful
    if len(q) < 3:
        return q, False

    # Check for injection phrases (case-insensitive — catches "IGNORE" and "ignore")
    if any(flag in q.lower() for flag in INJECTION_FLAGS):
        return q, False

    # Message passed all checks
    return q, True


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Filter Sections
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> tuple:
    """
    Builds the entire left sidebar with 7 collapsible filter sections.
    Each section covers one or more of the 9 data layers.

    Returns: (preferences dict, generate_clicked bool)
    - preferences: all current filter settings as a dictionary
    - generate_clicked: True if the user just clicked "Generate from filters"
    """
    preferences = {}  # We build this dict as we render each section

    with st.sidebar:
        st.title("Search Filters")
        st.caption("Set your preferences, or just type in the chat.")
        st.divider()

        # ── SECTION 1: WHERE — Layers I-1 and I-3 ────────────────────────
        # I-1 = Property listings (location fields)
        # I-3 = Neighborhood profile (city characteristics)
        with st.expander("Where — Location & neighborhood", expanded=True):

            preferences["city"] = st.selectbox(
                "City",
                options=[
                    "Any city in NCR",
                    "Makati",
                    "BGC / Taguig",
                    "Quezon City",
                    "Pasig",
                    "Mandaluyong",
                    "Pasay",
                    "Paranaque",
                    "Muntinlupa",
                    "Marikina",
                    "Caloocan",
                    "Manila (Intramuros / Ermita area)",
                ],
                # 'key' gives this widget a unique ID so Streamlit tracks it correctly
                key="city_select"
            )

            preferences["district"] = st.text_input(
                "District / area (optional)",
                placeholder="e.g. Rockwell, BGC, Eastwood, Ortigas…",
                key="district_input"
            )

        # ── SECTION 2: WHAT — Layers I-1 and I-9 ─────────────────────────
        # I-1 = Property type and offer type
        # I-9 = Building specifications (bedrooms, condition)
        with st.expander("What — Property type & offer"):

            preferences["property_type"] = st.radio(
                "Property type",
                options=["Condo", "House & Lot", "Townhouse", "Commercial"],
                index=0,  # Default = Condo (index 0 in the options list)
                key="prop_type_radio"
            )

            preferences["offer_type"] = st.radio(
                "Offer type",
                options=["For rent", "For sale", "Pre-selling"],
                index=0,  # Default = For rent
                key="offer_type_radio"
            )

            preferences["bedrooms"] = st.selectbox(
                "Bedrooms",
                options=["Any", "Studio", "1BR", "2BR", "3BR", "4BR+"],
                key="bedrooms_select"
            )

            preferences["condition"] = st.selectbox(
                "Unit condition",
                options=["Any condition", "Move-in ready", "Semi-furnished",
                         "Bare / For renovation", "Pre-selling / New"],
                key="condition_select"
            )

        # ── SECTION 3: BUDGET — Layers I-1 and I-5 ───────────────────────
        # I-1 = Listing price fields
        # I-5 = True ownership costs
        with st.expander("Budget — Pricing range"):

            preferences["budget_rent"] = st.slider(
                "Max monthly rent (₱)",
                min_value=5_000,
                max_value=150_000,
                value=30_000,       # Default starting value
                step=1_000,
                format="₱%d",       # Shows ₱ symbol in the slider label
                key="budget_rent_slider"
            )

            preferences["budget_purchase_m"] = st.slider(
                "Max purchase price (₱ Millions)",
                min_value=2,
                max_value=50,
                value=6,
                step=1,
                format="₱%dM",
                key="budget_purchase_slider"
            )

        # ── SECTION 4: COMMUTE — Layers I-2 and I-8 ──────────────────────
        # I-2 = Transit and mobility data
        # I-8 = Hidden transport costs (fuel, toll, time)
        with st.expander("Commute — Mobility & transport costs"):

            preferences["workplace"] = st.selectbox(
                "I work in",
                options=["BGC", "Makati CBD", "Ortigas",
                         "QC CBD (Eastwood / Cubao)", "Alabang",
                         "WFH / Fully remote"],
                key="workplace_select"
            )

            preferences["max_commute_mins"] = st.slider(
                "Max acceptable commute (minutes)",
                min_value=10,
                max_value=120,
                value=45,
                step=5,
                key="commute_slider"
            )

            preferences["transport_mode"] = st.radio(
                "Primary way to get to work",
                options=["Car / driving", "MRT / LRT + jeepney", "Grab / ride-hailing"],
                key="transport_radio"
            )

        # ── SECTION 5: LIFESTYLE — Layer I-4 ─────────────────────────────
        # I-4 = Household and lifestyle profiles
        with st.expander("Lifestyle — Household & work setup"):

            preferences["household_type"] = st.radio(
                "Household type",
                options=["Single", "Couple", "Family with kids",
                         "WFH Professional", "Senior / Retiree"],
                key="household_radio"
            )

            preferences["work_setup"] = st.radio(
                "Work setup",
                options=["Onsite (5 days/week)", "Hybrid (2–3 days/week)",
                         "WFH / Fully remote"],
                key="work_setup_radio"
            )

        # ── SECTION 6: UTILITIES — Layer I-7 ─────────────────────────────
        # I-7 = Energy, internet, water utilities
        with st.expander("Utilities — Energy & services"):

            preferences["solar_priority"] = st.toggle(
                "Solar panel is a priority for me",
                value=False,  # Off by default
                key="solar_toggle",
                help="Solar is only possible for house & lot owners. "
                     "MERALCO currently restricts condo solar installations."
            )

            preferences["fast_internet"] = st.toggle(
                "Fast fiber internet is required",
                value=True,   # On by default (most users need this)
                key="fiber_toggle"
            )

            preferences["water_zone"] = st.selectbox(
                "Water zone preference",
                options=["Any zone",
                         "Manila Water — East Zone (Pasig, Marikina, BGC, QC East)",
                         "Maynilad — West Zone (Makati, Paranaque, Muntinlupa, QC West)"],
                key="water_zone_select",
                help="NCR is split between two water providers with different rates."
            )

        # ── SECTION 7: MARKET — Layers I-5 and I-6 ───────────────────────
        # I-5 = Current ownership costs and rental yield
        # I-6 = Historical price data and forecasts
        with st.expander("Market — Forecast & investment view"):

            preferences["view_focus"] = st.radio(
                "My primary goal",
                options=["Renting a place to live",
                         "Buying a property to live in",
                         "Investing for rental income"],
                key="view_focus_radio"
            )

            preferences["forecast_horizon"] = st.selectbox(
                "Forecast time horizon",
                options=["6 months", "1 year", "2 years", "5 years"],
                index=1,  # Default = 1 year
                key="forecast_select"
            )

        st.divider()

        # ── GENERATE FROM FILTERS BUTTON ─────────────────────────────────
        # When clicked, this turns all filter settings into a chat message.
        # It's a shortcut so users don't have to type a question from scratch.
        generate_clicked = st.button(
            "Generate from filters ↗",
            type="primary",          # Streamlit "primary" = red button
            use_container_width=True, # Makes button stretch to sidebar width
            key="generate_btn"
        )

    # Return the preferences dict AND whether the button was just clicked
    return preferences, generate_clicked
