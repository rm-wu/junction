import os
from pathlib import Path
import json
from dotenv import load_dotenv

def get_token():
    token = os.getenv('HUGGINGFACE_TOKEN')
    
    if token:
        return token
        
    config_path = Path.home() / '.config' / 'huggingface' / 'token.json'
    
    try:
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get('token')
    except Exception as e:
        print(f"Error reading config file: {e}")
    
    raise ValueError("No Hugging Face token found. Please set up your token first.")


def setup_token(token):
    config_dir = Path.home() / '.config' / 'huggingface'
    config_dir.mkdir(parents=True, exist_ok=True) # create config directory if it doesn't exist
    
    config_path = config_dir / 'token.json'
    with open(config_path, 'w') as f:
        json.dump({'token': token}, f)
    
    print(f"Token saved to {config_path}")
    print("Make sure to add this path to your .gitignore!")
    
