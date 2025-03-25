import joblib
import streamlit as st
import numpy as np
import google.generativeai as genai
import pandas as pd
import plotly.express as px
from monitoring import monitoring_page 
# Configure API Key (Replace with your actual API key)
genai.configure(api_key="AIzaSyCiHV1nUw9QBn5iwv6JNU7k9YgTpOSlIvk")

# Load the trained model
model_path = "model/model.pkl"
scaler_path = "model/scaler.pkl"  # Path to your scaler file

scaler = joblib.load(scaler_path)
model = joblib.load(model_path)

# Function to predict the sorted fruits
def predict_sorted_fruits(model, scaler, sample_input):
    sample_input = np.array(sample_input).reshape(1, -1)
    
    try:
        sample_input_scaled = scaler.transform(sample_input)
    except Exception as e:
        st.error(f"Error during scaling: {e}")
        return [], []

    probabilities = model.predict_proba(sample_input_scaled)[0]
    class_labels = model.classes_

    sorted_indices = np.argsort(probabilities)[::-1]
    sorted_fruits = [class_labels[i] for i in sorted_indices]
    sorted_probs = [probabilities[i] for i in sorted_indices]

    return sorted_fruits, sorted_probs

# Function to predict the best crop
def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    input_features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    sorted_fruits, sorted_probs = predict_sorted_fruits(model, scaler, input_features)
    return sorted_fruits, sorted_probs

# Function to get seasonal crops using Gemini API
def get_seasonal_crops(location, season):
    prompt = f"""
    Based on historical agricultural and market demand trends,
    what are the most in-demand crops for {season} in {location}?
    Focus on crops that are popular in local markets and suitable for cultivation.
    Return a list of 5-10 crops.
    Only provide a comma-separated list of names with no numbers or extra text.
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    crops = response.text.strip()
    crop_list = [(crop.strip()).lower() for crop in crops.split(",")]

    return crop_list

# Function to recommend alternative crops if no match found
def get_alternative_crops(N, P, K, temperature, humidity, ph, rainfall):
    prompt = f"""
    Given the following field conditions:
    Nitrogen: {N}, Phosphorus: {P}, Potassium: {K}, Temperature: {temperature}°C, 
    Humidity: {humidity}%, pH: {ph}, Rainfall: {rainfall}mm,
    suggest alternative crops that might grow well based on these conditions. 
    Focus on crops that are suitable for these conditions and are in-demand in local markets.
    Return a list of 5-10 crops.
    Only provide a comma-separated list of names with no numbers or extra text.
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    crops = response.text.strip()
    crop_list = [(crop.strip()).lower() for crop in crops.split(",")]

    return crop_list

