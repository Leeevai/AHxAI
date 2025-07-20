from pydantic import BaseModel, Field
from typing import List
from libs import lib_names, private_libs

class Lib(BaseModel):
    f"""
        You will receive a user prompt that may or may not contain code. Your task is to:
        If the prompt contains code:
        Analyze the code to extract any function calls or relevant usage patterns.
        Identify which Python libraries are likely being used or would be helpful to solve the problem.
        If the prompt contains only natural language (no code):
        Infer what Python libraries might help solve the user's task, based on keywords or task intent (e.g., web scraping, data analysis, NLP, etc.).
        Return a list of all relevant library names. Do not return duplicates.
        The first word should in each entry should be the name of the library, and then there should be a small sentence 7 to 15 wrods at max indicating what are the things that i need from this library,
        avoid using questions, if you need more that one thing insert this library with difference search sentence, i will search a vector database so write a seach sentence that workd best with vector databases
        If the prompt is not code-related and has no technical request, return an empty list.
        Suggest all libraries that are present in the code, if code is available.
        NOTE: the libraries may be public or private with no training data one them
        
        Constraints:
        Don't the same library twice in the code unless its really needed for a different thing, not a thing similar to a previous topic
        Be accurate — only suggest libraries that are truly applicable.
        Do not hallucinate libraries unless their usage is clearly implied.
        Include libraries even if the user doesn't mention them by name, but their functionality is required.
    """

    lib: List[str] = Field(
        description=(
            "List of identified libraries from the user prompt or history. "
            "Each item must begin with the library name followed by a clear, concise task expressed as a direct command. "
            "Use action verbs (e.g., 'build', 'visualize', 'compute') to start each task description — this improves relevance in vector search. "
            "Avoid vague or filler phrases like 'implement endpoint for numerical computations with advanced math and visualization'. "
            "Be specific about what you want the library to do. "
            "No clutter — treat each description as if querying a vector database. "
            "Always separate concerns, don't use FastAPI  .... for numerical calculations (ommit thes ething only focus on the purpose of the library) VERY IMPORTANT." \
            "Always use the following formating `lib_name: seach sentence`."
        )
    )

    def to_dict_public(self) -> dict:
        
        out = {}
        for item in self.lib:
            name, search = item.split(':')
            out[name.lower()] = search

        filtered = {k: v for k, v in out.items() if k in lib_names}

        return filtered

    def to_dict_private(self) -> dict:
        
        out = {}
        for item in self.lib:
            name, search = item.split(':')
            out[name.lower()] = search

        filtered = {k: v for k, v in out.items() if k in private_libs}

        return filtered

class CodeTextSep(BaseModel):
    """
        You will be given a prompt that contains a mix of normal text and code.
        Your task is not to analyze, modify, or interpret either part.
        Simply separate the input into two distinct parts:
        Text Section: This includes any explanatory text, instructions, or natural language written by the user.
        Code Section: This includes only the code, exactly as written. Do not alter, reformat, or fix the code in any way.
    """

    text: str = Field(description="This is the text part of the promt")
    code: str = Field(description="This is the code part of the promt")