from langgraph.graph import StateGraph, START, END
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from typing import TypedDict

from src.JSON_logger import log_json_event
from src.classify import classify_inquiry
from src.retrieval import retrieve
from src.agent import run_agent_loop
from src.agent import requires_tool_call
from src.respond import create_ticket
from src.guardrails import LOG_PATH as FLAGGED_LOG_PATH
from src.guardrails import detect_prompt_injection
from src.guardrails import double_check_prompt_injection
from src.escalation import should_escalate_ticket

TOP_K = 10 #amount of releveant chunks to search for in retrieve_node
MAX_TRIES = 5 #Max tool lookup calls

class State(TypedDict):
    ticket: str
    prompt_injection: bool
    category: str
    urgency: str
    lookup_needed: bool
    lookup_result: dict
    retrieved_chunks: list
    response_draft : dict
    verification_passed : bool
    verification_reason : str
    should_escalate: bool
    escalate_reason: list

def detect_prompt_injection_node(state: State):
    flagged = detect_prompt_injection(state["ticket"])  
    return {"prompt_injection": flagged}

def route_after_prompt_guard(state: State):
    if state["prompt_injection"] == True:
        return "blocked_route"
    return "continue_route"

def double_check_prompt_injection_node(state:State):
    flagged = double_check_prompt_injection(state["ticket"])
    return {"prompt_injection": flagged}

def blocked_node(state: State):
    return {
        "response_draft": {
            "response": "I’m sorry, but I can’t help with that request. Please submit a normal support question and I’ll be happy to assist.",
            "verification_passed": False,
            "verification_reason": "Request blocked."
        }
    }

def classify_node(state: State):
    result = classify_inquiry(state["ticket"])
    return {"category": result["category"], "urgency": result["urgency"]}

def check_off_topic(state: State):
    if state["category"] == "OFF_TOPIC":
         # log to a JSON file when ticket is off topic
        log_json_event(
            FLAGGED_LOG_PATH,
            question=state["ticket"],
            reason="off_topic_category",
            is_off_topic=True,
        )
        return "blocked_route"
    return "continue_route"

def requires_lookup_node(state: State):
    requires_lookup = requires_tool_call(state["ticket"])
    return {"lookup_needed" : requires_lookup}

def route_after_requires_lookup(state: State):
    if state["lookup_needed"] == True:
        return "lookup_route"
    else:
        return "retrieve_route"

def tool_lookup_node(state: State):
    tool_lookup = run_agent_loop(state["ticket"], MAX_TRIES)
    return {"lookup_result": tool_lookup}

def lookup_passed(state: State):
    if state["lookup_result"]["status"] == "limit_reached":
        return "escalate_route"
    elif state["lookup_result"]["status"] == "not_found":
        return "invalid_route"
    else:
        return "retrieve_route"

def invalid_lookup_node(state: State):
    return {
        "response_draft": {
            "response": "The order or account details you provided are incorrect. Please check the information and try again.",
        }
    }

def retrieve_node(state: State):
    chunks = retrieve(state["ticket"], TOP_K)
    return {"retrieved_chunks": chunks}

def draft_and_verify_node(state: State):

    #if tool lookup was called returned the data if it exists otherwise the mdoels reasoning if no data is provided
    lookup = state.get("lookup_result")
    if lookup:
        context = lookup["data"] or lookup["answer"]
    else:
        context = None

    final_draft = create_ticket(state["ticket"], state["retrieved_chunks"], context)
    return {"response_draft": final_draft, "verification_passed": final_draft["verification_passed"]}

def should_escalate_ticket_node(state: State):                                                                            #incase lookup_result doesnt exist during no lookup path
    escalate, escalate_reason = should_escalate_ticket(state["urgency"], state["category"], state.get("verification_passed"), state.get("lookup_result", {}).get("status"))
    return {"should_escalate": escalate, "escalate_reason": escalate_reason}

def route_after_should_escalate_ticket(state: State):
    if state["should_escalate"] == True:
        return "escalate_route"
    return "end_route"


def escalate_node(state: State):
    existing_draft = state.get("response_draft", {}) or {}
    response = existing_draft.get("response")

    if not response:
        response = "This ticket requires human review."

    return {
        "response_draft": {
            **existing_draft,
            "response": response
        }
    }


# Define the graph structure
graph = StateGraph(State)

graph.add_node("prompt_guard", detect_prompt_injection_node)
graph.add_node("llm_prompt_guard", double_check_prompt_injection_node)
graph.add_node("blocked", blocked_node)
graph.add_node("classify", classify_node)
graph.add_node("requires_lookup", requires_lookup_node)
graph.add_node("lookup", tool_lookup_node)
graph.add_node("invalid_lookup", invalid_lookup_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("response", draft_and_verify_node)
graph.add_node("should_escalate", should_escalate_ticket_node)
graph.add_node("escalate", escalate_node)

graph.add_edge(START, "prompt_guard")

graph.add_conditional_edges("prompt_guard",route_after_prompt_guard,
    {
        "blocked_route": "blocked",
        "continue_route": "llm_prompt_guard",
    },
)

graph.add_conditional_edges("llm_prompt_guard",route_after_prompt_guard, 
    {
        "blocked_route": "blocked",
        "continue_route": "classify",
    },
)

graph.add_edge("blocked", END)

graph.add_conditional_edges("classify", check_off_topic, 
    {
        "blocked_route": "blocked",
        "continue_route": "requires_lookup",
    },
)

graph.add_conditional_edges("requires_lookup", route_after_requires_lookup,
    {
        "lookup_route": "lookup",
        "retrieve_route": "retrieve"
    },
)

graph.add_conditional_edges("lookup", lookup_passed,
    {
        "escalate_route": "should_escalate",
        "invalid_route" : "invalid_lookup",
        "retrieve_route": "retrieve"
    },
)

graph.add_edge("invalid_lookup", "should_escalate")

graph.add_edge("retrieve", "response")
graph.add_edge("response", "should_escalate")

graph.add_conditional_edges("should_escalate", route_after_should_escalate_ticket, 
    {
        "escalate_route": "escalate",
        "end_route": END
    },
)

graph.add_edge("escalate", END)

app = graph.compile()


def main(ticket):
    
    try:
        result = app.invoke({
            "ticket": ticket,
        })
    except APITimeoutError:
        print("The model took too long to respond. Please try again.")
        return
    except APIConnectionError:
        print("Could not connect to the model service. Please try again.")
        return
    except RateLimitError:
        print("The model service is currently rate limited. Please try again shortly.")
        return
    except APIStatusError as error: #catch all other api errors
        print(f"The model service returned an error: {error.status_code}")
        return
    except RuntimeError as error:
        print(f"Could not complete your ticket: {error}")
        return

    draft = result.get("response_draft") or {}

    log_json_event(
        "logs/final_ticket.json",
        ticket=result.get("ticket"),
        category=result.get("category"),
        urgency=result.get("urgency"),
        verification_result=draft.get("verification_passed"),
        final_response=draft.get("response"),
        should_escalate=result.get("should_escalate"),
        escalate_reason=result.get("escalate_reason"),
    )

    return draft["response"]


