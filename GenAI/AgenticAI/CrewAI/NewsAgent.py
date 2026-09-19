import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class NewsAgentError(RuntimeError):
    pass


def fetch_news(topic: str, page_size: int = 5) -> str:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise NewsAgentError("NEWSAPI_KEY is not set.")

    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": topic,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
        },
        headers={"X-Api-Key": api_key},
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    if data.get("status") != "ok":
        raise NewsAgentError(f"News API error: {data}")

    articles = data.get("articles", [])[:5]
    if not articles:
        return f"No recent news found for '{topic}'."

    lines = []
    for article in articles:
        title = article.get("title") or "Untitled"
        source = article.get("source", {}).get("name") or "Unknown source"
        lines.append(f"- {title} ({source})")
    return "\n".join(lines)


try:
    from crewai import Agent
    from crewai.tools import tool
    print("tool ==", tool)
except ImportError:  # pragma: no cover
    Agent = None
    tool = None


if tool is not None:
    @tool("Fetch recent news for a given topic.")
    def fetch_news_tool(topic: str) -> str:
        """Fetch recent news for a topic and return a short summary."""
        return fetch_news(topic)

    def build_news_agent(model: str = os.getenv("OLLAMA_MODEL", "llama3.2")):
        return Agent(
            role="News Analyst",
            goal="Find relevant recent news for the user's topic.",
            backstory="You collect fresh news and report the key headlines clearly.",
            tools=[fetch_news_tool],
            llm=f"ollama/{model}",
            verbose=False,
            allow_delegation=False,
        )
else:
    def build_news_agent(model: str = os.getenv("OLLAMA_MODEL", "llama3.2")):
        raise RuntimeError("CrewAI is not installed. Run: pip install crewai")


if __name__ == "__main__":
    topic = input("Enter news topic: ").strip()
    if topic:
        print(fetch_news(topic))
