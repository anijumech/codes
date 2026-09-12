import json
import os
from typing import Any, Dict, List, Optional

import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def call_ollama(model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Call the local Ollama chat API."""
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def get_weather_in_location(location: str, state: str = "", country: str = "") -> str:
    """Fetch the current weather for a place using the free Open-Meteo APIs."""
    place = ", ".join(part for part in [location, state, country] if part and part.strip())

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": place,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    geo_resp = requests.get(geo_url, params=geo_params, timeout=30)
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()

    results = geo_data.get("results") or []
    if not results:
        return f"I could not find a matching location for '{place}'. Please try a bigger city name or add state/country."

    selected = results[0]
    latitude = selected.get("latitude")
    longitude = selected.get("longitude")
    name = selected.get("name", "")
    admin = selected.get("admin1", "")
    country_name = selected.get("country", "")
    display_name = ", ".join(part for part in [name, admin, country_name] if part)

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m,is_day",
        "hourly": "temperature_2m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset",
        "timezone": "auto",
        "forecast_days": 1,
    }

    weather_resp = requests.get(weather_url, params=weather_params, timeout=30)
    weather_resp.raise_for_status()
    weather_data = weather_resp.json()

    current = weather_data.get("current", {})
    hourly = weather_data.get("hourly", {})
    daily = weather_data.get("daily", {})

    temp = current.get("temperature_2m")
    wind = current.get("wind_speed_10m")
    humidity = current.get("relative_humidity_2m")
    code = current.get("weather_code")
    weather_summary = weather_code_to_text(code)

    high = (daily.get("temperature_2m_max") or [None])[0]
    low = (daily.get("temperature_2m_min") or [None])[0]

    result = {
        "location": display_name,
        "temperature_c": temp,
        "weather": weather_summary,
        "wind_kph": wind,
        "humidity_percent": humidity,
        "high_c": high,
        "low_c": low,
    }
    return json.dumps(result, ensure_ascii=False)


def weather_code_to_text(code: Optional[int]) -> str:
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


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_in_location",
            "description": "Fetch the current weather and basic conditions for a place.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City or town name, e.g. Delhi or New York"},
                    "state": {"type": "string", "description": "Optional state or province name"},
                    "country": {"type": "string", "description": "Optional country name"},
                },
                "required": ["location"],
            },
        },
    }
]


def run_weather_agent(user_query: str, model: str = OLLAMA_MODEL) -> str:
    """Use Ollama to decide which tool to call, then summarize the weather result."""
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a helpful weather assistant. When the user asks about weather, "
                "invoke the weather tool with the appropriate location. "
                "Use the tool output to answer clearly and briefly."
            ),
        },
        {"role": "user", "content": user_query},
    ]

    first_response = call_ollama(model=model, messages=messages, tools=TOOLS)
    message = first_response.get("message", {})
    tool_calls = message.get("tool_calls") or []

    if not tool_calls:
        return message.get("content") or "I couldn't determine the right tool for that request."

    messages.append(message)

    for call in tool_calls:
        function = call.get("function", {})
        name = function.get("name")
        args = function.get("arguments", {})

        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}

        if name == "get_weather_in_location":
            result = get_weather_in_location(**args)
        else:
            result = json.dumps({"error": f"Unsupported tool requested: {name}"})

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.get("id"),
                "content": result,
            }
        )

    second_response = call_ollama(model=model, messages=messages, tools=TOOLS)
    final_message = second_response.get("message", {})
    content = final_message.get("content")

    if content:
        return content

    if final_message.get("tool_calls"):
        return "The model selected another tool call, but no final textual answer was generated."

    return "I could not produce a final weather answer."


if __name__ == "__main__":
    try:
        user_query = input("Ask for the weather: ").strip()
        if not user_query:
            raise ValueError("Query cannot be empty.")
        print(run_weather_agent(user_query))
    except Exception as exc:
        print(f"Weather agent error: {exc}\n")
        print("Make sure Ollama is running and a model like 'llama3.1' is installed.")
        print("Example: ollama run llama3.1")
