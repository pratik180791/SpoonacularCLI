import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RequestHandler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.http_session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 599]
        )
        self.http_session.mount("http://", HTTPAdapter(max_retries=retries))

    def http_get(self, url: str, params: dict) -> dict:
        response = self.http_session.get(url=url, params=params)
        if response.ok:
            return response.json()
        logging.error(f"{response.text} for url {url} and params {params}")
        return {}

    def http_post(self, url, params, data):
        pass


class RequestHandlerException(Exception):
    pass
