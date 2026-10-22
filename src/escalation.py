
def should_escalate_ticket(urgency, category, verification_passed, lookup_result):
    escalate_reasons = []
    if urgency == "high":
        escalate_reasons.append("urgency_high")
    if urgency == "UNKNOWN":
        escalate_reasons.append("urgency_unknown")
    if category == "UNKNOWN":
        escalate_reasons.append("category_unknown")
    if verification_passed == False:
         escalate_reasons.append("verification_failed")
    if lookup_result == "limit_reached":
        escalate_reasons.append("tool_limit_reached")
    if not escalate_reasons:
        return False, escalate_reasons
    return True, escalate_reasons