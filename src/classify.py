from llm_client import classify_json
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

   
def classify_ticket(message):
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

def user_inquiry(message):
    category = classify_ticket(message)
    urgency = detect_urgency(message) 
    return {"category": category, "urgency": urgency}

print(user_inquiry("what payment options do you offer?"))