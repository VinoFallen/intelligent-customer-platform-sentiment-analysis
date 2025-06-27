#frontend/pages/1_StorePage.py

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from database import get_all_users

st.set_page_config(page_title="Client List", layout="wide")

# Optionally show back button
st.page_link("Home.py", label="⬅ Back to Home")

# Call the display function

def display():
    count = st_autorefresh(interval=5000, limit=None, key="refresh_counter")

    st.title("👥 Client List")
    

    # Get newly fetched users
    new_users = get_all_users()

    # Initialize session state to store all seen users
    if "all_seen_users" not in st.session_state:
        st.session_state["all_seen_users"] = []

    image_path = "image.png"
    

    # Merge new users with previously seen users, avoiding duplicates
    existing_emails = {u["email"] for u in st.session_state["all_seen_users"]}
    for user in new_users:
        if user["email"] not in existing_emails:
            st.session_state["all_seen_users"].append(user)
            existing_emails.add(user["email"])

    users_to_display = st.session_state["all_seen_users"]

    # Initialize selected user state
    if "selected_user" not in st.session_state:
        st.session_state["selected_user"] = None

    # Show users in 2-column layout
    for i in range(0, len(users_to_display), 2):
        col1, col2 = st.columns(2)

        with col1:
            user = users_to_display[i]
            st.image(image_path, width=80)

            st.subheader(user["name"])
            st.write(f"📧 {user['email']}")
            if st.button(f"Analyse {user['name']}", key=f"btn_{i}"):
                st.session_state["selected_user"] = user
                st.success(f"Selected: {user['name']}")
                st.switch_page("pages/2_AnalyseClient.py") 

        if i + 1 < len(users_to_display):
            with col2:
                user = users_to_display[i + 1]
                st.image(image_path, width=80)

                st.subheader(user["name"])
                st.write(f"📧 {user['email']}")
                if st.button(f"Analyse {user['name']}", key=f"btn_{i+1}"):
                    st.session_state["selected_user"] = user
                    st.success(f"Selected: {user['name']}")
                    st.switch_page("pages/2_AnalyseClient.py")
              
      
display()