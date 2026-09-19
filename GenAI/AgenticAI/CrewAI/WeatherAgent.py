import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def weather_code_to_text(code):
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Rain showers",
        81: "Heavy rain showers",
        82: "Violent rain showers",
        85: "Snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Severe thunderstorm with hail",
    }
    return mapping.get(code, "Unknown weather condition")


def get_weather_in_location(location: str, state: str = "", country: str = "") -> str:
    place = ", ".join(part for part in [location, state, country] if part and part.strip())

    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": place, "count": 1, "language": "en", "format": "json"},
        timeout=30,
    )
    geo.raise_for_status()
    results = geo.json().get("results") or []
    if not results:
        return f"I could not find a matching location for '{place}'."

    selected = results[0]
    lat = selected.get("latitude")
    lon = selected.get("longitude")
    name = selected.get("name", "")
    admin = selected.get("admin1", "")
    country_name = selected.get("country", "")
    label = ", ".join(part for part in [name, admin, country_name] if part)

    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "timezone": "auto",
            "forecast_days": 1,
        },
        timeout=30,
    )
    weather.raise_for_status()
    data = weather.json()

    current = data.get("current", {})
    temp = current.get("temperature_2m")
    wind = current.get("wind_speed_10m")
    humidity = current.get("relative_humidity_2m")
    summary = weather_code_to_text(current.get("weather_code"))
    return f"{label}: {temp}°C, {summary}, wind {wind} km/h, humidity {humidity}%"


try:
    from crewai import Agent
    from crewai.tools import tool
except ImportError:  # pragma: no cover
    Agent = None
    tool = None


if tool is not None:
    @tool("Get the current weather for a city or location.")
    def fetch_weather_tool(location: str, state: str = "", country: str = "") -> str:
        """Get the current or past or future weather for a city or location or country."""
        return get_weather_in_location(location, state, country)

    def build_weather_agent(model: str = os.getenv("OLLAMA_MODEL", "llama3.2")):
        return Agent(
            role="Weather Specialist",
            goal="Provide weather details for the location that the user asks for.",
            backstory="You use live or historicalweather data to answer questions clearly.",
            tools=[fetch_weather_tool],
            llm=f"ollama/{model}",
            verbose=False,
            allow_delegation=False,
        )
else:
    def build_weather_agent(model: str = os.getenv("OLLAMA_MODEL", "llama3.2")):
        raise RuntimeError("CrewAI is not installed. Run: pip install crewai")


if __name__ == "__main__":
    city = input("Enter city: ").strip()
    if city:
        print(get_weather_in_location(city))
