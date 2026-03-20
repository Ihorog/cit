"""
FastAPI router для ci_stability_system.
Надає HTTP-ендпоінти для аналізу та стабілізації вузлів.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .detector import detect
from .models import NodeState, NodeStatus, StabilityFactors, StabilityNode
from .pipeline import run_pipeline
from .validator import validate

router = APIRouter(prefix="/stability", tags=["ci_stability_system"])


# --- Pydantic-схеми для запитів/відповідей ---

class FactorsInput(BaseModel):
    """Вхідні фактори вузла."""
    F: bool
    C: Optional[str] = None
    S: str = "stable"
    R: Optional[bool] = None


class NodeInput(BaseModel):
    """Вхідний вузол для аналізу або стабілізації."""
    node_id: str
    status: str = "-"
    factors: FactorsInput
    timestamp: int


class StabilizeRequest(BaseModel):
    """Запит на стабілізацію: вузол + режим."""
    node: NodeInput
    mode: str = "strict"


def _build_node(data: NodeInput) -> StabilityNode:
    """Перетворює Pydantic-модель у StabilityNode."""
    try:
        s_state = NodeState(data.factors.S)
    except ValueError:
        s_state = NodeState.UNSTABLE

    try:
        status = NodeStatus(data.status)
    except ValueError:
        status = NodeStatus.WEAK

    factors = StabilityFactors(
        F=data.factors.F,
        C=data.factors.C,
        S=s_state,
        R=data.factors.R,
    )
    return StabilityNode(
        node_id=data.node_id,
        status=status,
        factors=factors,
        timestamp=data.timestamp,
    )


@router.post("/node/analyze")
def analyze_node(payload: NodeInput) -> Dict[str, Any]:
    """
    Аналізує вузол: виявляє слабкі типи та перевіряє валідність.
    Повертає { weak_nodes, is_valid, errors }.
    """
    try:
        node = _build_node(payload)
        weak_types = detect(node)
        is_valid, errors = validate(node)
        return {
            "status": "ok",
            "data": {
                "weak_nodes": [w.value for w in weak_types],
                "is_valid": is_valid,
                "errors": errors,
            },
        }
    except Exception as exc:
        return {"status": "error", "data": {"message": f"[analyze] {type(exc).__name__}: {exc}"}}


@router.post("/node/stabilize")
def stabilize_node(payload: StabilizeRequest) -> Dict[str, Any]:
    """
    Запускає повний pipeline для вузла.
    Приймає вузол + mode (strict/adaptive).
    Повертає фінальний стан вузла.
    """
    try:
        node = _build_node(payload.node)
        result = run_pipeline(node, mode=payload.mode)
        return {
            "status": "ok",
            "data": {
                "node_id": result.node_id,
                "status": result.status.value,
                "osi_record": result.osi_record,
                "factors": {
                    "F": result.factors.F,
                    "C": result.factors.C,
                    "S": result.factors.S.value,
                    "R": result.factors.R,
                },
            },
        }
    except ValueError as exc:
        return {"status": "error", "data": {"message": str(exc)}}
    except Exception as exc:
        return {"status": "error", "data": {"message": f"[stabilize] {type(exc).__name__}: {exc}"}}


@router.get("/node/status/{node_id}")
def node_status(node_id: str) -> Dict[str, Any]:
    """
    Заглушка для майбутнього storage.
    Повертає { node_id, info: 'storage not connected' }.
    """
    return {
        "status": "ok",
        "data": {
            "node_id": node_id,
            "info": "storage not connected",
        },
    }
