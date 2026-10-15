import json
import os
from datetime import datetime

LOG_PATH = os.path.abspath("logs/flagged_query.json")

PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all system prompts",
    "ignore all prior directives",
    "ignore the above instructions",
    "ignore the system",
    "ignore the developer",
    "ignore instructions",
    "disregard previous instructions",
    "disregard the system prompt",
    "disregard the developer prompt",
    "stop following the instructions",
    "stop following the developer instructions",
    "you are now",
    "override the rules",
    "override the system",
    "override system instructions",
    "system prompt",
    "developer instructions",
    "prompt injection",
    "act as",
]

# compare words in message to ROMPT_INJECTION_KEYWORDS return true if message is flagged
def detect_prompt_injection(message):
    text = message.lower()
    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in text:
            log_prompt_injection_attempt(message)
            return True
    return False


# log to a JSON file when a prompt-injection attempt is detected
def log_prompt_injection_attempt(message):
    with open(LOG_PATH, "r") as log_file:
        entries = json.load(log_file)

    entries.append({
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "question": message,
        "flagged": True,
        "reason": "prompt_injection_keyword_detected",
    })

    with open(LOG_PATH, "w") as log_file:
        json.dump(entries, log_file, indent=2)