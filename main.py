from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
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

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")

# Connected clients
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            print(f"[DEBUG] Received: {message}")

            # Call OpenAI API
            try:
                completion = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message},
                    ]
                )
                reply = completion.choices[0].message.content
            except Exception as e:
                reply = f"[ERROR] {e}"

            # Broadcast to all clients
            for client in clients:
                try:
                    await client.send_text(f"{message}\n→ {reply}")
                except:
                    pass
    except Exception as e:
        print(f"[DISCONNECT] {e}")
    finally:
        clients.remove(websocket)
