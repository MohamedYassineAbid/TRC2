import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
from io import StringIO

np.random.seed(42)

# Crop thresholds (as above)
crop_thresholds = {
    "Rice":  {"Temp_max": 35, "Humidity_min": 60, "pH_min": 5.5, "pH_max": 7,   "N_min": 40, "K_min": 40, "Rain_min": 150},
    "Wheat": {"Temp_max": 30, "Humidity_min": 50, "pH_min": 6,   "pH_max": 7.5, "N_min": 35, "K_min": 38, "Rain_min": 100},
    "Maize": {"Temp_max": 32, "Humidity_min": 55, "pH_min": 5.8, "pH_max": 7,   "N_min": 50, "K_min": 45, "Rain_min": 120},
    "Barley":{"Temp_max": 28, "Humidity_min": 40, "pH_min": 6,   "pH_max": 7.5, "N_min": 30, "K_min": 35, "Rain_min": 80}
}

selected_crop = "Wheat"
time_series = np.arange(1, 25)

def generate_realistic_data(crop):
    base = crop_thresholds[crop]
    return {
        "N": np.random.normal(loc=base["N_min"] + 20, scale=10, size=24).clip(base["N_min"] - 5, 140),
        "P": np.random.normal(loc=70, scale=15, size=24).clip(5, 150),
        "K": np.random.normal(loc=base["K_min"] + 20, scale=6, size=24).clip(base["K_min"] - 5, 210),
        "Temperature": np.random.normal(loc=base["Temp_max"] - 3, scale=2, size=24).clip(15, 40),
        "Humidity": np.random.normal(loc=base["Humidity_min"] + 10, scale=7, size=24).clip(30, 90),
        "pH": np.random.normal(loc=(base["pH_min"] + base["pH_max"]) / 2, scale=0.3, size=24).clip(4.5, 8),
        "Rainfall": np.random.normal(loc=base["Rain_min"] + 30, scale=20, size=24).clip(20, 300)
    }

def check_alerts_at_hour(hour, data, crop):
    thresholds = crop_thresholds[crop]
    alerts = []
    treatments = []
    if data["Temperature"][hour] > thresholds["Temp_max"]:
        alerts.append(f"🔥 High Temp ({data['Temperature'][hour]:.1f}°C)")
        treatments.append("✅ Shade crops and use cooling systems.")
    if data["Humidity"][hour] < thresholds["Humidity_min"]:
        alerts.append(f"💧 Low Humidity ({data['Humidity'][hour]:.1f}%)")
        treatments.append("✅ Irrigate plants or increase humidity with misting systems.")
    if data["pH"][hour] < thresholds["pH_min"]:
        alerts.append(f"⚠️ pH too low ({data['pH'][hour]:.2f})")
        treatments.append("✅ Apply pH-raising amendments like lime.")
    if data["pH"][hour] > thresholds["pH_max"]:
        alerts.append(f"⚠️ pH too high ({data['pH'][hour]:.2f})")
        treatments.append("✅ Apply pH-lowering amendments like sulfur.")
    if data["N"][hour] < thresholds["N_min"]:
        alerts.append(f"🌱 Low Nitrogen ({int(data['N'][hour])})")
        treatments.append("✅ Apply nitrogen-rich fertilizers.")
    if data["K"][hour] < thresholds["K_min"]:
        alerts.append(f"🌿 Low Potassium ({int(data['K'][hour])})")
        treatments.append("✅ Apply potassium fertilizers.")
    if data["Rainfall"][hour] < thresholds["Rain_min"]:
        alerts.append(f"🌧 Low Rainfall ({data['Rainfall'][hour]:.1f} mm)")
        treatments.append("✅ Increase irrigation or use water-saving techniques.")
    return alerts, treatments

