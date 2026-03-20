#!/usr/bin/env python3
"""
Тести для плагіна ci_stability_system.
Покриває detector, validator, pipeline, resolver та API endpoint.
"""
import sys
import time
import unittest
from pathlib import Path

# Додаємо корінь проекту до шляху імпорту
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from plugins.ci_stability_system.models import (
    NodeState,
    NodeStatus,
    StabilityFactors,
    StabilityNode,
    WeakNodeType,
)
from plugins.ci_stability_system.detector import detect
from plugins.ci_stability_system.validator import validate
from plugins.ci_stability_system.pipeline import run_pipeline
from plugins.ci_stability_system.resolver import resolve


def _make_node(F=True, C="local", S=NodeState.STABLE, R=True, status=NodeStatus.WEAK):
    """Хелпер: створює StabilityNode з заданими параметрами."""
    return StabilityNode(
        node_id="test-node-001",
        status=status,
        factors=StabilityFactors(F=F, C=C, S=S, R=R),
        timestamp=int(time.time()),
    )


class TestDetector(unittest.TestCase):
    """Тести детектора слабких вузлів."""

    def test_detector_missing_fact(self):
        """F=False → MISSING_FACT у списку."""
        node = _make_node(F=False)
        weak = detect(node)
        self.assertIn(WeakNodeType.MISSING_FACT, weak)

    def test_detector_undefined_context(self):
        """C=None → UNDEFINED_CONTEXT у списку."""
        node = _make_node(C=None)
        weak = detect(node)
        self.assertIn(WeakNodeType.UNDEFINED_CONTEXT, weak)

    def test_detector_unstable_state(self):
        """S=UNSTABLE → UNSTABLE_STATE у списку."""
        node = _make_node(S=NodeState.UNSTABLE)
        weak = detect(node)
        self.assertIn(WeakNodeType.UNSTABLE_STATE, weak)

    def test_detector_no_feedback(self):
        """R=None → NO_FEEDBACK у списку."""
        node = _make_node(R=None)
        weak = detect(node)
        self.assertIn(WeakNodeType.NO_FEEDBACK, weak)

    def test_detector_no_weak_when_all_valid(self):
        """Якщо всі фактори OK → список порожній."""
        node = _make_node()
        weak = detect(node)
        self.assertEqual(weak, [])


class TestValidator(unittest.TestCase):
    """Тести валідатора факторів F/C/S/R."""

    def test_validator_invalid_no_fact(self):
        """F=False → is_valid=False."""
        node = _make_node(F=False)
        is_valid, errors = validate(node)
        self.assertFalse(is_valid)
        self.assertTrue(any("missing_fact" in e for e in errors))

    def test_validator_valid_all_factors(self):
        """Всі фактори OK → is_valid=True, список помилок порожній."""
        node = _make_node()
        is_valid, errors = validate(node)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

    def test_validator_invalid_undefined_context(self):
        """C=None → is_valid=False з distortion-помилкою."""
        node = _make_node(C=None)
        is_valid, errors = validate(node)
        self.assertFalse(is_valid)
        self.assertTrue(any("distortion" in e for e in errors))

    def test_validator_invalid_unstable_state(self):
        """S=UNSTABLE → is_valid=False з bias-помилкою."""
        node = _make_node(S=NodeState.UNSTABLE)
        is_valid, errors = validate(node)
        self.assertFalse(is_valid)
        self.assertTrue(any("bias" in e for e in errors))


class TestPipeline(unittest.TestCase):
    """Тести pipeline: detect → validate → stabilize → resolve → log."""

    def test_pipeline_strict_raises_on_weak(self):
        """strict mode + weak node → ValueError."""
        node = _make_node(F=False)
        with self.assertRaises(ValueError):
            run_pipeline(node, mode="strict")

    def test_pipeline_adaptive_stabilizes(self):
        """adaptive mode + S=unstable → фінальний статус '+'."""
        node = _make_node(S=NodeState.UNSTABLE)
        result = run_pipeline(node, mode="adaptive")
        self.assertEqual(result.status, NodeStatus.STABLE)

    def test_pipeline_strict_valid_node(self):
        """strict mode + валідний вузол → статус '+'."""
        node = _make_node()
        result = run_pipeline(node, mode="strict")
        self.assertEqual(result.status, NodeStatus.STABLE)

    def test_pipeline_adaptive_missing_fact_stays_invalid(self):
        """
        adaptive mode + F=False → stabilize не може виправити F,
        тому resolve не встановлює STABLE.
        """
        node = _make_node(F=False)
        # Стабілізатор не виправляє F, тому resolve не дасть STABLE
        result = run_pipeline(node, mode="adaptive")
        # Статус НЕ повинен бути STABLE (факт не підтверджений)
        self.assertNotEqual(result.status, NodeStatus.STABLE)


class TestResolver(unittest.TestCase):
    """Тести резолвера: закриття вузла у '+'."""

    def test_resolver_sets_stable(self):
        """Після resolve з валідними факторами → status='+'."""
        node = _make_node()
        result = resolve(node)
        self.assertEqual(result.status, NodeStatus.STABLE)

    def test_resolver_sets_osi_record(self):
        """Після resolve osi_record заповнений."""
        node = _make_node()
        result = resolve(node)
        self.assertIsNotNone(result.osi_record)
        self.assertEqual(result.osi_record["validated_state"], "stable")

    def test_resolver_does_not_set_stable_if_invalid(self):
        """Якщо вузол не валідний → resolve не ставить STABLE."""
        node = _make_node(F=False)
        result = resolve(node)
        self.assertNotEqual(result.status, NodeStatus.STABLE)


class TestAPIEndpoint(unittest.TestCase):
    """Тести FastAPI endpoint /stability/node/analyze."""

    def test_api_analyze_endpoint(self):
        """POST /stability/node/analyze → повертає weak_nodes та is_valid."""
        try:
            from fastapi.testclient import TestClient
            from fastapi import FastAPI
            from plugins.ci_stability_system.api import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)

            payload = {
                "node_id": "ci-test-001",
                "status": "-",
                "factors": {
                    "F": False,
                    "C": None,
                    "S": "stable",
                    "R": True,
                },
                "timestamp": int(time.time()),
            }
            response = client.post("/stability/node/analyze", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertIn("weak_nodes", data["data"])
            self.assertFalse(data["data"]["is_valid"])
            self.assertIn("missing_fact", data["data"]["weak_nodes"])
        except ImportError:
            self.skipTest("fastapi або httpx не встановлено — пропускаємо API-тест")

    def test_api_stabilize_endpoint_adaptive(self):
        """POST /stability/node/stabilize з mode=adaptive → статус '+'."""
        try:
            from fastapi.testclient import TestClient
            from fastapi import FastAPI
            from plugins.ci_stability_system.api import router

            app = FastAPI()
            app.include_router(router)
            client = TestClient(app)

            payload = {
                "node": {
                    "node_id": "ci-test-002",
                    "status": "-",
                    "factors": {
                        "F": True,
                        "C": "local",
                        "S": "unstable",
                        "R": True,
                    },
                    "timestamp": int(time.time()),
                },
                "mode": "adaptive",
            }
            response = client.post("/stability/node/stabilize", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["data"]["status"], "+")
        except ImportError:
            self.skipTest("fastapi або httpx не встановлено — пропускаємо API-тест")


if __name__ == "__main__":
    unittest.main(verbosity=2)
