from pathlib import Path

from glancepath.graph.model import EdgeKind, NodeKind
from glancepath.parser.scanner import scan_repository


def test_scan_discovers_python_symbols() -> None:
    fixture = Path(__file__).parent / "fixtures" / "sample_repo"
    graph = scan_repository(fixture)

    assert "app:validate_order" in graph.nodes
    assert "app:save_order" in graph.nodes
    assert "app:process_order" in graph.nodes
    assert "app:CheckoutService" in graph.nodes
    assert "app:CheckoutService.checkout" in graph.nodes
    assert "app:CheckoutService._process" in graph.nodes
    assert "helpers:apply_discount" in graph.nodes
    assert graph.nodes["app:CheckoutService.checkout"].kind is NodeKind.METHOD


def test_scan_resolves_basic_python_calls() -> None:
    fixture = Path(__file__).parent / "fixtures" / "sample_repo"
    graph = scan_repository(fixture)

    calls = {
        (edge.source, edge.target)
        for edge in graph.edges
        if edge.kind is EdgeKind.CALLS
    }

    assert ("app:process_order", "app:validate_order") in calls
    assert ("app:process_order", "app:save_order") in calls
    assert ("app:process_order", "helpers:apply_discount") in calls
    assert ("app:CheckoutService.checkout", "app:CheckoutService._process") in calls
    assert ("app:CheckoutService._process", "app:process_order") in calls


def test_unresolved_dynamic_calls_are_not_guessed() -> None:
    fixture = Path(__file__).parent / "fixtures" / "sample_repo"
    graph = scan_repository(fixture)

    expressions = {call.expression for call in graph.unresolved_calls}
    assert "bool" in expressions
    assert not any(edge.target == "bool" for edge in graph.edges)
