from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from endpoints.chat_webservice import chat_webservice_api_router

import os
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = input("Por favor, ingrese su API KEY de Google (GOOGLE_API_KEY): ")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


if __name__ == "__main__":
    app = FastAPI()
    
    app.include_router(chat_webservice_api_router)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
