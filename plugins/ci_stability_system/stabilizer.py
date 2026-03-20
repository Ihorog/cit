"""
Стабілізатор вузлів для ci_stability_system.
Переводить слабкий вузол у стан STABILIZING (0) та намагається виправити S.
"""
from __future__ import annotations

import copy

from .models import NodeState, NodeStatus, StabilityNode


def stabilize(node: StabilityNode) -> StabilityNode:
    """
    Переводить вузол у стан STABILIZING.
    В adaptive-режимі виправляє S → NodeState.STABLE.
    Повертає оновлений вузол (не мутує оригінал).
    """
    # Копіюємо вузол, щоб не мутувати вхідні дані
    stabilized = copy.deepcopy(node)

    # Встановлюємо статус "стабілізується"
    stabilized.status = NodeStatus.STABILIZING

    # Adaptive-корекція стану S → stable
    if stabilized.factors.S == NodeState.UNSTABLE:
        stabilized.factors.S = NodeState.STABLE

    return stabilized
