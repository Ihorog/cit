"""
Резолвер вузлів для ci_stability_system.
Закриває валідний вузол у статус STABLE (+) та фіксує osi_record.
"""
from __future__ import annotations

import copy
import time

from .models import NodeStatus, StabilityNode
from .validator import validate


def resolve(node: StabilityNode) -> StabilityNode:
    """
    Якщо всі фактори валідні → встановлює status = NodeStatus.STABLE (+).
    Фіксує osi_record з validated_state і timestamp.
    Повертає оновлений вузол.
    """
    is_valid, errors = validate(node)

    resolved = copy.deepcopy(node)

    if is_valid:
        resolved.status = NodeStatus.STABLE
        resolved.osi_record = {
            "node_id": resolved.node_id,
            "validated_state": "stable",
            "timestamp": int(time.time()),
            "factors_snapshot": {
                "F": resolved.factors.F,
                "C": resolved.factors.C,
                "S": resolved.factors.S.value,
                "R": resolved.factors.R,
            },
        }

    return resolved
