import os
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from merriam_webster_tool import MerriamWebster
"""
    Docs for using:
    1. Go to https://www.dictionaryapi.com/register/index and register an
       developer account with a key for the Collegiate Dictionary
    2. Get your API Key from https://www.dictionaryapi.com/account/my-keys
    3. Save your API Key into MERRIAM_WEBSTER_API_KEY env variable
"""
MODEL_NAME = "mistral:latest"  # use the Mistral model
MW_API_KEY = os.getenv("MW_API_KEY")

if MW_API_KEY is None:
    raise ValueError("API_KEY environment variable is not set.")

# LLM Used
llm = ChatOllama(model="mistral",
                temperature=0.2)

# Merriam Webster tool
mw_tool = MerriamWebster(api_key=MW_API_KEY)
word_to_define = "ethereal"
definition = mw_tool.run(word_to_define)

print(f"*** Merriam-Webster Tool Output for '{word_to_define}' ***")
print(definition)

# Agent
agent = create_agent(
    model=llm,
    tools=[mw_tool],
    system_prompt=("You are a dictionary assistant trying to output dictionary accurate definition of words with a much context as possible."
                   "Use the Merriam Webster dictionary Tool anytime a definition of a word of futher context about a word is needed."
                   ),
)

# Example usage
result = agent.invoke({
    "messages": [
        {"role": "user", "content": f"Use the Merriam-Webster tool to define the word {word_to_define} in detail"},
    ]
})

messages = result["messages"]
ai_messages = [msg for msg in messages if msg.__class__.__name__ == "AIMessage"] # Fallback: pick the last AIMessage
# Get the last AIMessage content
if ai_messages:
    ai_output = ai_messages[-1].content
    print(f"*** AI agent output for {word_to_define} ***")
    print(ai_output)
else:
    print("No AI messages found.")
