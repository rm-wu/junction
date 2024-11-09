from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from rag_chatbot import RAGChatbot

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str


# Initialize chatbot
print("Starting initialization...")
chatbot = RAGChatbot()
print("Initialization complete!")

@app.post("/chat")
async def chat(query: Query):
    try:
        response, sources, context = chatbot.get_response(query.message)
        return {
            "response": response,
            "sources": sources,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (HTML interface)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)