# Streamlit monitoring page
def monitoring_page():
    # Header
    st.title("Crop Monitoring Dashboard")

    # Select crop
    selected_crop = st.selectbox("Select Crop", ["Rice", "Wheat", "Maize", "Barley"])

    # Generate data
    data = generate_realistic_data(selected_crop)
    alerts_over_time = {}
    treatments_over_time = {}
    for hour in range(24):
        alerts, treatments = check_alerts_at_hour(hour, data, selected_crop)
        if alerts:
            alerts_over_time[hour + 1] = alerts
            treatments_over_time[hour + 1] = treatments
    
    # Display the alerts if any
    st.subheader("Alert Log")
    if alerts_over_time:
        for hour, alerts in alerts_over_time.items():
            st.markdown(f"**[Hour {hour}]**")
            for alert in alerts:
                st.markdown(f"   ➤ {alert}")
            st.write("-" * 50)
    else:
        st.markdown("✅ All environmental conditions were optimal for the entire 24 hours ✅")
    
    # 📈 Start Visualizing Each Feature Differently
    st.subheader("Environmental Factors")

    # Plot nitrogen levels
    st.subheader("Nitrogen Levels")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_series, data["N"], marker='o', color='green')
    ax.set_title("Nitrogen Levels")
    ax.set_xlabel("Hour")
    ax.set_ylabel("N")
    ax.grid(True)
    st.pyplot(fig)

    # Plot phosphorus levels
    st.subheader("Phosphorus Levels")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(time_series, data["P"], color='orange')
    ax.set_title("Phosphorus Levels")
    ax.set_xlabel("Hour")
    ax.set_ylabel("P")
    st.pyplot(fig)

    # Plot potassium levels
    st.subheader("Potassium Levels")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_series, data["K"], color='purple', marker='o', linestyle='-')
    ax.set_title("Potassium Levels")
    ax.set_xlabel("Hour")
    ax.set_ylabel("K")
    ax.grid(True)
    st.pyplot(fig)

    # Plot temperature with threshold
    st.subheader("Temperature Variation with Threshold")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_series, data["Temperature"], color='red', label='Temperature')
    ax.axhline(y=crop_thresholds[selected_crop]['Temp_max'], color='black', linestyle='--', label='Temp Threshold')
    ax.fill_between(time_series, data["Temperature"], crop_thresholds[selected_crop]['Temp_max'], where=(data["Temperature"] > crop_thresholds[selected_crop]['Temp_max']), color='red', alpha=0.3)
    ax.set_title("Temperature Variation with Threshold")
    ax.set_xlabel("Hour")
    ax.set_ylabel("°C")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Plot humidity
    st.subheader("Humidity Over Time")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.step(time_series, data["Humidity"], color='blue', where='mid')
    ax.set_title("Humidity Over Time")
    ax.set_xlabel("Hour")
    ax.set_ylabel("% Humidity")
    st.pyplot(fig)

    # Plot pH levels
    st.subheader("pH Level Changes")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_series, data["pH"], color='brown')
    ax.fill_between(time_series, data["pH"], color='brown', alpha=0.3)
    ax.set_title("pH Level Changes")
    ax.set_xlabel("Hour")
    ax.set_ylabel("pH")
    st.pyplot(fig)

    # Plot rainfall
    st.subheader("Rainfall Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(time_series, data["Rainfall"], color='skyblue')
    ax.set_title("Rainfall Distribution")
    ax.set_xlabel("Rainfall (mm)")
    ax.set_ylabel("Hour")
    st.pyplot(fig)

    # Create a CSV for the alert report
    def create_alert_report(alerts_over_time, treatments_over_time):
        report = []
        for hour in range(1, 25):
            if hour in alerts_over_time:
                for alert, treatment in zip(alerts_over_time[hour], treatments_over_time[hour]):
                    report.append([hour, alert, treatment])
        return pd.DataFrame(report, columns=["Hour", "Alert", "Treatment"])

    # Generate the alert report
    alert_report = create_alert_report(alerts_over_time, treatments_over_time)

    # Add download button for alert report (CSV)
    csv_alert_report = alert_report.to_csv(index=False)
    st.download_button(
        label="Download Alert Report (CSV)",
        data=csv_alert_report,
        file_name="crop_alert_report.csv",
        mime="text/csv"
    )

# Main execution
if __name__ == "__main__":
    monitoring_page()
