import requests
from urllib.parse import quote_plus
from libs import libs
from langchain_core.tools import tool

def _get_docs(base_url: str, topic: str, tokens: int = 5_000) -> str:

    topic = quote_plus(topic)

    url = f"{base_url}/llms.txt?topic={topic}&tokens={tokens}"

    response = requests.get(url)

    if response.status_code == 200:
        llms_text_data = response.text
    else:
        llms_text_data = f"Failed to fetch data. Status code: {response.status_code}"

    return llms_text_data

@tool
def scrap_docs(lib_name: str, topic: str) -> str:
    """
        Uses get_docs function to scrap documentation from context7, if code is provided
        use this code to reason about what the user want, the topic should be something related to the code
        and the prompt provided by the user, if there is code try reason what is the library used to scrap
        its docs using the get_docs function be more descriptive with the topic focus on making it relavant to what the user is promting you.
        You can use this tool multiple times.

        Args:
            lib_name: name of the library that we want to scrap that is provided by context7
            topic: topic of interets in the library to get more accurate and useful docs for out use case
    """

    return _get_docs(libs[lib_name], topic)