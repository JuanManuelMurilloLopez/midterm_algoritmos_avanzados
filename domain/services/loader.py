import requests


def load_season_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
