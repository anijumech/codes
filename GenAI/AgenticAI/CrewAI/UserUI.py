import os
from typing import List

from crewai import Agent, Crew, Task

from NewsAgent import build_news_agent
from WeatherAgent import build_weather_agent


def get_user_query() -> str:
    return input("Ask a question: ").strip()


def build_crew(user_query: str):
    news_agent = build_news_agent(model=os.getenv("OLLAMA_MODEL", "llama3.2"))
    weather_agent = build_weather_agent(model=os.getenv("OLLAMA_MODEL", "llama3.2"))

    tasks = [
        Task(
            description=(
                "Answer the user query using the news agent if the question is about current events, news, or recent developments. "
                f"User query: {user_query}"
            ),
            agent=news_agent,
            expected_output="A concise answer based on the latest relevant news information.",
        ),
        Task(
            description=(
                "Answer the user query using the weather agent if the question is about climate, conditions, or weather in a place. "
                f"User query: {user_query}"
            ),
            agent=weather_agent,
            expected_output="A concise answer with the weather details for the requested place.",
        ),
    ]

    return Crew(
        # agents=[weather_agent, news_agent],
        tasks=tasks,
        verbose=True,
        allow_delegation=False,
        chat_llm="llama3.2"
    )


def main():
    user_query = get_user_query()

    if not user_query:
        print("Please provide a valid question.")
        return

    crew = build_crew(user_query)
    result = crew.kickoff()
    print("\nFinal answer:\n")
    print(result)


if __name__ == "__main__":
    main()
