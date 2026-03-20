"""
Валідатор факторів для ci_stability_system.
Перевіряє коректність F/C/S/R за формулою F * C * S + R.
"""
from __future__ import annotations

from typing import List, Tuple

from .models import NodeState, StabilityNode


def validate(node: StabilityNode) -> Tuple[bool, List[str]]:
    """
    Перевіряє всі 4 фактори вузла.
    Повертає (is_valid, list_of_errors).

    Правила (формула: F * C * S + R):
      - F == False → invalid (відсутній факт)
      - C is None  → distortion (спотворення контексту)
      - S == unstable → bias (зміщення стану)
      - R is None  → unverified (непідтверджений результат)
    """
    errors: List[str] = []

    if not node.factors.F:
        errors.append("F: missing_fact — рішення без підтвердженого факту заборонено")

    if node.factors.C is None:
        errors.append("C: distortion — контекст не визначено, можливе спотворення")

    if node.factors.S == NodeState.UNSTABLE:
        errors.append("S: bias — нестабільний стан впливає на всі інші фактори")

    if node.factors.R is None:
        errors.append("R: unverified — вузол без зворотнього зв'язку не завершений")

    is_valid = len(errors) == 0
    return is_valid, errors
