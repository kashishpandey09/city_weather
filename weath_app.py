import requests
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os

# ✅ PAGE CONFIG MUST BE FIRST
st.set_page_config(layout="wide")

# ✅ HIDE STREAMLIT MENU, FOOTER, ETC.
 hide_streamlit_cloud_elements = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
a[title="View source"] {display: none !important;}
button[kind="icon"] {display: none !important;}
</style>
"""

st.markdown(hide_streamlit_cloud_elements, unsafe_allow_html=True)
# Function to convert Unix timestamp to local time
def unix_to_local_time(unix_timestamp, timezone_offset):
    local_time = datetime.utcfromtimestamp(unix_timestamp) + timedelta(seconds=timezone_offset)
    return local_time.strftime('%H:%M:%S')

# Outfit suggestions based on temperature
def outfit_suggestions(temp, description):
    if temp > 25:
        return "🌞 It's warm! Wear light clothes like shorts and a T-shirt."
    elif temp < 10:
        return "❄️ It's cold! A warm jacket and scarf would be perfect."
    elif "rain" in description.lower():
        return "☔ It's rainy! Don't forget an umbrella and waterproof jacket."
    else:
        return "🌤️ Dress comfortably, maybe with a sweater or light jacket."

# Background based on weather description
def set_weather_background(description):
    description = description.lower()
    if "clear" in description:
        background_image_url = "https://i.gifer.com/origin/f4/f437524b815d9d77d659da4c3a0a9213_w200.gif"
    elif "cloud" in description:
        background_image_url = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp1NjY3NzNxdnZqM3Zld3RnMTNxMjk4M2E2Nnp5ajhuOHlvNmNhYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dBXNPw0XBdF1n82BBf/giphy.gif"
    elif "rain" in description:
        background_image_url = "https://ewscripps.brightspotcdn.com/dims4/default/b092021/2147483647/strip/true/crop/597x336+0+0/resize/1280x720!/quality/90/?url=http%3A%2F%2Fewscripps-brightspot.s3.amazonaws.com%2Fbc%2F0d%2Fc3a24fcf488b8d82d5593b723f63%2Fhnet-image.gif"
    elif "snow" in description:
        background_image_url = "https://cdn.pixabay.com/animation/2022/11/08/06/19/06-19-11-383_512.gif"
    elif "thunderstorm" in description:
        background_image_url = "https://media.giphy.com/media/3o6Zt8zXy3p9y3g1U8/giphy.gif"
    else:
        background_image_url = "https://cdn.pixabay.com/animation/2024/05/27/21/56/21-56-03-220_512.gif"
    set_background_image(background_image_url)

# Set background image
def set_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            height: 100vh;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Fetch weather data
def get_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        weather_icon = data['weather'][0]['icon']
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        sunrise = unix_to_local_time(data['sys']['sunrise'], data['timezone'])
        sunset = unix_to_local_time(data['sys']['sunset'], data['timezone'])

        st.write(f"🌡️ Temperature in {city}: {temperature}°C")
        st.write(f"🌥️ Weather Description: {description.capitalize()}")
        st.write(f"💨 Wind Speed: {wind_speed} m/s")
        st.write(f"💧 Humidity: {humidity}%")
        st.write(f"🌅 Sunrise: {sunrise} (Local Time)")
        st.write(f"🌇 Sunset: {sunset} (Local Time)")

        st.image(f"http://openweathermap.org/img/wn/{weather_icon}.png", width=100)

        outfit = outfit_suggestions(temperature, description)
        st.markdown(f"👗 **Outfit Suggestion:** {outfit}")

        set_weather_background(description)

        get_forecast(city, api_key)
    else:
        st.write("❌ City not found. Please try again!")

# 5-day forecast and temperature graph
def get_forecast(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        st.sidebar.write("🌤️ 5-Day Forecast:")
        dates = []
        temps = []

        for forecast in data['list'][::8]:
            date = datetime.utcfromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            icon = forecast['weather'][0]['icon']

            dates.append(date)
            temps.append(temp)

            st.sidebar.write(f"📅 {date}: {temp}°C, {description}")
            st.sidebar.image(f"http://openweathermap.org/img/wn/{icon}.png", width=50)

        # Background for the graph
        bg_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSgyC8gReZ4RtauxTzgODM1Zi2qt8wx8ZGK1g&s"
        response = requests.get(bg_url)
        bg_img = Image.open(BytesIO(response.content)).convert("RGBA")

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.imshow(bg_img, extent=[-0.5, len(dates)-0.5, min(temps)-5, max(temps)+5], aspect='auto', alpha=0.3)
        ax.plot(dates, temps, marker='o', linestyle='-', color='blue')
        ax.set_title("📈 5-Day Temperature Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("°C")
        ax.grid(True)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45)

        st.sidebar.pyplot(fig)
    else:
        st.write("❌ Could not fetch forecast data.")

# Add this helper function near the top of your code
def show_resized_image(image_path, caption, size=(150, 150)):
    try:
        img = Image.open(image_path)
        img = img.resize(size)
        st.image(img, caption=caption)
    except Exception as e:
        st.error(f"Error loading image '{caption}': {e}")

# Update your about_section() to use resized images
def about_section():
    st.title("👨‍💼 About Us")
    st.markdown("Welcome to our weather app! Meet the team:")

    cols = st.columns(3)
    with cols[0]:
        show_resized_image("images/Altaf.jpeg", "Altaf Hussain")
        st.markdown("**Team Coordinator**")
    with cols[1]:
        show_resized_image("images/Shreya.jpeg", "Shreya Singh")
        st.markdown("**Backend Developer**")
    with cols[2]:
        show_resized_image("images/Kashi.png", "Kashish Pandey")
        st.markdown("**Frontend Developer**")

    st.markdown("---")
    st.subheader("📞 Contact Us")
    st.write("Email: altafaipa95@gmail.com")
    st.write("Phone: +9125971036")

# Main function
def main():
    api_key = "a6f81aff8e354cf14db2c448cbb27e5c"  # Replace with your actual API key

    menu = st.sidebar.selectbox("Navigate", ["Today's Weather", "About"])

    if menu == "Today's Weather":
        st.title("📡 Today's Weather")
        default_bg = "https://img.freepik.com/free-vector/sunshine-background-poster_1284-9444.jpg?semt=ais_hybrid&w=740"
        set_background_image(default_bg)
        city = st.text_input("Enter a city name:", "")
        if city:
            get_weather(city, api_key)
    elif menu == "About":
        about_section()

# Run app
if __name__ == "__main__":
    main()
