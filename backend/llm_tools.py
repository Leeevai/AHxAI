import requests
from urllib.parse import quote_plus
from libs import libs
from langchain_core.tools import tool

from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

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
    Retrieves relevant documentation for a Python library from an external documentation source.
    
    This tool fetches specific documentation sections for Python libraries to help answer user questions
    or provide context for code-related tasks. Use this when you need current, detailed documentation
    that goes beyond your training knowledge.
    
    When to use:
    - User asks about specific library functionality, methods, or classes
    - Code analysis requires understanding of library APIs or usage patterns
    - Need examples or detailed explanations for library features
    - Want to verify current library capabilities or syntax
    
    Best practices:
    - Make the topic specific and focused (e.g., "authentication methods" not just "auth")
    - Use this tool multiple times with different topics for comprehensive coverage
    - Only use for well-known public Python libraries (pandas, requests, flask, etc.)
    - Base the topic on user's actual needs and code context
    
    Args:
        lib_name (str): Name of the Python library (e.g., "pandas", "requests", "flask")
        topic (str): Specific area of interest within the library (e.g., "DataFrame operations", 
                    "HTTP authentication", "route decorators")
    
    Returns:
        str: Formatted documentation content relevant to the specified topic
    """

    return _get_docs(libs[lib_name], topic)

def _get_snippets(lib_name: str, topic: str):

    pinecone_key = os.getenv('PINECONE_KEY')
    pc = Pinecone(api_key=pinecone_key)

    index = pc.Index("first-index")

    results = index.search(
        namespace=lib_name,
        query={
            "top_k": 5,
            "inputs": {
                'text': topic
            }
        }
    )

    key_words = ['TITLE', 'text', 'LANGUAGE', 'SOURCE', 'CODE']

    context = ""

    for res in results['result']['hits']:
        fields = res['fields']
        temp = ""
        temp += key_words[0] + ': ' +fields[key_words[0]] + '\n'
        temp += "DESCRIPTION" + ': ' +fields[key_words[1]] + '\n'
        temp += key_words[2] + ': ' +fields[key_words[2]] + '\n'
        temp += key_words[3] + ': ' +fields[key_words[3]] + '\n'
        temp += key_words[4] + ': ' + f"```\n{fields[key_words[4]]}\n```" + '\n'

        context += temp + '----------------------\n'

    return context



@tool
def scrap_snippets(lib_name: str, topic: str) -> str:
    """
        Uses _get_snippets function to scrap documentation from pinecone database, if code is provided
        use this code to reason about what the user want, the topic should be something related to the code
        and the prompt provided by the user, if there is code try reason what is the library used in order to use get_snippets
        to get useful snippets from the vector database.
        Be more descriptive with the topic focus on making it relavant to what the user is promting you.
        You can use this tool multiple times.
        Only use this tool if you are somewhat sure that this library is NOT a public python library that you have been trained on and is a
        private one with no training data on it.

        Args:
            lib_name: name of the library that we want to get its snippet that is provided by our vector database
            topic: topic of interets in the library to get more accurate and useful docs for out use case
    """

    return _get_snippets(lib_name, topic)