import requests

from flask import request, url_for

from config import BASE_API_URL
from security import Token


def macro_collections():
    response = requests.get(f"{BASE_API_URL}/collection", headers=Token.get_header_access())

    try:
        collections = response.json()['collections']
    except KeyError:
        return []

    return collections


def redirect_url(default='home.home'):
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)
