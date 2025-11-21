from langchain_core.messages.base import BaseMessage
from typing import Callable, Dict, List
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage , AIMessage, ToolMessage
import os

def chat_agent_with_tools(input_message: BaseMessage, messages:List[BaseMessage], tools = Dict[str,Callable ]) -> AIMessage:
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    llm = init_chat_model("gemini-2.0-flash",  model_provider="google_genai",   api_key=gemini_api_key)
    
    tools_list = [tool for tool in tools.values()]
    llm_with_tools = llm.bind_tools(tools_list)
    
    messages = messages[:]+[input_message]
    
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    # Si el modelo llama a herramientas
    while  ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
             tool_name = tool_call["name"]
             selected_tool = tools[tool_name]
             tool_msg = selected_tool.invoke(tool_call)
             messages.append(tool_msg)
             # Reinvocar el modelo con la respuesta de las tools
             ai_msg = llm_with_tools.invoke(messages)
             messages.append(ai_msg)
    print(f"🤖 {ai_msg.content}\n")
    