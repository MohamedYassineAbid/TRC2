import streamlit as st

def monitoring_page():
    if "crop_recommendation" not in st.session_state:
        st.warning("Please get a crop recommendation first!")
        return

    st.title(f"Monitoring for {st.session_state['crop_recommendation']}")
    st.write("Monitor real-time sensor data and performance of the recommended crop.")

    # Here you can add real-time data or monitoring features
    st.write("Real-time monitoring of the crop will be displayed here.")
