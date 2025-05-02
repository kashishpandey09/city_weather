import requests
import streamlit as st
from datetime import datetime, timedelta

# Function to convert Unix timestamp to human-readable time in local time zone
def unix_to_local_time(unix_timestamp, timezone_offset):
    local_time = datetime.utcfromtimestamp(unix_timestamp) + timedelta(seconds=timezone_offset)
    return local_time.strftime('%H:%M:%S')

# Function to suggest outfits based on the weather
def outfit_suggestions(temp, description):
    if temp > 25:
        return "🌞 It's warm! Wear light clothes like shorts and a T-shirt."
    elif temp < 10:
        return "❄️ It's cold! A warm jacket and scarf would be perfect."
    elif "rain" in description.lower():
        return "☔ It's rainy! Don't forget an umbrella and waterproof jacket."
    else:
        return "🌤️ Dress comfortably, maybe with a sweater or light jacket."

# Function to set weather background based on weather description
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

# Function to set background image
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

# Function to get weather data
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

        # Display weather info
        st.write(f"🌡️ Temperature in {city}: {temperature}°C")
        st.write(f"🌥️ Weather Description: {description.capitalize()}")
        st.write(f"💨 Wind Speed: {wind_speed} m/s")
        st.write(f"💧 Humidity: {humidity}%")
        st.write(f"🌅 Sunrise: {sunrise} (Local Time)")
        st.write(f"🌇 Sunset: {sunset} (Local Time)")

        # Display weather icon
        st.image(f"http://openweathermap.org/img/wn/{weather_icon}.png", width=100)

        # Outfit suggestion
        outfit = outfit_suggestions(temperature, description)
        st.markdown(f"👗 **Outfit Suggestion:** {outfit}")

        # Set background based on weather
        set_weather_background(description)

        # Fetch and display 5-day forecast in the sidebar
        get_forecast(city, api_key)

    else:
        st.write("❌ City not found. Please try again!")

# Function to get 5-day weather forecast
def get_forecast(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Display the 5-day forecast in the sidebar
        st.sidebar.write("🌤️ 5-Day Forecast:")
        for forecast in data['list'][::8]:  # Take one forecast every 24 hours
            date = datetime.utcfromtimestamp(forecast['dt'])
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            weather_icon = forecast['weather'][0]['icon']
            st.sidebar.write(f"📅 {date.strftime('%Y-%m-%d %H:%M:%S')}: {temp}°C, {description}")
            st.sidebar.image(f"http://openweathermap.org/img/wn/{weather_icon}.png", width=50)

    else:
        st.write("❌ Could not fetch forecast data.")

# Main function to run the app
def main():
    api_key = "a6f81aff8e354cf14db2c448cbb27e5c"  # Replace with your actual API key
    st.title("📡 Today's Weather")

    # Default background
    background_image_url = "https://img.freepik.com/free-vector/sunshine-background-poster_1284-9444.jpg?semt=ais_hybrid&w=740"
    set_background_image(background_image_url)

    city = st.text_input("Enter a city name:", "")
    if city:
        get_weather(city, api_key)

if __name__ == "__main__":
    main()
