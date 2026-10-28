import json
from datetime import datetime


def log_json_event(file_path, question=None, response=None, verify_result=None, reason=None, is_prompt_injection=False, is_failed_response=False, is_off_topic=False, is_escalation=False, escalate_reason=None, ticket=None, category=None, urgency=None, verification_result=None, final_response=None, should_escalate=None):
    try:
        with open(file_path, "r") as log_file:
            entries = json.load(log_file)
    except (FileNotFoundError, json.JSONDecodeError):
        entries = []

    log_entry = {
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

    if ticket is not None:
        log_entry["ticket"] = ticket
    if category is not None:
        log_entry["category"] = category
    if urgency is not None:
        log_entry["urgency"] = urgency
    if verification_result is not None:
        log_entry["verification_result"] = verification_result
    if final_response is not None:
        log_entry["final_response"] = final_response
    if should_escalate is not None:
        log_entry["should_escalate"] = should_escalate
    if escalate_reason is not None:
        log_entry["escalate_reason"] = escalate_reason

    if is_prompt_injection:
        log_entry["question"] = question
        log_entry["flagged"] = True
        log_entry["reason"] = reason or "prompt_injection_keyword_detected"

    elif is_failed_response:
        log_entry["question"] = question
        log_entry["response"] = response
        log_entry["faithfulness_check"] = verify_result
        log_entry["reason"] = verify_result or reason
        log_entry["needed_correction"] = True

    elif is_off_topic:
        log_entry["question"] = question
        log_entry["flagged"] = True
        log_entry["reason"] = reason or "off_topic_category"

    elif is_escalation:
        log_entry["question"] = question
        log_entry["response"] = response
        log_entry["should_escalate"] = True
        log_entry["escalate_reason"] = escalate_reason

    entries.append(log_entry)

    with open(file_path, "w") as log_file:
        json.dump(entries, log_file, indent=2)
