import pytest
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "metrics", Path(__file__).resolve().parents[1] / "ecommercetools" / "utilities" / "metrics.py"
)
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


def test_product_consumption_rate():
    total_items = 10
    total_orders = 4
    result = metrics.product_consumption_rate(total_items, total_orders)
    assert result == pytest.approx(2.5)
