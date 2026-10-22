import json
from datetime import datetime


def log_json_event(file_path, question=None, response=None, verify_result=None, reason=None, is_prompt_injection=False, is_failed_response=False, is_off_topic=False, is_escalation=False, escalate_reason=None):
    with open(file_path, "r") as log_file:
        entries = json.load(log_file)

    log_entry = {
        "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

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
        log_entry["escalate_reason"] = escalate_reason

    entries.append(log_entry)

    with open(file_path, "w") as log_file:
        json.dump(entries, log_file, indent=2)
