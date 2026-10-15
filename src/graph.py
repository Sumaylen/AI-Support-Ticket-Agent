from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from classify import classify_inquiry
from retrieval import retrieve
from agent import run_agent_loop
from respond import create_ticket

TOP_K = 10 #amount of releveant chunks to search for in retrieve_node
MAX_TRIES = 5 #Max tool lookup calls

class State(TypedDict):
    ticket: str
    category: str
    urgency: str
    lookup_result: dict
    retrieved_chunks: list
    response_draft : dict
    verification_passed : bool
    verification_reason : str

def classify_node(state: State):
    result = classify_inquiry(state["ticket"])
    return {"category": result["category"], "urgency": result["urgency"]}

def tool_lookup_node(state: State):
    tool_lookup = run_agent_loop(state["ticket"], MAX_TRIES)
    return {"lookup_result": tool_lookup}

def retrieve_node(state: State):
    chunks = retrieve(state["ticket"], TOP_K)
    return {"retrieved_chunks": chunks}

def draft_and_verify_node(state: State):

    #it tool lookup was called returned the data if it exists otherwise the mdoels reasoning if no data is provided
    lookup = state.get("lookup_result")
    if lookup:
        context = lookup["data"] or lookup["answer"]
    else:
        context = None

    final_draft = create_ticket(state["ticket"], state["retrieved_chunks"], context)
    return {"response_draft": final_draft}


def print_result_summary(result: dict):
    """Print a simple summary of the most important output fields."""
    ticket = result.get("ticket", "N/A")
    category = result.get("category", "N/A")
    urgency = result.get("urgency", "N/A")
    chunks = result.get("retrieved_chunks") or []
    draft = result.get("response_draft") or {}

    response_text = draft.get("response", "No response draft generated.") if isinstance(draft, dict) else str(draft)
    verification = draft.get("verification_passed") if isinstance(draft, dict) else None
    verification_text = draft.get("verification_reason", "No verification text available.") if isinstance(draft, dict) else "No verification text available."

    print("\n--- Ticket Summary ---")
    print(f"Ticket: {ticket}")
    print(f"Category: {category}")
    print(f"Urgency: {urgency}")
    print(f"Verified: {'Yes' if verification else 'No'}")
    print("\nVerification:")
    print(verification_text)
    # print("\nRetrieved chunks:")
    # for i, chunk in enumerate(chunks, start=1):
    #     source = chunk.get("source", "unknown") if isinstance(chunk, dict) else "unknown"
    #     text = chunk.get("text", str(chunk)) if isinstance(chunk, dict) else str(chunk)
    #     print(f"\n[{i}] {source}")
    #     print(text)
    print("\nResponse:")
    print(response_text)
    print("---------------------\n")

# Define the graph structure
graph = StateGraph(State)

graph.add_node("classify", classify_node)
graph.add_node("lookup", tool_lookup_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("response", draft_and_verify_node)

graph.add_edge(START, "classify")
graph.add_edge("classify", "lookup")
graph.add_edge("lookup", "retrieve")
graph.add_edge("retrieve", "response")
graph.add_edge("response", END)

app = graph.compile()

result = app.invoke({
    "ticket": "What is the details for order ID 4501 for account id 1013"
})

print_result_summary(result)

print(app.get_graph().draw_mermaid())