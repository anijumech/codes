import asyncio
import json
import os
from pathlib import Path

import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ENV_PATH)

MODEL_NAME = os.getenv("OLLAMA_MODEL") or os.getenv("OPENAI_MODEL")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN") or os.getenv("MASSIVE_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")

if not MODEL_NAME:
    raise RuntimeError(f"OLLAMA_MODEL or OPENAI_MODEL is missing in {ENV_PATH}")

if not MCP_SERVER_URL:
    raise RuntimeError(f"MCP_SERVER_URL is missing in {ENV_PATH}")

client = AsyncOpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key=OLLAMA_API_KEY,
)


# ---------------------------------------------------------
# Convert MCP tools -> OpenAI tools
# ---------------------------------------------------------

def convert_mcp_tools(mcp_tools):

    tools = []

    for tool in mcp_tools:

        tools.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        })

    return tools


# ---------------------------------------------------------
# Convert MCP result -> text
# ---------------------------------------------------------

def extract_mcp_result(result):

    output = []

    for content in result.content:

        if hasattr(content, "text"):
            output.append(content.text)

        else:
            output.append(str(content))

    return "\n".join(output)


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------

async def run_agent(question):

    tools = []
    mcp = None

    try:
        mcp_headers = {}
        # if MCP_AUTH_TOKEN:
        #     mcp_headers["Authorization"] = f"Bearer {MCP_AUTH_TOKEN}"

        print(MCP_SERVER_URL + "?apikey=" + MCP_AUTH_TOKEN)

        async with streamable_http_client(
            # MCP_SERVER_URL,
            MCP_SERVER_URL + "?apikey=" + MCP_AUTH_TOKEN,
            # http_client=httpx.AsyncClient(headers=mcp_headers),
            http_client=httpx.AsyncClient(),
        ) as (
            read_stream,
            write_stream,
        ):

            async with ClientSession(
                read_stream,
                write_stream
            ) as mcp:

                # ---------------------------------------------
                # Initialize MCP connection
                # ---------------------------------------------

                await mcp.initialize()

                # ---------------------------------------------
                # Discover MCP tools
                # ---------------------------------------------

                response = await mcp.list_tools()

                mcp_tools = response.tools

                print("\nAvailable MCP tools:")

                for tool in mcp_tools:
                    print(f"  - {tool.name}")

                # ---------------------------------------------
                # Convert tools to OpenAI format
                # ---------------------------------------------

                tools = convert_mcp_tools(mcp_tools)

                # ---------------------------------------------
                # Initial user message
                # ---------------------------------------------

                input_messages = [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]

                # ---------------------------------------------
                # Agent loop
                # ---------------------------------------------

                while True:

                    response = await client.responses.create(
                        model=MODEL_NAME,
                        instructions="""
You are an intelligent research agent.

You have access to tools provided by an MCP server.

When answering the user's question:

1. Determine whether MCP tools are necessary.
2. If a tool is useful, call the appropriate tool.
3. You may call multiple tools.
4. Use the results of the tools to reason about the answer.
5. Do not invent data that could have been obtained from a tool.
6. Continue using tools until you have enough information.
7. Then provide a concise, well-supported final answer.
""",
                        input=input_messages,
                        tools=tools,
                    )

                    # -----------------------------------------
                    # Look for tool calls
                    # -----------------------------------------

                    tool_calls = [
                        item
                        for item in response.output
                        if item.type == "function_call"
                    ]

                    # -----------------------------------------
                    # No tool calls -> final answer
                    # -----------------------------------------

                    if not tool_calls:

                        print("\nANSWER:")
                        print(response.output_text)

                        return response.output_text

                    # -----------------------------------------
                    # Execute MCP tools
                    # -----------------------------------------

                    for tool_call in tool_calls:

                        tool_name = tool_call.name

                        arguments = json.loads(
                            tool_call.arguments
                        )

                        print(
                            f"\nCalling MCP tool: "
                            f"{tool_name}"
                        )

                        print(
                            f"Arguments: {arguments}"
                        )

                        # Find the MCP tool
                        result = await mcp.call_tool(
                            tool_name,
                            arguments,
                        )

                        result_text = extract_mcp_result(
                            result
                        )

                        print(
                            f"Tool result:\n"
                            f"{result_text}"
                        )

                        # -------------------------------------
                        # Give tool result back to LLM
                        # -------------------------------------

                        input_messages.append(
                            {
                                "type": "function_call",
                                "call_id": tool_call.call_id,
                                "name": tool_name,
                                "arguments": tool_call.arguments,
                            }
                        )

                        input_messages.append(
                            {
                                "type": "function_call_output",
                                "call_id": tool_call.call_id,
                                "output": result_text,
                            }
                        )
    except Exception as exc:
        print(f"\nMCP server unavailable or auth failed: {exc}")
        print("Continuing without MCP tools using the local model only.\n")

    input_messages = [
        {
            "role": "user",
            "content": question,
        }
    ]

    while True:
        response = await client.responses.create(
            model=MODEL_NAME,
            instructions="""
You are an intelligent research agent.

Use the local model to answer the user's question.
Do not invent data. If you do not have enough information, say so clearly.
""",
            input=input_messages,
            tools=[],
        )

        if response.output_text:
            print("\nANSWER:")
            print(response.output_text)
            return response.output_text

        return "I could not produce a response from the local model." 


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

async def main():

    question = input(
        "Analyze Apple Stock"
    )

    await run_agent(question)


if __name__ == "__main__":
    asyncio.run(main())