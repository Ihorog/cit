"""
Моделі даних для плагіна ci_stability_system.
Визначає enum-и та dataclass-и для роботи з вузлами стабільності.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeStatus(str, Enum):
    """Статус вузла: слабкий (-), стабілізується (0), стабільний (+)."""
    WEAK = "-"
    STABILIZING = "0"
    STABLE = "+"


class NodeState(str, Enum):
    """Внутрішній стан системи (фактор S)."""
    STABLE = "stable"
    UNSTABLE = "unstable"


class WeakNodeType(str, Enum):
    """Типи слабких вузлів, що виявляються детектором."""
    MISSING_FACT = "missing_fact"
    UNDEFINED_CONTEXT = "undefined_context"
    UNSTABLE_STATE = "unstable_state"
    NO_FEEDBACK = "no_feedback"
    SEMANTIC_GAP = "semantic_gap"
    PREDICTION_BIAS = "prediction_bias"
    DATA_NOISE = "data_noise"
    FALSE_PATTERN = "false_pattern"


@dataclass
class StabilityFactors:
    """
    Обов'язкові інваріанти стабільності вузла Ci.
    F — підтверджений факт (Kazkar)
    C — контекст: простір/час/умови (Malya)
    S — внутрішній стан системи (Nastrij)
    R — зворотній зв'язок/результат (Podija)
    """
    F: bool
    C: Optional[str]
    S: NodeState
    R: Optional[bool]


@dataclass
class StabilityNode:
    """Вузол стабільності — основна одиниця обробки pipeline."""
    node_id: str
    status: NodeStatus
    factors: StabilityFactors
    timestamp: int
    osi_record: Optional[dict] = field(default=None)
