# Custom Merriam-Webster Dictionary Tool for LangChain

This repository provides a custom LangChain tool that integrates directly with the **Merriam-Webster Collegiate Dictionary API**. It allows agents to retrieve accurate dictionary definitions, handle spelling suggestions, and return clean, human-readable formatted outputs.

This tool is designed for developers building LLM-powered applications who want **reliable dictionary lookups**, high‑quality definition formatting, and transparent API handling.

---

## 🚀 Features

* **Accurate dictionary definitions** retrieved from the official Merriam-Webster Collegiate Dictionary API.
* **Handles multiple entry formats**, including:

  * Exact word matches
  * Multiple definitions / senses
  * Part of speech (functional label)
  * Proper extraction of short definitions
* **Smart fallback behavior**:

  * Returns spelling suggestions when the word is not found
  * Gracefully handles empty or malformed responses
* **Plug-and-play LangChain `BaseTool` integration**
* Clean, numeric formatting for multi-definition results

## 📁 File Location
```
dictionary_integration/
  merriam_webster_tool.py # Main Python tool implementation
  dictionary_agent_instance.py # Example agent using Ollama + Mistral
  test_merriam_webster_tool.py # Unit & integration tests
```
## 📦 Installation

Install LangChain first:


```bash
pip install langchain
```

Ensure you also have:

```bash
pip install requests
```


## 🔑 Setup: Environment Variable

You must provide your generated Merriam-Webster API key. The tool specifically utilizes Merriam-Webster's Collegiate® Dictionary with Audio's API found here: https://dictionaryapi.com/products/api-collegiate-dictionary

Set it as an environment variable:

### Windows (PowerShell):

```powershell
setx MW_API_KEY "your_api_key_here"
```

### macOS / Linux:

```bash
export MW_API_KEY="your_api_key_here"
```


## 📘 Example Outputs (using the tool's output specifically as AI agent responses depends on LLM model used)

### 📗 When a word exists ( as response depends on LLM model used)

```
Definitions of 'ethereal':

1. ethe-re-al, adjective, seeming to belong to or come from another world : otherworldly
2. ethe-re-al, adjective, of, relating to, or suggesting heaven or the heavens
3. ethe-re-al, adjective, lacking material substance : immaterial, intangible
```

### 🔍 When the word is misspelled (example input is "etherael")

```
You can try one of the following alternatives:

1. ethereal
2. ethereally
3. etherealized
4. etherized
5. etherealizes
```

### ❌ When no results or suggestions exist

```
No results found for 'asdasdasd'.
```

---

## 🧩 Tool API Details

Your `MerriamWebster` tool is structured around these internal helper methods:

* `_query_api(word)` — calls MW API and returns JSON
* `_format_api_response(word, data)` — handles suggestions vs definitions
* `_format_definitions(entries)` — formats multi-entry results
* `_format_definition(entry)` — extracts headword, part of speech, short definitions

All formatting is designed for clarity and agent readability.

---

## 🧪 Unit Testing

The tool is tested with the standard python framework ```pytest```.

Basic example:

```python
def test_valid_word():
    tool = MerriamWebster(api_key="dummy_key")
    result = tool._format_api_response("test", [{"shortdef": ["a procedure"], "fl": "noun", "hwi": {"hw": "test"}}])
    assert "Definition of 'test'" in result
```
