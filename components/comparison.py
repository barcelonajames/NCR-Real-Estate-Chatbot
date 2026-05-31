# components/comparison.py
# PURPOSE: Shows a side-by-side comparison of two or more properties or areas.
#
# Used when the user asks questions like:
#   "Which is better: condo in Mandaluyong or townhouse in Pasig?"
#   "Compare BGC vs Ortigas for a young professional"
#
# Each option gets its own column with key stats, pros, and cons.
#
# NO API KEYS NEEDED — pure Streamlit display.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import streamlit as st


def render_comparison(items: list):
    """
    Displays a side-by-side comparison of properties or areas.

    Parameters:
    - items: list of dicts, each representing one option.
      Each dict should have:
      - label (str): the name of the option
      - price_php (int): monthly rent or purchase price
      - sqm (int): floor area in square meters
      - tmc_php (int): estimated True Monthly Cost
      - pros (list of str): advantages
      - cons (list of str): disadvantages
    """

    st.subheader("Side-by-side comparison")
    st.caption("Tap any column to explore further in the chat.")

    if not items:
        st.write("No items to compare.")
        return

    # Create one column per option
    # st.columns(n) splits the page into n equal columns
    cols = st.columns(len(items))

    for i, item in enumerate(items):
        with cols[i]:
            # ── OPTION HEADER ──────────────────────────────────────────────
            label = item.get("label", f"Option {i + 1}")
            st.markdown(f"### {label}")

            # ── KEY METRICS ────────────────────────────────────────────────
            rent = item.get("price_php", 0)
            sqm = item.get("sqm", 0)
            tmc = item.get("tmc_php", 0)

            if rent > 0:
                st.metric("Monthly rent", f"₱{rent:,.0f}")

            if sqm > 0:
                st.metric("Floor area", f"{sqm} sqm")

            if tmc > 0 and rent > 0:
                # Show TMC with the hidden gap as a delta
                hidden = tmc - rent
                st.metric(
                    "True Monthly Cost",
                    f"₱{tmc:,.0f}",
                    delta=f"+₱{hidden:,.0f} hidden" if hidden > 0 else None,
                    delta_color="inverse"  # Red = higher cost = not ideal
                )

            st.divider()

            # ── PROS ────────────────────────────────────────────────────────
            pros = item.get("pros", [])
            if pros:
                st.markdown("**✅ Advantages**")
                for pro in pros:
                    st.markdown(f"- {pro}")

            # ── CONS ────────────────────────────────────────────────────────
            cons = item.get("cons", [])
            if cons:
                st.markdown("**❌ Disadvantages**")
                for con in cons:
                    st.markdown(f"- {con}")
