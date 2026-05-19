def fake_alarm_lifecycle() -> list[dict]:
    return [{"event": "assert", "alarm_id": "ALM-001"}, {"event": "acknowledge", "alarm_id": "ALM-001"}, {"event": "return_to_normal", "alarm_id": "ALM-001"}]
