"""
Логер OSI-записів для ci_stability_system.
Фіксує стан вузла у stdout та повертає dict-запис.
"""
from __future__ import annotations

import json
import time

from .models import StabilityNode


def log_osi(node: StabilityNode) -> dict:
    """
    Записує osi_record вузла: { node_id, status, timestamp, validated_state, factors_snapshot }.
    Виводить у stdout (без секретів).
    Повертає dict.
    """
    record = {
        "node_id": node.node_id,
        "status": node.status.value,
        "timestamp": node.timestamp,
        "validated_state": (node.osi_record or {}).get("validated_state", "unresolved"),
        "factors_snapshot": {
            "F": node.factors.F,
            "C": node.factors.C,
            "S": node.factors.S.value,
            "R": node.factors.R,
        },
    }

    # Виводимо у stdout для операційного моніторингу
    print(f"[ci_stability_system] OSI: {json.dumps(record, ensure_ascii=False)}")

    return record
