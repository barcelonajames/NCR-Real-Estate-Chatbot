# components/link_cards.py
# PURPOSE: Shows real, live property listing cards from SearchAPI results.
#
# Each card shows:
#   - Property image (if available)
#   - Title (name of the listing)
#   - Price
#   - Location
#   - A button that opens the actual listing in a new tab
#
# These are REAL listings fetched from Google in Step 3 — not made-up data.
#
# NO API KEYS NEEDED — pure Streamlit display.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import streamlit as st


def render_links(listings: list):
    """
    Displays property listing cards in a 2-column grid.

    Parameters:
    - listings: list of dicts from Step 4, each with:
      title (str), price (str), area (str), url (str), image_url (str)
    """

    st.subheader("Current listings")
    st.caption("Live results from property websites. Click to view the full listing.")

    # Limit to 4 listings — showing more would clutter the page
    # and make it harder for the user to choose
    display_listings = listings[:4]

    if not display_listings:
        st.info("No listings were found for this query. Try adjusting your filters.")
        return

    # ── DISPLAY IN 2-COLUMN GRID ──────────────────────────────────────────
    # We loop through listings in pairs (index 0+1, then 2+3)
    # range(0, 4, 2) generates: 0, 2 (starting indexes for each row)
    for row_start in range(0, len(display_listings), 2):
        # Create 2 columns for this row
        cols = st.columns(2)

        for col_index, col in enumerate(cols):
            listing_index = row_start + col_index

            # Stop if we've run out of listings to show
            if listing_index >= len(display_listings):
                break

            listing = display_listings[listing_index]

            with col:
                # st.container(border=True) draws a bordered box around each card
                with st.container(border=True):

                    # ── PROPERTY IMAGE ──────────────────────────────────────
                    image_url = listing.get("image_url", "")
                    if image_url:
                        try:
                            # st.image() loads an image from a URL
                            # use_container_width=True makes it fill the card width
                            st.image(image_url, use_container_width=True)
                        except Exception:
                            # If the image fails to load (URL broken, etc.),
                            # show a house emoji as a placeholder
                            st.markdown("🏠 _Image not available_")
                    else:
                        # No image URL provided — show placeholder
                        st.markdown("🏠")

                    # ── LISTING TITLE ───────────────────────────────────────
                    title = listing.get("title", "Property listing")
                    # Truncate very long titles to keep cards a consistent size
                    if len(title) > 70:
                        title = title[:67] + "..."
                    st.markdown(f"**{title}**")

                    # ── PRICE ───────────────────────────────────────────────
                    price = listing.get("price", "")
                    if price:
                        st.markdown(f"💰 **{price}**")

                    # ── AREA / LOCATION ─────────────────────────────────────
                    area = listing.get("area", "")
                    if area:
                        st.markdown(f"📍 {area}")

                    # ── LINK BUTTON ─────────────────────────────────────────
                    url = listing.get("url", "#")
                    # st.link_button() creates a button that opens a URL in a new tab
                    st.link_button(
                        "View full listing ↗",
                        url,
                        use_container_width=True  # Stretch button to card width
                    )
