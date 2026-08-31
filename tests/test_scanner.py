from pathlib import Path

from glancepath.graph.model import NodeKind
from glancepath.parser.scanner import scan_repository


def test_scan_discovers_python_symbols() -> None:
    fixture = Path(__file__).parent / "fixtures" / "sample_repo"
    graph = scan_repository(fixture)

    assert "app:validate_order" in graph.nodes
    assert "app:save_order" in graph.nodes
    assert "app:process_order" in graph.nodes
    assert "app:CheckoutService" in graph.nodes
    assert "app:CheckoutService.checkout" in graph.nodes
    assert graph.nodes["app:CheckoutService.checkout"].kind is NodeKind.METHOD
