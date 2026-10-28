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
        primary_model="Qwen_Qwen3.5-4B-Q4_K_M"
        guardrail_model="Qwen_Qwen3.5-4B-Q4_K_M"

    elif backend == "groq":
        print("Running with groq backend") 
        thinking = "disabled"
        client = OpenAI(
            base_url = "https://api.groq.com/openai/v1",
            api_key = os.environ.get("GROQ_API_KEY")
        )
        primary_model="openai/gpt-oss-120b"
        guardrail_model="meta-llama/llama-prompt-guard-2-86m"
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    return client, primary_model, guardrail_model, thinking


client, primary_model,guardrail_model, thinking = get_llm_client()


def chat_with_model(messages,model = "primary_model", response_format=None, tools=None):
    
    if model == "primary_model":
        llm_model = primary_model
    else:
        llm_model = guardrail_model
    print("Current Model: " + llm_model)
    chat_params = {
        "model": llm_model,
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


def classify_json(message, schema_name, field, allowed_values, model = "primary_model"):
    
    if model == "primary_model":
        llm_model = "primary_model"
    else:
        llm_model = "guardrail_model"

    try:
        response = chat_with_model(
                message,
                model = llm_model,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema_name,
                        "strict": True,
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


        formatted_response = json.loads(response.content)
        return formatted_response[field]
    except Exception:
        return "UNKNOWN"


