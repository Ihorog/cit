"""
Детектор слабких вузлів для ci_stability_system.
Виявляє типи слабкостей за факторами F/C/S/R.
"""
from __future__ import annotations

from typing import List

from .models import NodeState, StabilityNode, WeakNodeType


def detect(node: StabilityNode) -> List[WeakNodeType]:
    """
    Аналізує вузол і повертає список виявлених слабких типів.
    Кожен фактор перевіряється незалежно.
    """
    weak_types: List[WeakNodeType] = []

    # F == False → відсутній підтверджений факт
    if not node.factors.F:
        weak_types.append(WeakNodeType.MISSING_FACT)

    # C is None → контекст не визначено
    if node.factors.C is None:
        weak_types.append(WeakNodeType.UNDEFINED_CONTEXT)

    # S == UNSTABLE → нестабільний внутрішній стан
    if node.factors.S == NodeState.UNSTABLE:
        weak_types.append(WeakNodeType.UNSTABLE_STATE)

    # R is None → зворотній зв'язок відсутній
    if node.factors.R is None:
        weak_types.append(WeakNodeType.NO_FEEDBACK)

    return weak_types
