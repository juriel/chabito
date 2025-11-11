# Standard library imports
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv

from .dto.message_dto import ChatRequestDTO
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage , AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor



CHABITO_SYSTEM_PROMPT = """

Eres chabito y vas a manejar el chatbot de tu dueño
"""
chat_webservice_api_router = APIRouter()
@cbv(chat_webservice_api_router)
class ChatWebService:
    """
    Chat service for Don Confiado AI assistant.
    
    Handles multimodal conversations (text, audio, images) with intention detection
    and automatic data extraction from invoices and user inputs.
    """
    
    def __init__(self):
        """Initialize the chat service with environment variables and conversation storage."""
        
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self._conversations = {}
        self.gemini_model = init_chat_model("gemini-2.0-flash", model_provider="google_genai",  api_key=self.GOOGLE_API_KEY)
        print("GEMINI_MODEL IS ",type(self.GOOGLE_API_KEY))

    # =============================================================================
    # CONVERSATION MANAGEMENT UTILITIES
    # =============================================================================
    
    def find_conversation(self, conversation_id: str):
        """
        Find an existing conversation or create a new one.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of messages for the conversation
        """


        global CHABITO_SYSTEM_PROMPT
        if conversation_id in self._conversations.keys():
            return self._conversations[conversation_id]
        else:
            conversation = []
            conversation.append(SystemMessage(content=CHABITO_SYSTEM_PROMPT))
            self._conversations[conversation_id] = conversation
            return conversation 

    
    # =============================================================================
    # MAIN CHAT ENDPOINT
    # =============================================================================
    
    @chat_webservice_api_router.post("/api/chat_v2.0")
    async def chat_with_structure_output(self, request: ChatRequestDTO):
        """
        Main chat endpoint with intention detection and multimodal support.
        
        Handles text, audio, and image inputs with automatic data extraction
        and entity creation (products, providers, clients).
        
        Args:
            request: ChatRequestDTO with user message and optional file data
            
        Returns:
            Dict with chat response, detected intention, and saved entities
        """
        # Initialize LLM
        llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", api_key=self.GOOGLE_API_KEY)
        
        print("=========REQUEST=========")
        print(request)
        print("=========================")
        
        
        # Get or create conversation
        conversation = self.find_conversation(request.user_id)

        conversation.append(HumanMessage(content=request.message))
        tools = []
        prompt = prompt = ChatPromptTemplate.from_messages( 
            [ ("system", CHABITO_SYSTEM_PROMPT), ("placeholder", "{chat_history}"), ("human", "{input}"), ("placeholder", "{agent_scratchpad}"), ] )
        agent = create_tool_calling_agent(llm, tools,prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        response = agent_executor.invoke({"input":request.message, "chat_conversation":conversation})
        response_dto = {"answer": response["output"]}
        print("=========RESPONSE=========")
        print(response_dto)



        return response_dto
        
        

        