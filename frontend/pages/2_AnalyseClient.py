#frontend/pages/2_AnalyseClient.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
from database import get_sentiment_trend, get_sentiment_details

st.set_page_config(page_title="Analyse Client", layout="wide")
st.page_link("pages/1_StorePage.py", label="⬅ Back to Clients", icon="👥")

# --- Session Fallback ---
if "selected_user" not in st.session_state:
    st.warning("⚠ No client selected.")
    st.stop()

user = st.session_state["selected_user"]
email = user["email"]
client_name = user["name"]

st.title(f"📊 Sentiment Analysis for {client_name}")
st.write(f"📧 Email: {email}")

# --- Fetch Sentiment Data ---
raw_data = get_sentiment_trend(email)
if not raw_data:
    st.info("No sentiment data available for this client yet.")
    st.stop()

df = pd.DataFrame(raw_data)
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# --- Display Net Sentiment Score ---
score_colors = {-3: "red", 0.5: "orange", 1: "gray", 2: "green"}
net_score = round(df["score"].sum(), 2)
progress_percent = min(abs(net_score), 50) / 50
progress_color = "red" if net_score < 0 else "blue"

st.markdown("### 🧠 Total Sentiment Score")
st.markdown(f"""
<div style="background-color: #eee; height: 24px; width: 100%; border-radius: 8px; overflow: hidden;">
  <div style="
    width: {progress_percent * 100}% ;
    background-color: {progress_color};
    height: 100%;
  ">
  </div>
</div>
<div style="margin-top: 8px; font-weight: bold; font-size: 16px;">
  Net Sentiment Score: {net_score}
</div>
""", unsafe_allow_html=True)


# --- Create Plot ---
fig = go.Figure()

# Add line segments
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["datetime"][i], df["datetime"][i + 1]],
        y=[df["score"][i], df["score"][i + 1]],
        mode="lines",
        line=dict(color=score_colors.get(df["score"][i + 1], "gray"), width=3),
        hoverinfo="skip",
        showlegend=False
    ))

# Add markers
for i in range(len(df)):
    point = df.iloc[i]
    fig.add_trace(go.Scatter(
        x=[point["datetime"]],
        y=[point["score"]],
        mode='markers',
        marker=dict(size=12, color=score_colors.get(point["score"], "gray"), line=dict(width=2, color='black')),
        hovertemplate='Time: %{x|%Y-%m-%d %H:%M:%S}<br>Score: %{y}<extra></extra>',
        showlegend=False
    ))

fig.update_layout(
    title="📈 Sentiment Score Over Time (Click a point)",
    xaxis_title="Date & Time",
    yaxis_title="Sentiment Score",
    yaxis=dict(range=[-3.5, 2.5], dtick=0.5),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(size=14),
    title_x=0.5
)

# --- Plot & Click ---
clicked_points = plotly_events(fig, click_event=True, hover_event=False, override_height=500)

if clicked_points:
    clicked_time = clicked_points[0]["x"]  # Can be '2025-06-24 13:05' or '2025-06-24 13:05:00'

    # Ensure full seconds format for matching
    if len(clicked_time.strip().split(':')) == 2:
        clicked_time += ":00"

    detail = get_sentiment_details(email, clicked_time)

    if detail:
        st.markdown(f"### 📨 Summary for {clicked_time}")
        st.markdown(f"- *Subject:* {detail['subject']}")
        st.markdown(f"- *Sentiment Score:* {detail['sentiment_score']}")
        st.markdown(f"- *Summary:* {detail['summary']}")
        st.markdown(f"- *Action:* {detail['action']}")
    else:
        st.warning("⚠ No matching record found for that message.")