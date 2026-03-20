"""
Pipeline ci_stability_system: detect → validate → stabilize → resolve → log.
Оркеструє повний цикл обробки вузла стабільності.
"""
from __future__ import annotations

from .detector import detect
from .logger import log_osi
from .models import StabilityNode
from .resolver import resolve
from .stabilizer import stabilize
from .validator import validate


def run_pipeline(node: StabilityNode, mode: str = "strict") -> StabilityNode:
    """
    Запускає повний pipeline для вузла стабільності.

    Кроки:
    1. detect   — виявити слабкі типи
    2. validate — перевірити F/C/S/R
    3. strict   → ValueError при наявності помилок
       adaptive → stabilize → повторна валідація
    4. resolve  — закрити у '+'
    5. log_osi  — зафіксувати osi_record
    6. повернути фінальний вузол
    """
    # Крок 1: виявлення слабких вузлів
    weak_types = detect(node)

    # Крок 2: валідація факторів
    is_valid, errors = validate(node)

    # Крок 3: обробка невалідних вузлів за режимом
    if not is_valid:
        if mode == "strict":
            details = "; ".join(errors)
            raise ValueError(
                f"[ci_stability_system] Вузол '{node.node_id}' не пройшов валідацію "
                f"(mode=strict): {details}"
            )
        # adaptive-режим: стабілізуємо і перевіряємо повторно
        node = stabilize(node)
        is_valid, errors = validate(node)

    # Крок 4: закриття у '+' (якщо valid після можливої стабілізації)
    node = resolve(node)

    # Крок 5: логування
    log_osi(node)

    # Крок 6: повернення фінального вузла
    return node
