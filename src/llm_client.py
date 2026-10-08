import os
from dotenv import load_dotenv  
from openai import OpenAI

load_dotenv()  


tools = [
    {
        "type":"function",
        "function":{
            "name":"python",
            "description":"Runs code in an ipython interpreter and returns the result of the execution after 60 seconds.",
            "parameters":{
            "type":"object",
            "properties":{
                "code":{
                "type":"string",
                "description":"The code to run in the ipython interpreter."
                }
            },
            "required":["code"]
            }
        },
    }
]

def get_llm_client():

    tool = [
    {
        "type":"function",
        "function":{
            "name":"python",
            "description":"Runs code in an ipython interpreter and returns the result of the execution after 60 seconds.",
            "parameters":{
            "type":"object",
            "properties":{
                "code":{
                "type":"string",
                "description":"The code to run in the ipython interpreter."
                }
            },
            "required":["code"]
            }
        },
    }
]
    #Get the backend from environment variable or default to "local"
    backend = os.environ.get("LLM_BACKEND", "local").lower()

    if backend == "local":
        print("Running with local backend") 
        thinking = "on"
        client = OpenAI(
            base_url = "http://localhost:8000/v1",
            api_key = "None needed" # No API key needed for local backend
        )
        model="Qwen_Qwen3.5-4B-Q4_K_M"
        tools = tool
    elif backend == "groq":
        print("Running with groq backend") 
        thinking = "disabled"
        client = OpenAI(
            base_url = "https://api.groq.com/openai/v1",
            api_key = os.environ.get("GROQ_API_KEY")
        )
        model="qwen/qwen3.8-27b"
        tools = tool
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    return client, model, thinking

client, model, thinking = get_llm_client()
def _ticket_response(system_prompt, message):
    
    chat_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
      
        #Reduce randomness for the most applicable and consistant answer
        "temperature": 0
    }
     # disables thinking, works only on select models
    if thinking == "off":
        chat_params["extra_body"] = {
            "chat_template_kwargs": {"enable_thinking": False}
        }

    chat_completion = client.chat.completions.create(**chat_params)
        
    model_response = chat_completion.choices[0].message.content

    return model_response


print(_ticket_response("Call tools", "I want to find a palindrome"))