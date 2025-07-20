from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from structured_outputs import Lib, CodeTextSep
from llm_tools import scrap_docs, scrap_snippets
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

def llm_hints(kind: str, libs: dict):

    public_prompt = f"{kind.upper()} LIBS:\n"

    for k, v in libs.items():
        public_prompt += f"use {k} for {v}\n"
    
    return public_prompt

llm = init_chat_model("gpt-4.1", model_provider="openai")
lib_extractor_llm = llm.with_structured_output(Lib)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] to allow all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = []

class QueryRequest(BaseModel):
    query: str
    system_prompt: str

@app.post("/execute-query")
async def execute_query(request: QueryRequest):
    query = request.query
    system_prompt = request.system_prompt

    try:
        def execute_llm(llm, query: str, system_promt: str):
            tools_registry = {
                "scrap_docs": scrap_docs,
                "scrap_snippets": scrap_snippets
            }
    
            tools = [scrap_docs, scrap_snippets]
            llm_with_tools = llm.bind_tools(tools)

            messages = [
                SystemMessage(system_promt),
                HumanMessage(query),
            ]

            memory.extend(messages)
    
            useful_libs = lib_extractor_llm.invoke(query)
            public_libs = useful_libs.to_dict_public()
            private_libs = useful_libs.to_dict_private()

            public_prompt = llm_hints("public", public_libs)
            private_prompt = llm_hints("private", private_libs)

            libs_text = f"{public_prompt}\n\n{private_prompt}"
    
            next_prompt = f"get the docs and search for the topics of the following libraries\n{libs_text}"
    
            ai_message = llm_with_tools.invoke(next_prompt)
            messages.append(ai_message)
            memory.append(ai_message)

            tool_calls = ai_message.tool_calls
    
            for tool_call in tool_calls:
                selected_tool = tools_registry[tool_call['name']]
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
                memory.append(tool_msg)
    
            output = llm_with_tools.invoke(memory)

            print(memory)

            return (output, messages, tool_calls)
        
        result, full_messages, tool_calls = execute_llm(llm, query, system_prompt)
        return {"result": result, "full_messages": full_messages, "tool_calls": tool_calls}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)