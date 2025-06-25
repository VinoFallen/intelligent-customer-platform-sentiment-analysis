import streamlit as st
import requests

st.title("Client Email Dashboard")

if st.button("Check Health"):
    try:
        res = requests.get("https://intelligent-customer-platform-sentiment.onrender.com/health")
        st.success(res.json())
    except:
        st.error("Backend not reachable.")
