#
#
#

__author__ = 'Nick Allevato'

from getpass import getpass

from bs4 import BeautifulSoup
import requests

from BaseScraper import BaseScraper


class LeopardWebScraper(BaseScraper):
    name = 'Leopard Web Scraper'
    simple = 'wit'

    requires_auth = True
    session = None

    # login_url = 'http://leopardweb.wit.edu'
    login_url = 'https://cas.wit.edu/cas/login'

    def __init__(self, username, password):
        name = ' for ' + self.name if self.name else ''
        if not username:
            username = input('Enter username' + name + ': ')
        if not password:
            password = getpass('Enter password' + name + ': ')

        if self.authenticate(username, password):
            pass
        print('test')

    def authenticate(self, username, password):
        # WIT makes this complicated and requires that a specific identifier is sent along.
        # This identifier is uniquely generated per request and lives in the login page.
        # We need to scrape this out, along with other possible information, before we can post.
        self.session = requests.Session()
        response = self.session.get(self.login_url, verify=False)
        soup = BeautifulSoup(response.text)

        payload = {
            'username': username,
            'password': password
        }

        form = soup.find('form', id='fm1')
        for hidden in form.find_all('input', type='hidden'):
            payload[hidden.attrs['name']] = hidden.attrs['value']

        bigurl = 'https://cas.wit.edu/cas/login?service=https%3A%2F%2Fprodweb2.wit.edu%3A443%2Fssomanager%2Fc%2FSSB'
        response = self.session.post(bigurl, payload, verify=False)

        return False

    def scrape_data(self):
        pass

    def __del__(self):
        pass

    disconnect = __del__


if __name__ == '__main__':
    # run the leopard web scraper
    un = input('Enter username: ')
    pw = getpass('Enter password: ')
    scraper = LeopardWebScraper(un, pw)
    pass
