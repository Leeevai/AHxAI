from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from dotenv import load_dotenv

from helpers import get_docs
from libs import libs, lib_names

load_dotenv()

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

    return get_docs(libs[lib_name], topic)

# Initialize the chat model
llm = init_chat_model("gpt-4.1", model_provider="openai")

from pydantic import BaseModel, Field
from typing import List

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
        Suggest all libraries that are present in the code, if code is available
        
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

    def to_dict(self) -> dict:
        
        out = {}
        for item in self.lib:
            name, search = item.split(':')
            out[name.lower()] = search

        filtered = {k: v for k, v in out.items() if k in lib_names}

        return filtered

lib_extractor_llm = llm.with_structured_output(Lib)

app = FastAPI()

# Define request model
class QueryRequest(BaseModel):
    query: str
    system_prompt: str

@app.post("/")
async def execute_query(request: QueryRequest):
    query = request.query
    system_prompt = request.system_prompt

    try:
        def execute_llm(llm, query: str, system_promt: str):
            tools_registry = {
                "scrap_docs": scrap_docs
            }
    
            tools = [scrap_docs]
            llm_with_tools = llm.bind_tools(tools)
    
            messages = [
                SystemMessage(system_promt),
                HumanMessage(query),
            ]
    
            useful_libs = lib_extractor_llm.invoke(query)
            useful_libs = useful_libs.to_dict()
    
            libs_text = ""
    
            for k, v in useful_libs.items():
                libs_text += f"{k} search for `{v}`\n"
    
            next_prompt = f"get the docs and search for the topics of the following libraries\n{libs_text}"
    
            ai_message = llm_with_tools.invoke(next_prompt)
            messages.append(ai_message)
    
            tool_calls = ai_message.tool_calls
    
            for tool_call in tool_calls:
                selected_tool = tools_registry[tool_call['name']]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
    
            output = llm_with_tools.invoke(messages)
            return (output, messages, tool_calls)
        
        result, full_messages, tool_calls = execute_llm(llm, query, system_prompt)
        return {"result": result, "full_messages": full_messages, "tool_calls": tool_calls}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add this line if you need to run the server using command: uvicorn <filename>:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)