def blocked_command_flow() -> list[dict]:
    return [{"event": "request_issued"}, {"event": "authorization_checked", "result": "allowed"}, {"event": "arbitration_result", "result": "blocked"}, {"event": "rejection_recorded", "reason": "interlock"}]
