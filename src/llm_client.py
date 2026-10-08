import json
import os
from dotenv import load_dotenv  
from openai import OpenAI



load_dotenv()  


def get_llm_client():

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
    elif backend == "groq":
        print("Running with groq backend") 
        thinking = "disabled"
        client = OpenAI(
            base_url = "https://api.groq.com/openai/v1",
            api_key = os.environ.get("GROQ_API_KEY")
        )
        model="qwen/qwen3.8-27b"
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    return client, model, thinking


client, model, thinking = get_llm_client()


def chat_with_model(messages, response_format=None, tools=None):

    chat_params = {
        "model": model,
        "messages": messages,
        "temperature": 0,
    }

    if tools is not None:
        chat_params["tools"] = tools

    if response_format is not None:
        chat_params["response_format"] = response_format

    # disables thinking, works only on select models
    if thinking == "off":
        chat_params["extra_body"] = {
            "chat_template_kwargs": {"enable_thinking": False}
        }

    chat_completion = client.chat.completions.create(**chat_params)


    msg = chat_completion.choices[0].message

    return msg


def classify_json(message, schema_name, field, allowed_values):
    response = chat_with_model(
        message,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        field: {"type": "string", "enum": allowed_values}
                    },
                    "required": [field],
                    "additionalProperties": False,
                },
            },
        },
    )

    try:
        formatted_response = json.loads(response.content)
        return formatted_response[field]
    except Exception:
        return "UNKNOWN"


