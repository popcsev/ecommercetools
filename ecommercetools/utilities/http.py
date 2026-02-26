"""
HTTP utilities for web scraping and fetching content.
"""

import requests
from requests_html import HTMLSession


def get_source(url: str):
    """Return the source code for the provided URL.

    Args:
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html.

    Raises:
        RuntimeError: If the request fails or returns a non-200 status code.
    """

    try:
        session = HTMLSession()
        response = session.get(url)

        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            raise RuntimeError('Error: Too many requests. Google has temporarily blocked you. Try again later.')
        else:
            raise RuntimeError(f'Error: HTTP {response.status_code} when fetching {url}')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
