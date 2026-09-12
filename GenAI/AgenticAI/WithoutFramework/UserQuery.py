import json
from typing import Any, Dict, List, Optional
import WeatherAgent
import NewsAgent

import requests


OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2"


def ollama_chat(messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def news_agent(topic: str) -> str:
    return NewsAgent.fetch_news_from_newsapi(topic=topic)


def weather_agent(city: str) -> str:
    return WeatherAgent.get_weather_in_location(city)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "NewsAgent",
            "description": "Get latest news for a given topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The news topic to search for."}
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "WeatherAgent",
            "description": "Get weather information for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city for the weather report."}
                },
                "required": ["city"],
            },
        },
    },
]


AVAILABLE_TOOLS = {
    "NewsAgent": news_agent,
    "WeatherAgent": weather_agent,
}


def get_tool_call(user_query: str) -> Dict[str, Any]:
    print("\n[DEBUG] get_tool_call() started")
    print(f"[DEBUG] User query: {user_query}")

    messages = [
        {
            "role": "system",
            "content": "You are a routing assistant. Select the single best tool for the user's request. If no tool matches, ask a clarifying question.",
        },
        {"role": "user", "content": user_query},
    ]

    print("[DEBUG] Sending request to Ollama for tool selection...")
    result = ollama_chat(messages, tools=TOOLS)
    print(f"[DEBUG] Ollama response received:")

    message = result.get("message", {})
    tool_calls = message.get("tool_calls") or []
    print(f"[DEBUG] Tool calls received:")

    if not tool_calls:
        raise ValueError("No tool was selected by the LLM.")

    tool_call = tool_calls[0]
    function = tool_call.get("function", {})
    selected_tool = {
        "name": function.get("name"),
        "arguments": function.get("arguments", {}),
    }
    print(f"[DEBUG] Selected tool: {selected_tool}")
    return selected_tool


def call_selected_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    print(f"\n[DEBUG] call_selected_tool() called with tool={tool_name}, arguments={arguments}")

    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Unsupported tool: {tool_name}")

    tool_function = AVAILABLE_TOOLS[tool_name]
    print(f"[DEBUG] Executing function: {tool_function.__name__}")
    result = tool_function(**arguments)
    print(f"[DEBUG] Tool result: {result}")
    return result


def build_final_answer(user_query: str, tool_result: str) -> str:
    print(f"\n[DEBUG] build_final_answer() started")
    print(f"[DEBUG] User query: {user_query}")
    print(f"[DEBUG] Tool result: {tool_result}")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use the tool result and the user's query to provide a clear final answer.",
        },
        {"role": "user", "content": f"User query: {user_query}\n\nTool result: {tool_result}"},
    ]

    print("[DEBUG] Sending final prompt to Ollama...")
    result = ollama_chat(messages)
    final_answer = result["message"]["content"].strip()
    print(f"[DEBUG] Final answer generated: {final_answer}")
    return final_answer


def main() -> None:
    print("\n[DEBUG] Program started")
    user_query = input("Ask a question: ").strip()
    print(f"[DEBUG] Raw user input: '{user_query}'")

    if not user_query:
        print("Please provide a valid question.")
        return

    tool_call = get_tool_call(user_query)
    tool_name = tool_call["name"]
    tool_arguments = tool_call["arguments"]

    tool_result = call_selected_tool(tool_name, tool_arguments)
    final_answer = build_final_answer(user_query, tool_result)

    print("\n[DEBUG] Printing final answer to user...")
    print(final_answer)


if __name__ == "__main__":
    main()
