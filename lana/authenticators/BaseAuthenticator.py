from abc import abstractmethod

import requests


class BaseAuthenticator():
    def __init__(self, url):
        self._session = requests.Session()
        self._login_url = url
        self._is_auth = False
        requests.packages.urllib3.disable_warnings()

    @property
    def is_auth(self):
        if self._session:
            return self._is_auth
        else:
            return False

    @property
    def session(self):
        return self._session

    @abstractmethod
    def authenticate(self, username, password, **kwargs):
        pass

    def post(self, *args, **kwargs):
        return self._session.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self._session.put(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._session.get(*args, **kwargs)

    def close(self):
        self._session.close()
