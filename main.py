from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")


# Shared chat state and client tracking
chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # Add user message to history
            chat_history.append({"role": "user", "content": data})

            # Get GPT response
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=chat_history,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"[Error]: {str(e)}"

            # Add reply to history
            chat_history.append({"role": "assistant", "content": reply})

            # Broadcast user message and GPT reply to all clients
            for client in connected_clients:
                await client.send_text(f"You: {data}")
                await client.send_text(f"GPT: {reply}")

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
