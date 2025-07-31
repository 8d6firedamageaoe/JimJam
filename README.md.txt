# Multi-User ChatGPT API with FastAPI

This project allows multiple users to chat with ChatGPT via a backend built using FastAPI and an OpenAI API key.

## 🛠️ Installation

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI key
uvicorn main:app --reload
