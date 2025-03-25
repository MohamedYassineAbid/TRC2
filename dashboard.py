import joblib
import streamlit as st
import pickle
import numpy as np

# Load the trained model
model_path = "model/model.pkl"
scaler_path = "model/scaler.pkl"  # Path to your scaler file


scaler = joblib.load(scaler_path)

# Load the model
model = joblib.load(model_path)

# Function to predict the sorted fruits
def predict_sorted_fruits(model, scaler, sample_input):
    # Ensure the input is in the correct shape (2D array)
    sample_input = np.array(sample_input).reshape(1, -1)
    
    try:
        # Scale the input using the loaded scaler
        sample_input_scaled = scaler.transform(sample_input)
    except Exception as e:
        st.error(f"Error during scaling: {e}")
        return [], []

    # Get prediction probabilities
    probabilities = model.predict_proba(sample_input_scaled)[0]
    class_labels = model.classes_

    # Sort the probabilities in descending order
    sorted_indices = np.argsort(probabilities)[::-1]
    sorted_fruits = [class_labels[i] for i in sorted_indices]
    sorted_probs = [probabilities[i] for i in sorted_indices]

    return sorted_fruits, sorted_probs

# Function to predict the best crop
def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    input_features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    sorted_fruits, sorted_probs = predict_sorted_fruits(model, scaler, input_features)
    return sorted_fruits, sorted_probs

def dashboard_page():
    if "location_granted" not in st.session_state:
        st.error("Please login first!")
        return
    
    st.title("Crop Recommendation Dashboard")
    st.write("Input your field data to get the best crop recommendation.")

    # Take user inputs
    N = st.number_input("Nitrogen (N)", min_value=0, max_value=200, value=50)
    P = st.number_input("Phosphorus (P)", min_value=0, max_value=200, value=50)
    K = st.number_input("Potassium (K)", min_value=0, max_value=200, value=50)
    temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0, value=25.0)
    humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=60)
    ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5)
    rainfall = st.number_input("Rainfall (mm)", min_value=0, max_value=300, value=100)

    # Predict the best crop when user submits
    if st.button("Get Crop Recommendation"):
        sorted_fruits, sorted_probs = predict_crop(N, P, K, temperature, humidity, ph, rainfall)
        
        # Display the top recommendations
        st.write("**Top 5 Recommended Crops**:")
        for i in range(5):
            st.write(f"{sorted_fruits[i]}: {sorted_probs[i]:.2f}")

        # Show a bar chart for better visualization (optional)
        st.bar_chart(sorted_probs)  # Display the probabilities as a bar chart

    # Navigation to the monitoring page
    if st.button("Go to Monitoring"):
        st.session_state["crop_recommendation"] = sorted_fruits[0]  # Store the top recommendation
