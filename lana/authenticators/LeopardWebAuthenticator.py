from bs4 import BeautifulSoup

from lana.authenticators.BaseAuthenticator import BaseAuthenticator
from lana.utils import validate_response


class LeopardWebAuthenticator(BaseAuthenticator):
    """ Gets a valid open session to LeopardWeb, Wentworth's student portal.
    This can be used anywhere else a session may be needed for scraping.

    This class doesn't expose __enter__ and __exit__ methods because this class
    is designed to be stored and interacted with from another class or functions.
    It does not do anything on its own, other than open a session.

    Usage:
    Simply initialize a new instance of the class with a given URL and call the
    "authenticate" method
    >>> auth = LeopardWebAuthenticator('http://leopardweb.wit.edu/')
    >>> if auth.authenticate('username', 'password'):
    ...     pass

    """
    _user_agent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                   'Chrome/43.0.2357.125 Safari/537.36')
    _session_post_args = {
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': _user_agent
        },
        'verify': False,
        'allow_redirects': True
    }

    def __init__(self, url):
        super().__init__(url)

    def authenticate(self, username, password, addheaders=None, **kwargs):
        """ Try to authenticate with the given credentials and parameters.
        :param username: A username (required). Raises ValueError is not specified
        :param password: A user's specific password (required). Raises ValueError is not specified
        :param addheaders: Additional headers that you want passed along.
        :param kwargs: Any additional kwargs will be posted along
        :return: True if authentication is successful, False if failed. Does not raise an exception if
                 failed.
        """
        if not username:
            raise ValueError('A username must be supplied to authenticate')

        if not password:
            raise ValueError('A password must be supplied to authenticate')

        if not addheaders:
            addheaders = {}

        if kwargs:
            self._session_post_args.update(kwargs)
        self._session_post_args.get('headers', {}).update(addheaders)

        response = self.get(self._login_url, **self._session_post_args)
        validate_response(response, 'Could not connect to the leopardweb login, check the URL')
        soup = BeautifulSoup(response.text)

        payload = {
            'username': username,
            'password': password
        }
        del password

        form = soup.find('form', id='fm1')
        if not form:
            return True

        for hidden in form.find_all('input', type='hidden'):
            payload[hidden.attrs['name']] = hidden.attrs['value']

        # TODO generate this from the form's action attribute
        bigurl = 'https://cas.wit.edu/cas/login?service=https%3A%2F%2Fprodweb2.wit.edu%3A443%2Fssomanager%2Fc%2FSSB'
        response = self.post(bigurl, payload, **self._session_post_args)
        del payload
        validate_response(response, 'Could not authenticate, response from post 404\'d')

        soup = BeautifulSoup(response.text)
        if len(soup.find_all('div', class_='errors')) > 0:
            # Authentication failed
            return False

        self._is_auth = True
        return True

    @property
    def post_args(self):
        """
        :return: A list of cached arguments passed with session interaction (post, get, etc.)
        """
        return self._session_post_args
