import requests
import urllib.parse
import json
import pandas as pd
from ecommercetools.utilities.http import get_source as _get_source


def get_knowledge_graph(api_key: str,
                        query: str,
                        output="dataframe"):
    """Return a Google Knowledge Graph for a given query.

    Args:
        api_key (string): Google Knowledge Graph API key.
        query (string): Term to search for.
        output (string, optional): Output format (dataframe, or json).

    Returns:
        response (object): Knowledge Graph response object in JSON format.
    """

    endpoint = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': api_key,
    }

    url = endpoint + '?' + urllib.parse.urlencode(params)
    response = _get_source(url)

    if output == "json":
        return json.loads(response.text)
    else:
        return pd.json_normalize(json.loads(response.text), record_path='itemListElement')