# Function to provide treatment advice for crops based on input conditions
def get_crop_treatment(crop):
    treatments = {
        'rice': "Rice requires flooded conditions. Ensure good water availability and pH levels of 5.5–7.0.",
        'maize': "Maize needs a well-drained soil and prefers temperatures between 18–30°C. Keep the soil pH between 5.8 and 7.0.",
        'chickpea': "Chickpeas thrive in well-drained soil with moderate rainfall and prefer a pH between 6.0 and 8.0.",
        'kidneybeans': "Kidney beans require a warm climate with temperatures between 20–30°C. The soil should be well-drained.",
        'pigeonpeas': "Pigeon peas prefer a tropical climate and well-drained soil with a pH between 6.0 and 7.5.",
        'mothbeans': "Moth beans grow best in hot and dry climates. The soil should be sandy and well-drained.",
        'mungbean': "Mung beans thrive in warm temperatures of 25–35°C with moderate rainfall and soil pH of 6.0–7.5.",
        'blackgram': "Blackgram requires a warm climate with temperatures between 25–30°C. The soil should be well-drained.",
        'lentil': "Lentils prefer cool conditions with temperatures around 15°C and a soil pH of 6.0–7.0.",
        'pomegranate': "Pomegranate requires a hot, dry climate with temperatures above 35°C. Ensure well-drained soil.",
        'banana': "Bananas need a warm and humid climate with temperatures between 25–30°C. The soil should be rich in organic matter.",
        'mango': "Mangoes prefer tropical climates with temperatures above 25°C. Ensure well-drained, fertile soil.",
        'grapes': "Grapes thrive in warm and dry climates with temperatures between 25–30°C and well-drained soil.",
        'watermelon': "Watermelon prefers warm conditions with temperatures between 24–30°C and needs plenty of water.",
        'muskmelon': "Muskmelons thrive in warm, dry climates. Ensure soil is well-drained and pH is between 6.0–7.5.",
        'apple': "Apple trees prefer cool climates with temperatures around 20°C and well-drained soil.",
        'orange': "Oranges require warm climates and well-drained, sandy soil with a pH of 6.0–7.5.",
        'papaya': "Papayas require a tropical climate with temperatures between 25–30°C and well-drained soil.",
        'coconut': "Coconuts grow in tropical climates with temperatures around 27°C. Ensure high humidity and sandy soil.",
        'cotton': "Cotton requires a hot, dry climate with temperatures between 21–30°C and well-drained soil.",
        'jute': "Jute thrives in warm, humid climates and requires plenty of water and a pH of 6.0–7.0.",
        'coffee': "Coffee grows best in a cool, tropical climate with temperatures between 15–25°C and acidic, well-drained soil."
    }
    
    return treatments.get(crop.lower(), "Treatment information is not available for this crop.")


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
    finallist,sorted_fruits=[],[]
    # Predict the best crop when user submits
    if st.button("Get Crop Recommendation"):
        sorted_fruits, suitability_scores = predict_crop(N, P, K, temperature, humidity, ph, rainfall)
        
        # Get the current season and location
        season = "summer"
        location = "morroco"

        # Get seasonal crop recommendations from Gemini API
        recommended_crops = get_seasonal_crops(location, season)

        # Filter the recommended crops from the sorted fruits
        finallist = [item for item in sorted_fruits if item in recommended_crops]

        if finallist:
            # Prepare data for visualization
            crop_data = pd.DataFrame({
                "Crop": finallist[:10],  # Top 5 crops
                "Suitability": [suitability_scores[sorted_fruits.index(crop)] for crop in finallist[:5]]  # Matching scores
            })
            # Create bar chart
            fig = px.bar(crop_data, x="Crop", y="Suitability", title="Top Recommended Crops", color="Crop",
             labels={"Suitability": "Suitability Score"})
            fig.update_layout(yaxis_title=None)
# Show the plot
            st.plotly_chart(fig)

            # Display cultivation advice for the crops in the final list
            st.subheader("Cultivation Advice for Recommended Crops")
            for crop in finallist[:5]:  # Display the top 5 crops
                st.markdown(f"### {crop.capitalize()}")
                st.write(get_crop_treatment(crop))
        else:
            st.warning(f"No suitable crops found for {location} based on the given data input.")
            
            # Provide environmental adaptation advice
            st.subheader("Environmental Adaptation Recommendations")
            adaptation_tips = get_environment_adaptation(N, P, K, temperature, humidity, ph, rainfall)
            st.write(adaptation_tips)

    # Navigation to the monitoring page
    if st.button("Go to Monitoring"):
        monitoring_page() # Warn the user if both lists are empty



# Example helper function to generate environmental adaptation tips
def get_environment_adaptation(N, P, K, temperature, humidity, ph, rainfall):
    adaptation_tips = []
    if ph < 6.0:
        adaptation_tips.append("Add lime to the soil to increase pH.")
    elif ph > 7.5:
        adaptation_tips.append("Add sulfur or organic matter to reduce pH.")

    if N < 50:
        adaptation_tips.append("Increase nitrogen levels using urea or compost.")
    if P < 30:
        adaptation_tips.append("Use phosphorus-rich fertilizers like DAP.")
    if K < 40:
        adaptation_tips.append("Apply potassium sulfate or potash.")

    if temperature < 15:
        adaptation_tips.append("Consider greenhouse techniques to maintain optimal temperature.")
    if humidity < 40:
        adaptation_tips.append("Implement irrigation or misting systems to increase humidity.")

    if not adaptation_tips:
        adaptation_tips.append("Your environment is generally suitable, but consider seasonal factors.")

    return "\n".join(adaptation_tips)
