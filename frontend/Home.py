#frontend/Home.py

import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Client Sentiment Analysis", layout="wide")

# --- Title ---
st.title("📧 Client Sentiment Analysis Dashboard")

# --- Intro ---
st.subheader("Welcome to the Client Sentiment Analysis Dashboard.")
st.write("""
This system analyzes incoming emails using an ML model, stores results, and provides insights into client sentiment.
""")

# --- Feature List ---
st.subheader("🔍 What You Can Do Here:")
st.markdown("""
- *Fetch and Analyze* client emails  
- *View Sentiment Scores*  
- *Visualize Trends*  
""")

# --- Navigation Button ---
if st.button("🚀 Start Analysis"):
    st.switch_page("pages/1_StorePage.py")  # Switches to the analysis page