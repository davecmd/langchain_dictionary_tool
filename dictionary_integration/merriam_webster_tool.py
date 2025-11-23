import requests
from typing import Iterator, cast
from langchain.tools import BaseTool

class MerriamWebster(BaseTool):
    '''
    Langchain tool for retrieving accurate word definitions for using the Merriam-Webster Collegiate Dictionary API.

    This tool properly handles:
        - Exact dictionary entries
        - Spelling Suggestion or similar words if given word is not found
        - Missing words
        - Multiple definitions and different contexts for the same word
    '''

    name: str = "MerriamWebsterDictionary"
    description: str = ("Used to look up word definitions accurately through accessing Merriam Webster's Dictionary API."
                       "Use this tool to get exact Merriam-Webster dictionary definitions for any word. Do NOT make up definitions yourself."
                        "Input: a single word (string)"
                        "Output: a short text-based definition or an informative message if not found.")
    api_key: str

    def _run(self, word: str) -> str:
        '''
        Main tool run function.

        Input: word to be queried
        Output: Merriam-Webster API formatted response

        '''

        word = word.strip()
        if not word:
            return "Please provide a word to look up."

        data = self._query_api(word)
        return self._format_api_response(word, data)

    def _query_api(self, word: str) -> list[str] | list[dict]:
        ''' Calls Merriam-Webster's API and return the parsed JSON response. '''

        api_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
        input_url = f"{api_url}{word}?key={self.api_key}"
        resp = requests.get(input_url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _format_api_response(self, word: str, data: list[str] | list[dict]) -> str:
        ''' Checks API response and returns the appropriate responses. '''

        # no json data  means no word was found.
        if not data:
            return f"No results found for '{word}'."

        # if data's reponse is a list of strings then they are suggestions:
        if isinstance(data[0], str):
            content = data[:5]  # takes to 5 suggestions
            if len(content) > 1:
                alternatives = [f"{i + 1}. {content[i]}" for i in range(len(content))]
                return "You can try one of the following alternatives:\n\n" + "\n".join(alternatives)
            else:
                return f"Did you mean '{content[0]}'?"
        definitions = cast(list[dict], data)
        return self._format_definitions(word, definitions)

    def _format_definitions(self, query: str, definitions: list[dict]) -> str:
        ''' Takes the definition and structures a response while running a helper formatting definition function. '''

        formatted_definitions: list[str] = []
        for definition in definitions:
            formatted_definitions.extend(self._format_definition(definition))
        if len(formatted_definitions) == 1:
            return f"Definition of '{query}':\n{formatted_definitions[0]}"

        result = f"Definitions of '{query}':\n\n"
        for i, formatted_definition in enumerate(formatted_definitions, 1):
            result += f"{i}. {formatted_definition}\n"
        return result

    def _format_definition(self, definition: dict) -> Iterator[str]:
        '''
        Convert a single Merriam-Webster dictionary entry into one or more
        human-readable definition strings.

        MW entries can contain:
            - "hwi.hw": the headword (may include '*' indicating syllable breaks)
            - "fl": functional label (noun, verb, adjective, etc.)
            - "shortdef": a list of brief definitions

        '''

        # headword
        if "hwi" in definition:
            headword = definition["hwi"]["hw"].replace("*", "-")
        else:
            headword = definition["meta"]["id"].split(":")[0]

        # functional label
        functional_label = definition.get("fl", "unknown")

        # short definitions
        if "shortdef" in definition:
            for short_def in definition["shortdef"]:
                yield f"{headword}, {functional_label}, {short_def}"
        else:
            yield f"{headword}, {functional_label}"
