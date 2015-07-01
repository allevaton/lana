from abc import abstractmethod

import requests


class BaseAuthenticator():
    def __init__(self, url):
        """ Initialize the authenticator
        :param url: Takes a login URL. This is so you don't have to pass it constantly.
        :return:
        """
        self._session = requests.Session()
        self._login_url = url
        self._is_auth = False
        requests.packages.urllib3.disable_warnings()

    @property
    def is_auth(self):
        """
        :return:Returns whether or not this authenticator has been authenticated
        """
        if self._session:
            return self._is_auth
        else:
            return False

    @property
    def session(self):
        """
        :return: Returns the session object
        """
        return self._session

    @abstractmethod
    def authenticate(self, username, password, **kwargs):
        """ Implementation-specific and arguments may differ
        """
        pass

    def post(self, *args, **kwargs):
        """ Post the given arguments to this session. The arguments are the same as requests.post()
        :return: A (hopefully) valid requests.Response() object
        """
        return self._session.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """ Put the given arguments to this session. The arguments are the same as requests.put()
        :return: A (hopefully) valid requests.Response() object
        """
        return self._session.put(*args, **kwargs)

    def get(self, *args, **kwargs):
        """ Get a response from the URL from the session. The arguments are the same as requests.get()
        :return: A (hopefully) valid requests.Response() object
        """
        return self._session.get(*args, **kwargs)

    def close(self):
        """ Close and disconnect the session.
        :return:
        """
        self._session.close()
