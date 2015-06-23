#
#
#

import json
import os
import sys
from getpass import getpass
from urllib import parse

from bs4 import BeautifulSoup
import requests

from BaseScraper import BaseScraper


class LeopardWebScraper(BaseScraper):
    name = 'Leopard Web Scraper'
    simple = 'wit'

    _session = None

    _login_url = 'http://leopardweb.wit.edu'
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

    _is_auth = False

    def __init__(self):
        pass

    def get_qs(self):
        """ Gets the magic query string for posting and getting the list of all classes
        """
        n = self.simple + '.qs'
        if os.path.exists(n):
            with open(n) as fp:
                return fp.readline()
        else:
            # need to generate and save the new query string
            if not self._session:
                raise ConnectionError('You must be connected to generate a query string')

                # TODO finish the ability to generate a query string

    def connect(self):
        self._session = requests.Session()
        return True

    def authenticate(self, username='', password=''):
        # WIT makes this complicated and requires that a specific identifier is sent along.
        # This identifier is uniquely generated per request and lives in the login page.
        # We need to scrape this out, along with other possible information, before we can post.
        # if not self._session:
        #     raise ConnectionError('You must be connected to authenticate')
        name = ' for ' + self.name if self.name else ''
        if not username:
            username = input('Enter username' + name + ': ')
        if not password:
            password = getpass('Enter password' + name + ': ')

        response = self._session.get(self._login_url, **self._session_post_args)
        soup = BeautifulSoup(response.text)

        payload = {
            'username': username,
            'password': password
        }

        form = soup.find('form', id='fm1')
        for hidden in form.find_all('input', type='hidden'):
            payload[hidden.attrs['name']] = hidden.attrs['value']

        bigurl = 'https://cas.wit.edu/cas/login?service=https%3A%2F%2Fprodweb2.wit.edu%3A443%2Fssomanager%2Fc%2FSSB'
        response = self._session.post(bigurl, payload, **self._session_post_args)
        del password

        soup = BeautifulSoup(response.text)
        if len(soup.find_all('div', class_='errors')) > 0:
            print('Authenticating %s failed' % self.name, file=sys.stderr)
            return False

        self._is_auth = True
        return True

    def scrape_data(self, outfile_name=''):
        payload = parse.parse_qs(self.get_qs(), keep_blank_values=True)

        response = self._session.post('https://prodweb2.wit.edu/SSBPROD/bwskfcls.P_GetCrse_Advanced',
                                      payload, **self._session_post_args)
        soup = BeautifulSoup(response.text)
        data = []
        headers = []
        for c in soup.find(class_='datadisplaytable').find_all('tr'):
            if not headers and c.find('th', class_='ddheader'):
                headers = [head.text.lower() for head in c.find_all('th', class_='ddheader')]
                headers = [h.split('(')[0].strip() for h in headers]
                continue

            if not c.find('td', class_='dddefault'):
                continue

            # Yes, these are the droids you were looking for.
            d = self.cleanup_entry(dict(zip(headers, [t.text for t in c.find_all('td', class_='dddefault')])))
            data.append(d)

        data = self.cleanup_data(data)

        if outfile_name:
            with open(outfile_name, 'w') as fp:
                fp.write(json.dumps(data))

        return data

    def cleanup_entry(self, class_row):
        class_row['instructor'] = class_row['instructor'].split('(')[0].strip()
        class_row['attribute'] = class_row['attribute'].strip()
        return class_row

    def cleanup_data(self, data):
        for entry in data:
            del entry['select']

        return data

    def __del__(self):
        pass


if __name__ == '__main__':
    # run the leopard web scraper
    # un = input('Enter username: ')
    # pw = getpass('Enter password: ')

    scraper = LeopardWebScraper()
    if scraper.connect() and scraper.authenticate():
        scraper.scrape_data('wit.json')
