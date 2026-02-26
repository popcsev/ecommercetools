import pandas as pd
import pytest

pytest.importorskip('mlxtend')

from ecommercetools.marketing import create_basket_matrix, get_frequent_itemsets, get_association_rules


def _sample_transactions():
    return pd.DataFrame(
        {
            'order_id': [1, 1, 2, 2, 3, 3, 4],
            'sku': ['A', 'B', 'A', 'C', 'A', 'B', 'C'],
            'quantity': [1, 1, 1, 1, 1, 1, 1],
        }
    )


def test_create_basket_matrix_shape_and_values():
    df = _sample_transactions()
    basket = create_basket_matrix(df, order_id_column='order_id', sku_column='sku', quantity_column='quantity')

    assert basket.shape == (4, 3)
    assert basket.loc[1, 'A'] is True
    assert basket.loc[1, 'C'] is False


def test_apriori_and_rules_run():
    df = _sample_transactions()
    itemsets = get_frequent_itemsets(df, min_support=0.25)

    assert not itemsets.empty
    assert 'support' in itemsets.columns

    rules = get_association_rules(itemsets, metric='confidence', min_threshold=0.1)
    assert isinstance(rules, pd.DataFrame)
