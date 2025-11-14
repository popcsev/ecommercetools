import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

pandas = pytest.importorskip('pandas')
numpy = pytest.importorskip('numpy')

from ecommercetools.utilities import tools


def test_get_previous_value_returns_previous_value():
    df = pandas.DataFrame({'group': ['A', 'A', 'A', 'B', 'B'],
                           'value': [2, 1, 3, 1, 2]})
    prev = tools.get_previous_value(df, 'group', 'value')
    expected = pandas.Series([1.0, numpy.nan, 2.0, numpy.nan, 1.0])
    pandas.testing.assert_series_equal(prev, expected)
