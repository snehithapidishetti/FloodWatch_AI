import streamlit as st
import pandas as pd
import joblib
import requests
import os
import folium

from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium


# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


# -----------------------------
# Page settings
# -----------------------------

st.set_page_config(
    page_title="FloodWatch AI",
    page_icon="🌊",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("🌊 FloodWatch AI")
st.subheader("AI-Based Flood Risk Prediction and Alert System")

st.divider()


# -----------------------------
# Location
# -----------------------------

st.header("📍 Location")

location = st.text_input(
    "Enter your location",
    "Hyderabad"
)


# -----------------------------
# Weather API
# -----------------------------

if st.button("🌦️ Get Current Weather"):

    if not API_KEY:
        st.error("OpenWeather API key not found in .env file.")

    else:

        try:

            url = "https://api.openweathermap.org/data/2.5/weather"

            params = {
                "q": location,
                "appid": API_KEY,
                "units": "metric"
            }

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            if response.status_code == 200:

                weather = response.json()

                temperature = weather["main"]["temp"]
                humidity = weather["main"]["humidity"]
                wind_speed = weather["wind"]["speed"]

                rainfall = weather.get(
                    "rain",
                    {}
                ).get(
                    "1h",
                    0
                )

                weather_description = weather["weather"][0]["description"]

                st.success(
                    f"✅ Weather data loaded for {location}"
                )

                # Weather cards
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "🌡️ Temperature",
                        f"{temperature} °C"
                    )

                with col2:
                    st.metric(
                        "💧 Humidity",
                        f"{humidity} %"
                    )

                with col3:
                    st.metric(
                        "🌧️ Rainfall",
                        f"{rainfall} mm"
                    )

                with col4:
                    st.metric(
                        "💨 Wind Speed",
                        f"{wind_speed} m/s"
                    )

                st.info(
                    f"Current weather: {weather_description.title()}"
                )

                # Save weather values
                st.session_state["rainfall"] = rainfall
                st.session_state["humidity"] = humidity

            else:

                st.error(
                    "Location not found or API request failed."
                )

        except Exception as e:

            st.error(
                f"Unable to get weather data: {e}"
            )


st.divider()


# -----------------------------
# Environmental Data
# -----------------------------

st.header("🌧️ Environmental Data")

col1, col2 = st.columns(2)

with col1:

    rainfall = st.number_input(
        "Rainfall (mm)",
        min_value=0.0,
        max_value=1000.0,
        value=float(
            st.session_state.get("rainfall", 50.0)
        )
    )

    humidity = st.number_input(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(
            st.session_state.get("humidity", 60.0)
        )
    )


with col2:

    river_level = st.number_input(
        "River Level (m)",
        min_value=0.0,
        max_value=20.0,
        value=2.0
    )

    soil_moisture = st.number_input(
        "Soil Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0
    )


st.divider()


# -----------------------------
# Flood Prediction
# -----------------------------

if st.button(
    "🔍 Predict Flood Risk",
    use_container_width=True
):

    # Load model
    model = joblib.load(
        "flood_model.pkl"
    )

    # Input data
    input_data = pd.DataFrame({
        "rainfall": [rainfall],
        "humidity": [humidity],
        "river_level": [river_level],
        "soil_moisture": [soil_moisture]
    })

    # Prediction
    prediction = model.predict(
        input_data
    )[0]

    probability = model.predict_proba(
        input_data
    )[0][1]


    # Risk result
    if prediction == 1:

        risk_level = "HIGH RISK"

        st.error(
            f"🚨 HIGH FLOOD RISK in {location}"
        )

        st.warning(
            "Please stay alert and follow local safety instructions."
        )

    else:

        risk_level = "LOW RISK"

        st.success(
            f"✅ LOW FLOOD RISK in {location}"
        )


    # -----------------------------
    # Result cards
    # -----------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Flood Risk Level",
            risk_level
        )

    with col2:

        st.metric(
            "Flood Risk Probability",
            f"{probability * 100:.1f}%"
        )


    # -----------------------------
    # Data Summary
    # -----------------------------

    st.divider()

    st.header("📊 Environmental Data Summary")

    summary = pd.DataFrame({
        "Parameter": [
            "Location",
            "Rainfall",
            "Humidity",
            "River Level",
            "Soil Moisture"
        ],
        "Value": [
            location,
            f"{rainfall} mm",
            f"{humidity} %",
            f"{river_level} m",
            f"{soil_moisture} %"
        ]
    })

    st.table(summary)


    # -----------------------------
    # Visualization
    # -----------------------------

    st.header("📈 Environmental Data Visualization")

    chart_data = pd.DataFrame({
        "Parameter": [
            "Rainfall",
            "Humidity",
            "River Level",
            "Soil Moisture"
        ],
        "Value": [
            rainfall,
            humidity,
            river_level,
            soil_moisture
        ]
    })

    st.bar_chart(
        chart_data.set_index("Parameter")
    )


    # -----------------------------
    # Risk Probability
    # -----------------------------

    st.subheader("🎯 Flood Risk Probability")

    probability_data = pd.DataFrame({
        "Risk": [
            "No Flood Risk",
            "Flood Risk"
        ],
        "Probability": [
            1 - probability,
            probability
        ]
    })

    st.bar_chart(
        probability_data.set_index("Risk")
    )


    # -----------------------------
    # Map
    # -----------------------------

    st.divider()

    st.header("🗺️ Location Map")

    try:

        geolocator = Nominatim(
            user_agent="floodwatch_ai"
        )

        location_data = geolocator.geocode(
            location
        )

        if location_data:

            latitude = location_data.latitude
            longitude = location_data.longitude

            flood_map = folium.Map(
                location=[
                    latitude,
                    longitude
                ],
                zoom_start=10
            )

            folium.Marker(
                [
                    latitude,
                    longitude
                ],
                popup=f"{location} - {risk_level}",
                tooltip="FloodWatch AI"
            ).add_to(flood_map)

            st_folium(
                flood_map,
                width=1000,
                height=500
            )

        else:

            st.warning(
                "Location not found."
            )

    except Exception:

        st.warning(
            "Unable to load the map."
        )


    # -----------------------------
    # Disclaimer
    # -----------------------------

    st.divider()

    st.info(
        "FloodWatch AI is a project prototype using a sample dataset "
        "and machine-learning model. It should not be used as an official "
        "real-world flood warning system."
    )
    # -----------------------------
# AI Flood Assistant
# -----------------------------

st.divider()

st.header("🤖 FloodWatch AI Assistant")

st.write(
    "Ask questions about floods, rainfall, flood risk, "
    "and safety."
)

user_question = st.text_input(
    "Ask your question:"
)

if st.button("💬 Ask AI"):

    if user_question:

        try:
            from ollama import chat

            response = chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are FloodWatch AI Assistant. "
                            "Answer questions about floods, rainfall, "
                            "weather and general flood safety in simple "
                            "language. Do not claim to provide official "
                            "emergency warnings."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_question
                    }
                ]
            )

            answer = response["message"]["content"]

            st.success("🤖 AI Response")

            st.write(answer)

        except Exception as e:

            st.error(
                f"Unable to connect to Ollama: {e}"
            )

    else:

        st.warning(
            "Please enter a question."
        )