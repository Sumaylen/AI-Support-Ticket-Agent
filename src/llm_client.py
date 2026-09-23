import os
from dotenv import load_dotenv  
from openai import OpenAI

load_dotenv()  

def get_llm_client():
    #Get the backend from environment variable or default to "local"
    backend = os.environ.get("LLM_BACKEND", "local").lower()

    if backend == "local":
        print("Running with local backend") 
        client = OpenAI(
            base_url = "http://localhost:8000/v1",
            api_key = "None needed" # No API key needed for local backend
        )
        model="Qwen_Qwen3.5-4B-Q4_K_M"
    elif backend == "groq":
        print("Running with groq backend") 
        client = OpenAI(
            base_url = "https://api.groq.com/openai/v1",
            api_key = os.environ.get("GROQ_API_KEY")
        )
        model="qwen/qwen3.8-27b"
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    return client, model

client, model = get_llm_client()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What sound does a sheep make?",
        }
    ],
    model=model
)

print(chat_completion.choices[0].message.content)