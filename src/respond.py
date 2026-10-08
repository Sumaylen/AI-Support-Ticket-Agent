# This file is a simple implementation of an Evaluator Optimizer
import json
import os
from datetime import datetime

from retrieval import retrieve
from llm_client import get_llm_client

LOG_PATH = os.path.abspath("logs/failed_responselog.json")

REPLY_PROMPT = ("You are a support agent for a company."
    " Use the provided company policies as the sole factual basis for your answer."
    "Write a brief, empathetic, customer-friendly response to the ticket using only relevant policy information."
    "Do not make up policies, exceptions, or guarantees. "
    "If the issue is outside the policy, explain the limitation clearly and suggest the next appropriate action. ")

VERIFY_PROMPT = (
    "Check the draft against the retrieved policy text only. "
    "Return exactly 'true' only if every factual claim is directly supported or clearly implied by the policy text. "
    "Return exactly 'false' if any claim is unsupported, speculative, invented, or goes beyond the policy. "
    "Do not reject a claim just because it is phrased more simply than the policy text. "
    "Do reject claims that add assumptions, guesses, or likely explanations not stated in the policy. "
    "After the true/false answer, add a brief reason."
)

FIX_PROMPT = (
    "Rewrite the draft so it contains only claims directly supported by the retrieved policy text. "
    "Remove any unsupported assumptions, speculation, or extra explanations not present in the policy. "
    "Keep the answer brief, clear, and policy-grounded."
)

client, model, thinking = get_llm_client()

#chat response tmeplate
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

# pass the ticket to the model including relevant policies
def draft_reply(ticket, retrieved_chunks, extra_instruction="", failure_reason=""):
    chunks_text = format_chunks(retrieved_chunks)
    policy_prompt =( f"{REPLY_PROMPT}"
                     f"Use only the following retrieved policy information: \n{chunks_text}")

    #run with extra prompts if trying to improve accuracy of prompts
    if extra_instruction:
        policy_prompt += f"\n\nExtra instruction: {extra_instruction}"
    if failure_reason:
        policy_prompt += f"\n\nFix this specific issue: {failure_reason}"
    
    return _ticket_response(policy_prompt, ticket,)

# check if model response is accurate
def check_faithfulness(draft, retrieved_chunks):
   chunks_text = format_chunks(retrieved_chunks)
   user_message = (
        f"Retrieved policy information:\n{chunks_text}\n\n"
        f"Draft response:\n{draft}"
    )
   return _ticket_response(VERIFY_PROMPT, user_message)

#Helper function to format the retrieved chunks into a more readable format
def format_chunks(retrieved_chunks):
    chunks_text = ""
    for chunk in retrieved_chunks:
        chunks_text += f"Source: {chunk['source']}\n"
        chunks_text += f"{chunk['text']}\n\n"
    return chunks_text

# log to a JSON file when model responses are inaccurate
def log_failed_response(question, response, verify_result):
    with open(LOG_PATH, "r") as log_file:
        entries = json.load(log_file)

    entries.append({
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "question": question,
        "response": response,
        "faithfulness_check": verify_result,
        "reason": verify_result,
        "needed_correction": True,
    })

    with open(LOG_PATH, "w") as log_file:
        json.dump(entries, log_file, indent=2)


def create_ticket(message):
    ticket = message
    retrieved_chunks = retrieve(ticket, 5)

    response = draft_reply(ticket, retrieved_chunks)
    verify = check_faithfulness(response, retrieved_chunks)

    max_attempts = 3
    attempt = 0
    failure_reason=""
    #check if response is accurate and re-prompt the model with extra details if not
    while attempt < max_attempts:
        if verify.strip().lower().startswith("true"):
            return response
        else:
            if attempt >= 1:
                failure_reason = verify
            print("\n I FAILED \n")
            log_failed_response(ticket, response, verify)
            response = draft_reply(ticket, retrieved_chunks, extra_instruction=FIX_PROMPT, failure_reason=failure_reason)
            verify = check_faithfulness(response, retrieved_chunks)
            attempt += 1

    return response

print(create_ticket("I placed a sale item order with overnight shipping to a PO box, and now I want to add another item and change the address after it shipped. Can I do all of that?"))