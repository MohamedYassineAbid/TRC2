import streamlit as st
from login import login_page
from dashboard import dashboard_page
from monitoring import monitoring_page

# Main function to handle page navigation
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "dashboard":
        dashboard_page()
    elif st.session_state["page"] == "monitoring":
        monitoring_page()

if __name__ == "__main__":
    main()
