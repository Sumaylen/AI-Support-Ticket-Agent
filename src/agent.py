import json
import os
from tools import get_order_status
from tools import get_account_info
from llm_client import chat_with_model
from tools import TOOLS
from datetime import datetime


AGENT_SYSTEM_PROMPT = (
    "You are a lookup assistant for a customer support system. "
    "Your job is to retrieve factual order and account details relevant to a customer's message. "
    "If the request is not about an order, account, payment, refund, subscription, tracking, or invoice lookup, refuse and say you can only look up order and account details. "
    "Use get_order_status when the customer asks about a specific order, and it needs both an order ID and an account ID. "
    "Use get_account_info when the customer asks about their account. "
    "Only call a tool with IDs that appear in the customer's message. Never guess or invent an ID. "
    "If a required ID is missing, do not call the tool. State which ID is missing. "
    "If a tool returns an error or no result, report that plainly. Do not fill in details yourself. "
    "Return only the facts found; do not speculate or answer unrelated questions. "
)


def run_tool_call(tool_call):
    #get the correct paramaters from the tool
    args = json.loads(tool_call.function.arguments)

    #calls the appropriate tool function
    if tool_call.function.name == "get_order_status":
        return get_order_status(
            order_id=args["order_id"],
            account_id=args["account_id"]
        )
    elif tool_call.function.name == "get_account_info":
        return get_account_info(
            account_id=args["account_id"]
        )
    else:
        return f"Unknown tool: {tool_call.function.name}"

# agent loop that keeps calling tools until it retruns a non tool answer or reaches the tool call limit
def run_agent_loop(message, max_tries):
    tries = 0
    messages =  [{"role": "user", "content": message}]
    status = "no_lookup"
    data = []

    while tries < max_tries:

        #important for prompt_messages to be created every loop to avoid duplication of system and user messages
        prompt_messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]

        # add everything from messages to prompt message
        for msg in messages:
                prompt_messages.append(msg)

        #model call with USER and SYSTEM information 
        #also includes ASSISTANT and TOOL information after the loop runs once
        response = chat_with_model(prompt_messages, tools=TOOLS)

        #if tool was not called return
        if not response.tool_calls:
            return {
                "status": status,
                "data": data,
                "answer": response.content
            }

        #Append the models tool call to preserve context
        tool_calls_list = []

        for tool_call in response.tool_calls:
            tool_calls_list.append({
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            })

        assistant_message = {
        "role": "assistant",
        "content": response.content,
        "tool_calls": tool_calls_list,
    }
        
        messages.append(assistant_message)
        #for every tool called, call the appropriate function
        for tool_call in response.tool_calls:
            result = run_tool_call(tool_call)
            
            data.append(result)

            if result is None:
                status = "not_found"
            elif status != "not_found":
                status = "found"

            #append the details from the tool response
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        tries += 1

    return {
        "status": "limit_reached",
        "data": data,
        "answer": "Tool call limit reached, self destructing in 3 seconds."
    }

# returns true if a tool call is necessary by checking for keywords and ids
def requires_tool_call(message):
    text = message.lower()
    has_id = check_digit(message)
    keywords = False
    if "order" in text or "account" in text:
        keywords = True
    if keywords and has_id == True:
        return True
    else:
        return False

# helper functio nthat checks if there is a 4 digit number in the ticket message
def check_digit(message):
    counter = 0
    for letter in message:
        if letter.isdigit() == True:
            counter += 1
        else:
            counter = 0
        if counter > 3:
            return True
    return False

