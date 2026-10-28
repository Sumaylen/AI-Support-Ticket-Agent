from src.llm_client import classify_json
from src.dataset import load_dataset_split

category_list = None
CLASSIFY_PROMPT = None

def initialize_classifier():
    global category_list, CLASSIFY_PROMPT
    if category_list is not None:
        return

    dataset = load_dataset_split()
    category_list = dataset[0]["category"].unique().tolist() #returns a list of unique categories form train_df  
    category_list.append("OFF_TOPIC")

    CLASSIFY_PROMPT = (
        "You route customer support messages into one category.\n"
        f"Allowed categories: {', '.join(category_list)}\n"
        "Disambiguation for commonly confused categories:\n"
        "- DELIVERY: asking about delivery options or how long delivery takes\n"
        "- SHIPPING: setting up or changing the shipping address\n"
        "- ORDER: placing, changing, or tracking an order\n"
        "- CANCEL: cancelling an order, or asking about cancellation fees\n"
        "- PAYMENT: payment methods accepted, or problems with a payment\n"
        "Reply with ONLY JSON: {\"category\": \"<name>\"}, where <name> is copied "
        "exactly, character for character, from the allowed categories. "
        "Never abbreviate, alter, or invent a name.\n"
    )

URGENCY_PROMPT = (
    "Rate how urgent this customer message is. "
    "low: general question, no time pressure. "
    "medium: a problem affecting them, but not blocking. "
    "high: blocked, money at risk, or an explicit deadline."
)
URGENCY_LEVELS = ["low", "medium", "high"]

   
def classify_ticket(message):
    initialize_classifier()
    return classify_json(
        [
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": message},
        ],
        "ticket_category",
        "category",
        category_list
    )


def detect_urgency(message):
    return classify_json(
        [
            {"role": "system", "content": URGENCY_PROMPT},
            {"role": "user", "content": message},
        ],
        "ticket_urgency",
        "urgency",
        URGENCY_LEVELS
    )

def classify_inquiry(message):
    category = classify_ticket(message)
    urgency = detect_urgency(message) 
    return {"category": category, "urgency": urgency}


# test = classify_ticket("I would like to downloasd bill #00108, can you help me?")
# print(test)