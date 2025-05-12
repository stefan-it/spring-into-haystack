from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.agents import Agent
from haystack_integrations.tools.mcp import MCPTool, StdioServerInfo
from haystack.utils import Secret


github_mcp_server = StdioServerInfo(
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": Secret.from_env_var("GITHUB_PERSONAL_ACCESS_TOKEN").resolve_value() # The more secure solution ;)
    },
    command="docker",
    args=[
        "run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"
    ])

print("MCP server is created")

tool_1 = MCPTool(name="get_file_contents", server_info=github_mcp_server)
tool_2 = MCPTool(name="create_issue", server_info=github_mcp_server)

print("MCP tools are created")

system_prompt = """
You are an helpful and intelligent GitHub agent. Please execute the following steps:
    1. Use the "get_file_contents" tool to retrieve the raw content from the `README.md` file.
    2. Carefully analyze the retrieved raw content from the `README.md` for common misspellings, typos or redundant words. Perform a very detailed analysis of each word and don't hallucinate.
    3. Verify in a reasoning step that found typos do really exists in the `README.md` file.
    4. If a typo is found, create an issue in the same user-defined repository using the "create_issue" tool with the following information:
       - The defined title
       - A detailed description of the typo location (e.g. line number) and provide a suggestion for a fix
       - Add an issue footer that states: *Made from Bavarian Oberland with ❤️ and 🥨.*
"""

## Create agent - info taken from: https://docs.haystack.deepset.ai/docs/openaichatgenerator#in-a-pipeline
agent = Agent(
    chat_generator=OpenAIChatGenerator(
        api_key=Secret.from_env_var("OPENAI_API_KEY"),
        model="o4-mini-2025-04-16"
    ),
    system_prompt=system_prompt,
    tools=[tool_1, tool_2]
)

print("Agent created")

owner = "stefan-it"
repo = "spring-into-haystack"
title = "docs: fix typos using Haystack Agent"

## Example query to test your agent
user_input = f"Can you find the typo in the `README.md` of {owner}/{repo} from the `main` branch and open an issue (if not yet existing) with the title {title} about how to fix it?"

response = agent.run(messages=[ChatMessage.from_user(text=user_input)])

## Print the agent thinking process
print(response)
## Print the final response
print(response["messages"][-1].text)
