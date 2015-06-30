import json
import os
import sys
from collections import defaultdict
from getpass import getpass
from urllib import parse

import requests

from bs4 import BeautifulSoup

from lana.BaseScraper import BaseScraper
from lana.utils import dict_safe_update, validate_response

requests.packages.urllib3.disable_warnings()


class LeopardWebScraper(BaseScraper):
    name = 'Leopard Web Scraper'
    simple = 'wit'

    _session = None
    _scraping_term = None

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

    def __init__(self, term):
        self._scraping_term = term
        self._session = requests.Session()

    def generate_qs(self):
        # need to generate and save the new query string
        if not self._session:
            raise ConnectionError('You must be connected to generate a query string')

        payload = {
            'p_calling_proc': 'P_CrseSearch',
            'p_term': self._scraping_term
        }

        response = self._session.post('https://prodweb2.wit.edu/SSBPROD/bwckgens.p_proc_term_date',
                                      payload, **self._session_post_args)
        validate_response(response, 'Generating query string failed, could not post to search page')
        soup = BeautifulSoup(response.text)
        form = soup.find_all('form')[1]

        data = defaultdict(list)
        for h in form.find_all('input', type='hidden'):
            data[h.attrs.get('name')].append(h.attrs.get('value'))

        select = form.find('select', attrs={'name': 'sel_subj'})
        for option in select.find_all('option'):
            data['sel_subj'].append(option.attrs.get('value'))

        return parse.urlencode(data)

    def get_qs(self):
        """ Gets the magic query string for posting and getting the list of all classes
        """
        name = '%s.%s.qs' % (self.simple, self._scraping_term)
        if os.path.exists(name):
            with open(name) as fp:
                return fp.readline()
        else:
            qs = self.generate_qs()
            with open(name, 'w') as fp:
                return fp.writelines([qs])

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
        validate_response(response, 'Could not connect to the leopardweb login, check the URL')
        soup = BeautifulSoup(response.text)

        payload = {
            'username': username,
            'password': password
        }

        form = soup.find('form', id='fm1')
        if not form:
            return True

        for hidden in form.find_all('input', type='hidden'):
            payload[hidden.attrs['name']] = hidden.attrs['value']

        bigurl = 'https://cas.wit.edu/cas/login?service=https%3A%2F%2Fprodweb2.wit.edu%3A443%2Fssomanager%2Fc%2FSSB'
        response = self._session.post(bigurl, payload, **self._session_post_args)
        del password
        validate_response(response, 'Could not authenticate, response 404\'d')

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
        validate_response(response, 'Scraping failed: could not post to advanced search')
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
            d = self.cleanup_entry(dict(zip(headers, [t.text.strip() for t in c.find_all('td', class_='dddefault')])))
            data.append(d)

        data = self.cleanup_data(data)

        if outfile_name:
            with open(outfile_name, 'w') as fp:
                fp.write(json.dumps(data))

        return data

    def cleanup_entry(self, class_row):
        # TODO there may be more instructors split by commas; handle this
        class_row['instructor'] = class_row['instructor'].split('(')[0].strip()
        class_row['attribute'] = class_row['attribute'].strip()
        class_row['title'] = class_row['title'].title()
        return class_row

    def cleanup_data(self, data):
        prev = {}
        for entry in data:
            del entry['select']

            # Sometimes, classes have empty entries which means they are an extension of
            # the previous class. We can easily handle this by discovering an empty class,
            # and updating it with the previous.
            if not entry['subj'] and not entry['crse'] and not entry['sec']:
                dict_safe_update(entry, prev)

            prev = entry

        return data

    def __del__(self):
        pass


if __name__ == '__main__':
    # run the leopard web scraper
    # un = input('Enter username: ')
    # pw = getpass('Enter password: ')

    scraper = LeopardWebScraper("201601")
    if scraper.authenticate():
        scraper.scrape_data('wit.json')
