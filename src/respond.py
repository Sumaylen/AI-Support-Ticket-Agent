# This file is a simple implementation of an Evaluator Optimizer
import json
import os
from datetime import datetime

from llm_client import chat_with_model


LOG_PATH = os.path.abspath("logs/failed_responselog.json")

REPLY_PROMPT = (
    "You are a support agent. Answer using only the retrieved policy text and tool lookup results. "
    "Write a brief, empathetic, customer-friendly reply based only on supported facts. "
    "Do not invent policies, exceptions, or guarantees. "
    "Use the lookup results for order, account, delivery, and plan details when available. "
    "Use the policy text for payment rules, refund rules, and failed-payment guidance. "
    "If the customer provides an order number or account detail that is missing, invalid, or not found, say that the detail could not be verified and ask them to confirm it. "
    "If the request is outside company policy, give a short professional refusal and suggest the next correct step."
)

VERIFY_PROMPT = (
    "Check the draft against the retrieved policy text and the tool lookup results. "
    "Return exactly 'true' only if every factual claim is supported by the policy text or lookup data. "
    "Return exactly 'false' if any claim is unsupported, speculative, invented, or inconsistent with the evidence. "
    "A generic refusal is not valid for real order, account, payment, or lookup requests. "
    "After the true/false answer, add a brief reason in one sentence."
)

FIX_PROMPT = (
    "Rewrite the draft so every claim is supported by the retrieved policy text or lookup results. "
    "Remove unsupported assumptions, speculation, and extra explanations. "
    "Keep the response brief, clear, empathetic, and grounded in the evidence."
)

# pass the ticket to the model including relevant policies
def draft_reply(ticket, retrieved_chunks, lookup_result="", extra_instruction="", failure_reason="" ):
    chunks_text = format_chunks(retrieved_chunks)
    policy_prompt =( f"{REPLY_PROMPT}"
                     f"Use only the following retrieved policy information: \n{chunks_text}")

    #run with extra prompts if trying to improve accuracy of prompts
    if extra_instruction:
        policy_prompt += f"\n\nExtra instruction: {extra_instruction}"
    if failure_reason:
        policy_prompt += f"\n\nFix this specific issue: {failure_reason}"
    if lookup_result:
        policy_prompt += f"\n\nContext from the tool lookups: {lookup_result}"
    
    return chat_with_model([
    {"role": "system", "content": policy_prompt},
    {"role": "user", "content": ticket},
    ])

# check if model response is accurate
def check_faithfulness(draft, retrieved_chunks, lookup_result=""):
   chunks_text = format_chunks(retrieved_chunks)
   user_message = (
        f"Retrieved policy information:\n{chunks_text}\n\n"
        f"Context from the tool lookups:\n{lookup_result}\n\n"
        f"Draft response:\n{draft}"
    )
   return chat_with_model([
    {"role": "system", "content": VERIFY_PROMPT},
    {"role": "user", "content": user_message},
    ])

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


def create_ticket(message, retrieved_chunks, lookup_result):
    ticket = message
    verification_passed = False
   
    response = draft_reply(ticket, retrieved_chunks, lookup_result)
   
    max_attempts = 3
    attempt = 0
    failure_reason="No Failure"
    #check if response is accurate and re-prompt the model with extra details if not
    while attempt < max_attempts:
        verify = check_faithfulness(response.content, retrieved_chunks, lookup_result)
        # If passedself evaluation return
        if verify.content.strip().lower().startswith("true"):
            verification_passed = True
            return {"response": response.content, 
                    "verification_passed": verification_passed, 
                    "verification_reason": verify.content, 
                    "attempts": attempt + 1
                    }
        # else draft a new resposne with extra context
        else:
            failure_reason = verify.content
            print("\n I FAILED \n")
            log_failed_response(ticket, response.content, verify.content)
            response = draft_reply(ticket, retrieved_chunks, lookup_result, extra_instruction=FIX_PROMPT, failure_reason=failure_reason,)
            attempt += 1

    # check if verification passed in the final draft       
    if verify.content.strip().lower().startswith("true"):
                verification_passed = True
    else:
        verification_passed = False

    return {"response": response.content, 
            "verification_passed": verification_passed, 
            "verification_reason": verify.content, 
            "attempts": attempt + 1
            }
