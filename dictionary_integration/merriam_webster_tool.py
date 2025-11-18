import os
from json import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

import requests
from typing import List
from langchain.tools import tool

MODEL_NAME = "mistral:latest"  # use the Mistral model

MW_API_KEY = os.getenv("MW_API_KEY")
if MW_API_KEY is None:
    raise ValueError("API_KEY environment variable is not set.")

# Merriam-Webster query function
@tool
def get_definition(word: str) -> str:
    '''Query a dictionary API (Merriam-Webster / dictionaryapi.com).

    Input: a single word (string)
    Output: a short text-based definition or an informative message if not found.
    '''
    api_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
    url = f"{api_url}{word}?key={MW_API_KEY}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return f"No results found for '{word}'."
        if isinstance(data[0], str):
            # API returned suggestions
            return f"Did you mean: {', '.join(data[:5])}?"
        defs: List[str] = []
        for entry in data[:3]:  # first 3 entries
            short = entry.get("shortdef", [])
            if short:
                entry_id = entry.get("meta", {}).get("id", word)
                defs.append(f"{entry_id}: " + "; ".join(short))
        return "\n".join(defs) if defs else f"No definitions found for '{word}'."
    except Exception as e:
        return f"Error looking up '{word}': {e}"

# LLM Used
llm = ChatOllama(model="mistral",
                temperature=0.2)

# Agent
agent = create_agent(
    model=llm,
    tools=[get_definition],
    system_prompt="You are a dictionary assistant. Provide accurate definitions to the given word.",
)

# Example usage
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Define the word 'cat'."}
    ]
})

messages = result["messages"]
ai_messages = [msg for msg in messages if msg.__class__.__name__ == "AIMessage"] # Fallback: pick the last AIMessage
# Get the last AIMessage content
if ai_messages:
    ai_output = ai_messages[-1].content
    print(ai_output)
else:
    print("No AI messages found.")
