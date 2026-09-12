import os
import json
import re
from pathlib import Path
from typing import Callable, Dict, List, Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class NewsAgentError(RuntimeError):
    pass


def get_llm_client():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    return {"base_url": base_url.rstrip("/"), "model": model}


def call_llm(prompt: str, system_prompt: str = "You are a helpful news agent.", model: str = "llama3.2") -> str:
    client = get_llm_client()
    base_url = client["base_url"]
    model_name = model or client["model"]

    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=60,
    )

    if response.status_code >= 400:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise NewsAgentError(f"Ollama request failed: {detail}")

    payload = response.json()
    content = payload.get("message", {}).get("content", "")
    if not content:
        raise NewsAgentError(f"Ollama returned no content: {payload}")
    return content.strip()


def fetch_news_from_newsapi(topic: str, page_size: int = 5, language: str = "en") -> List[Dict[str, Any]]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise NewsAgentError(
            "NEWSAPI_KEY is not set. Get a free API key from https://newsapi.org/ and export it."
        )

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
    }
    headers = {"X-Api-Key": api_key}

    response = requests.get(url, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "ok":
        raise NewsAgentError(f"News API returned an error: {payload}")

    articles = payload.get("articles", [])
    cleaned = []
    for article in articles:
        cleaned.append(
            {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
                "description": article.get("description"),
            }
        )

    return cleaned


def fetch_news_from_gnews(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise NewsAgentError(
            "GNEWS_API_KEY is not set. Get a free API key from https://gnews.io/ and export it."
        )

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": topic,
        "lang": "en",
        "max": max_results,
        "apikey": api_key,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()

    articles = payload.get("articles", [])
    return [
        {
            "title": item.get("title"),
            "source": item.get("source", {}).get("name"),
            "url": item.get("url"),
            "published_at": item.get("publishedAt"),
            "description": item.get("description"),
        }
        for item in articles
    ]


def tool_registry() -> List[Dict[str, Any]]:
    return [
        {
            "name": "fetch_news_from_newsapi",
            "description": "Fetches the latest news articles for a topic using NewsAPI (requires NEWSAPI_KEY).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The news topic or keyword to search for."}
                },
                "required": ["topic"],
            },
            "function": lambda topic: fetch_news_from_newsapi(topic),
        },
        {
            "name": "fetch_news_from_gnews",
            "description": "Fetches the latest news articles for a topic using GNews (requires GNEWS_API_KEY).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The news topic or keyword to search for."}
                },
                "required": ["topic"],
            },
            "function": lambda topic: fetch_news_from_gnews(topic),
        },
    ]


def normalize_tool_name(raw_tool_name: str) -> str:
    if not raw_tool_name:
        return ""

    tool_name = str(raw_tool_name).strip()
    tool_name = tool_name.strip("` \\n\t")

    if tool_name.startswith("{"):
        match = re.search(r'"tool_name"\s*:\s*"([A-Za-z0-9_]+)"', tool_name)
        if match:
            return match.group(1)

    match = re.search(r'([A-Za-z0-9_]+)', tool_name)
    if match:
        return match.group(1)
    return ""


def decide_tool(user_query: str, tools: List[Dict[str, Any]]) -> str:
    tool_descriptions = json.dumps([
        {"name": tool["name"], "description": tool["description"]} for tool in tools
    ], indent=2)

    prompt = f"""
You are choosing a tool from the list below to answer this user request:
User request: {user_query}

Available tools:
{tool_descriptions}

Return ONLY a valid JSON object like:
{{"tool_name": "fetch_news_from_newsapi"}}

Choose the tool that is best suited to fetch recent news about the user's topic.
"""

    candidates = {tool["name"] for tool in tools}

    try:
        llm_response = call_llm(prompt, system_prompt="You are a tool-selection agent for a news assistant.")
        cleaned = llm_response.strip()
        cleaned = re.sub(r"```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()

        try:
            payload = json.loads(cleaned)
            tool_name = payload.get("tool_name") if isinstance(payload, dict) else None
            if tool_name in candidates:
                return tool_name
        except (TypeError, ValueError):
            pass

        parsed = normalize_tool_name(cleaned)
        if parsed in candidates:
            return parsed
    except Exception:
        pass

    # Fallback strategy: if no LLM is available or parsing fails, pick the NewsAPI tool if configured; otherwise GNews.
    if os.getenv("NEWSAPI_KEY"):
        return "fetch_news_from_newsapi"
    if os.getenv("GNEWS_API_KEY"):
        return "fetch_news_from_gnews"
    return "fetch_news_from_newsapi"


def execute_tool(tool_name: str, topic: str, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for tool in tools:
        if tool["name"] == tool_name:
            return tool["function"](topic)
    raise NewsAgentError(f"Tool '{tool_name}' not found in the registry.")


def format_news(news_items: List[Dict[str, Any]]) -> str:
    if not news_items:
        return "No news articles were returned for this topic."

    lines = []
    for idx, item in enumerate(news_items, start=1):
        title = item.get("title") or "Untitled"
        source = item.get("source") or "Unknown source"
        url = item.get("url") or "No URL"
        published_at = item.get("published_at") or "Unknown date"
        description = item.get("description") or "No description available."
        lines.append(
            f"{idx}. {title}\n"
            f"   Source: {source}\n"
            f"   Published: {published_at}\n"
            f"   URL: {url}\n"
            f"   Summary: {description}\n"
        )
    return "\n".join(lines)


def run_news_agent(user_query: str) -> str:
    tools = tool_registry()
    tool_name = decide_tool(user_query, tools)

    # Ask the LLM to refine the user's topic into a news search query that is clean and specific.
    refined_query_prompt = f"""
Turn the user's news request into a short search query for a news API.
User input: {user_query}
Return only a single short phrase, no extra text.
Example output: "AI startup funding"
"""

    try:
        refined_topic = call_llm(
            refined_query_prompt,
            system_prompt="You rewrite user requests into concise search queries for news APIs.",
        )
        refined_topic = re.sub(r"\s+", " ", refined_topic).strip()
    except Exception:
        refined_topic = user_query.strip()

    if not refined_topic:
        refined_topic = user_query.strip()

    news_items = execute_tool(tool_name, refined_topic, tools)
    return format_news(news_items)


if __name__ == "__main__":
    print("NewsAgent started. Enter a topic (for example: 'latest AI news').")
    while True:
        user_input = input("\nYour topic: ").strip()
        if not user_input:
            print("Please enter a valid topic.")
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break

        try:
            result = run_news_agent(user_input)
            print("\nLatest news related to your topic:\n")
            print(result)
        except Exception as exc:
            print(f"Error: {exc}")
            print("Make sure Ollama is running locally and the model 'llama3.2' is available.")
            print("Also set one of the free news API keys:")
            print("- NEWSAPI_KEY: https://newsapi.org/")
            print("- GNEWS_API_KEY: https://gnews.io/")
