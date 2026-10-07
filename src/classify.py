import json
from llm_client import get_llm_client
from dataset import load_dataset_split

dataset = load_dataset_split()
category_list = dataset[0]["category"].unique().tolist() #returns a list of unique categories form train_df  


CLASSIFY_PROMPT = (
                    "Choose one category from: "
                    f"{category_list}. "
                    "Return valid JSON as: {\"category\":\"<category_name>\"}."
                )
URGENCY_PROMPT = (
    "Rate how urgent this customer message is. "
    "low: general question, no time pressure. "
    "medium: a problem affecting them, but not blocking. "
    "high: blocked, money at risk, or an explicit deadline."
)
URGENCY_LEVELS = ["low", "medium", "high"]


client, model, thinking = get_llm_client()
   
#chat request helper that takes in instructions and user message and outputs a JSON response
def _ask_json(system_prompt, message, schema_name, field, allowed_values):
    
    chat_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "response_format": {
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

    #if output is still in wrong format return UNKNOWN otherwise return a JSON formatted response
    try:
        formatted_response = json.loads(model_response)
        return formatted_response[field]
    except Exception:
        return "UNKNOWN"


def classify_ticket(message):
    return _ask_json(CLASSIFY_PROMPT, message, "ticket_category", "category", category_list)


def detect_urgency(message):
    return _ask_json(URGENCY_PROMPT, message, "ticket_urgency", "urgency", URGENCY_LEVELS)

def user_inquiry(message):
    category = classify_ticket(message)
    urgency = detect_urgency(message) 
    return {"category": category, "urgency": urgency}

