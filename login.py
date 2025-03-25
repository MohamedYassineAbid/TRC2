import streamlit as st
import geocoder

def login_page():
    st.title("Login Page")

    if "username" not in st.session_state:
        st.session_state["username"] = None

    if "password" not in st.session_state:
        st.session_state["password"] = None

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
            else:
                st.error("Unable to fetch your location. Please try again.")

        if st.session_state["location_granted"]:
            st.session_state["page"] = "dashboard"
            st.rerun()
