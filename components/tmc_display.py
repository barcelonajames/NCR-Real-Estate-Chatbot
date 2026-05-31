# components/tmc_display.py
# PURPOSE: Shows the True Monthly Cost (TMC) breakdown — the chatbot's signature feature.
#
# The TMC reveals the REAL monthly cost of living somewhere, beyond just rent.
# It includes utilities, transport, commute time, and renovation costs.
# The "hidden gap" is the difference between advertised rent and actual TMC.
#
# NO API KEYS NEEDED — pure Streamlit + Plotly display.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import streamlit as st
import plotly.graph_objects as go  # For building the comparison bar chart


def render_tmc(breakdown: dict):
    """
    Displays the True Monthly Cost breakdown with metrics and a visual chart.

    Parameters:
    - breakdown: dict with these keys (all values in ₱):
      housing, utilities, transport, time_cost, spec_gap,
      total_tmc, advertised, hidden_gap
    """

    st.subheader("True Monthly Cost breakdown")
    st.caption(
        "The real all-in monthly cost — not just the advertised rent. "
        "Cheap rent doesn't always mean cheaper living."
    )

    # ── KEY COMPARISON METRICS ─────────────────────────────────────────────
    # Show the two most important numbers side by side:
    # "What the ad says" vs "What you'll actually pay"
    advertised = breakdown.get("advertised", 0)
    total_tmc = breakdown.get("total_tmc", 0)
    hidden_gap = breakdown.get("hidden_gap", max(0, total_tmc - advertised))

    col1, col2 = st.columns(2)

    with col1:
        # st.metric() creates a clean stat card with a label and value
        st.metric(
            label="Advertised monthly rent",
            value=f"₱{advertised:,.0f}"
        )

    with col2:
        st.metric(
            label="True Monthly Cost",
            value=f"₱{total_tmc:,.0f}",
            # delta shows the DIFFERENCE as a sub-value
            # "inverse" color = red because higher cost is worse for the user
            delta=f"+₱{hidden_gap:,.0f} in hidden costs",
            delta_color="inverse"
        )

    st.divider()

    # ── COST COMPONENT TABLE ──────────────────────────────────────────────
    # Break down each category of cost so the user understands WHERE the money goes
    st.markdown("**Cost breakdown:**")

    cost_items = [
        ("🏠 Housing", "Rent or mortgage amortisation + condo dues", breakdown.get("housing", 0)),
        ("⚡ Utilities", "Electricity + water + internet", breakdown.get("utilities", 0)),
        ("🚗 Transport", "Fuel + toll + parking + vehicle maintenance", breakdown.get("transport", 0)),
        ("⏱️ Time cost", "Commute hours per month × your hourly income rate", breakdown.get("time_cost", 0)),
        ("🔧 Renovation gap", "Renovation budget amortised over 36 months", breakdown.get("spec_gap", 0)),
    ]

    # Only show cost items that are greater than zero
    # (Some properties have no spec_gap, for example)
    for emoji_label, description, value in cost_items:
        if value > 0:
            row_cols = st.columns([2, 2, 1])
            row_cols[0].write(emoji_label)
            row_cols[1].write(f"_{description}_")
            row_cols[2].write(f"**₱{value:,.0f}**")

    st.divider()

    # Total row (bold, prominent)
    total_cols = st.columns([2, 2, 1])
    total_cols[0].write("**TOTAL TRUE MONTHLY COST**")
    total_cols[2].write(f"**₱{total_tmc:,.0f}**")

    # ── BAR CHART ─────────────────────────────────────────────────────────
    # Visual comparison — makes the gap immediately obvious
    if total_tmc > 0 and advertised > 0:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=["Advertised rent", "True Monthly Cost"],
            y=[advertised, total_tmc],
            marker_color=["#4A86C8", "#FF4B4B"],  # Blue for advertised, red for TMC
            # text= labels the bar tops with the actual values
            text=[f"₱{advertised:,.0f}", f"₱{total_tmc:,.0f}"],
            textposition="outside",
            width=0.5  # Narrower bars look cleaner
        ))

        fig.update_layout(
            title="Advertised rent vs True Monthly Cost",
            yaxis_title="₱ per month",
            yaxis=dict(tickformat=",.0f"),  # Format y-axis numbers with commas
            showlegend=False,
            height=320,
            margin=dict(t=50, b=30, l=60, r=20)
        )

        st.plotly_chart(fig, use_container_width=True)
