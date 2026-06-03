from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .routes.chat import router as chat_router
from .routes.telegram import router as chat_telegram

app = FastAPI()
        
        
app.include_router(chat_router)
app.include_router(chat_telegram)
