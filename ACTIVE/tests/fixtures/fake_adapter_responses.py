def accepted_output_response() -> dict:
    return {"status": "accepted", "reason": None}


def blocked_output_response(reason: str = "interlock") -> dict:
    return {"status": "blocked", "reason": reason}


def adapter_transport_failure(reason: str = "timeout") -> dict:
    return {"status": "transport_failed", "reason": reason}


def adapter_observed_response(value: str = "1") -> dict:
    return {"status": "observed", "reason": None, "observed_value": value}
