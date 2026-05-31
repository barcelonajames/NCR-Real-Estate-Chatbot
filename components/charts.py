# components/charts.py
# PURPOSE: Shows interactive price trend charts using Plotly.
#
# Used when the user asks about:
#   - Price history ("How have BGC condo prices changed?")
#   - Market forecasts ("Is now a good time to buy in Pasig?")
#   - Price comparisons over time between two areas
#
# Plotly creates interactive charts — users can hover over data points,
# zoom in, and download the chart as an image.
#
# NO API KEYS NEEDED — pure Plotly + Streamlit display.
# WHO OWNS THIS FILE: Member 1 (Frontend)

import streamlit as st
import plotly.graph_objects as go  # For creating chart figures and traces


def render_chart(chart_data: dict):
    """
    Displays a Plotly line chart for price trends.

    Parameters:
    - chart_data: dict with two keys:
      - "labels": list of x-axis labels (e.g., years or quarters)
      - "series": list of dicts, each representing one line on the chart
                  Each series has "name" (legend label) and "values" (y-axis data)

    Example chart_data:
    {
        "labels": ["2021", "2022", "2023", "2024"],
        "series": [
            {"name": "BGC Condo (₱/sqm)", "values": [165000, 180000, 195000, 210000]},
            {"name": "Pasig Condo (₱/sqm)", "values": [120000, 130000, 145000, 158000]}
        ]
    }
    """

    labels = chart_data.get("labels", [])
    series = chart_data.get("series", [])

    # If there's no data, show a message instead of an empty chart
    if not labels or not series:
        st.info("No chart data is available for this query.")
        return

    st.subheader("Price trend chart")

    # ── CREATE THE CHART ──────────────────────────────────────────────────
    # go.Figure() is an empty chart canvas
    fig = go.Figure()

    # Add one LINE per series (each series = one area or property type)
    for s in series:
        fig.add_trace(go.Scatter(
            x=labels,
            y=s.get("values", []),
            mode="lines+markers",  # Show both the line AND dots at each data point
            name=s.get("name", "Price"),
            line=dict(width=2.5)   # Line thickness
        ))

    # ── STYLE THE CHART ───────────────────────────────────────────────────
    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Price (₱)",
        yaxis=dict(tickformat=",.0f"),  # Format y-axis as "180,000" not "180000"
        hovermode="x unified",          # When hovering, show ALL series values at that x-point
        height=380,
        margin=dict(t=20, b=40, l=60, r=20),
        legend=dict(
            orientation="h",    # Horizontal legend (displays below the chart)
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    # Display the chart in Streamlit at full container width
    st.plotly_chart(fig, use_container_width=True)
