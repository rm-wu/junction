import os
from config import setup_token

if __name__ == "__main__":
    if input("Setting up Hugging Face Token ? (y/n): ").lower() == 'y':
        token = input("Please enter your Hugging Face token: ")
        setup_token(token)

    print("Setting up environment...")
    if input("Install requirements? (y/n): ").lower() == 'y':
        os.system("pip install fastapi uvicorn transformers torch langchain sentence-transformers faiss-cpu langchain-community accelerate>=0.26.0")
    
    print("Starting server...")
    os.system("python chat_app.py")

