import streamlit as st
import geocoder
from datetime import datetime

# Function to determine the current season based on the month
def get_current_season():
    # Get the current month
    month = datetime.now().month
    # Define seasons based on the month (Northern Hemisphere)
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

def login_page():
    st.title("Login Page")

    if "username" not in st.session_state:
        st.session_state["username"] = None

    if "password" not in st.session_state:
        st.session_state["password"] = None

    if "location_granted" not in st.session_state:
        st.session_state["location_granted"] = False

    if st.session_state["username"] is None:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "aa" and password == "aa":
                st.session_state["username"] = username
                st.session_state["password"] = password
                st.session_state["location_granted"] = False  # Location is initially not granted
                st.success("Login successful!")
                st.rerun()  # Refresh the page to navigate
            else:
                st.error("Invalid credentials")

    if st.session_state["username"] is not None:
        # Attempt to get user location based on IP (only if not already granted)
        if not st.session_state["location_granted"]:
            g = geocoder.ip("me")  # Get GPS location based on IP
            if g.ok:
                st.session_state["location_granted"] = True
                st.session_state["country"] = g.country
                st.success(f"Location access granted! Your country: {st.session_state['country']}")
                
                # Get current season based on the user's location
                season = get_current_season()
                st.session_state["season"] = season
                st.success(f"The current season in your location is: {season}")
            else:
                st.error("Unable to fetch your location. Please try again.")

        if st.session_state["location_granted"]:
            st.session_state["page"] = "dashboard"
            st.rerun()
