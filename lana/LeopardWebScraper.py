import json
import os
import re
import sys
from collections import defaultdict
from getpass import getpass
from urllib import parse

from bs4 import BeautifulSoup

from lana.BaseScraper import BaseScraper
from lana.utils import dict_safe_update, validate_response
from lana.authenticators.LeopardWebAuthenticator import LeopardWebAuthenticator


class LeopardWebScraper(BaseScraper):
    name = 'Leopard Web Scraper'
    simple = 'wit'

    _scraping_term = None

    _login_url = 'http://leopardweb.wit.edu'

    def __init__(self, term):
        self._scraping_term = term
        self._authenticator = LeopardWebAuthenticator(self._login_url)

    def generate_qs(self):
        # need to generate and save the new query string
        if not self._authenticator.is_auth:
            raise PermissionError('You must be connected to generate a query string')

        payload = {
            'p_calling_proc': 'P_CrseSearch',
            'p_term': self._scraping_term
        }

        response = self._authenticator.post('https://prodweb2.wit.edu/SSBPROD/bwckgens.p_proc_term_date',
                                            payload, **self._authenticator.post_args)
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

    def authenticate(self, username, password):
        return self._authenticator.authenticate(username, password)

    def scrape_data(self, outfile_name=''):
        if not self._authenticator.is_auth:
            raise PermissionError('You must be authenticated to scrape the data')

        payload = parse.parse_qs(self.get_qs(), keep_blank_values=True)

        response = self._authenticator.post('https://prodweb2.wit.edu/SSBPROD/bwskfcls.P_GetCrse_Advanced',
                                            payload, **self._authenticator.post_args)
        validate_response(response, 'Scraping failed: could not post to advanced search')
        soup = BeautifulSoup(response.text)

        whitespace_re = re.compile(r'\s+')
        credit_decimal_re = re.compile(r'([0-9]+)\.0+')
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
            row = dict(zip(headers, [t.text.strip() for t in c.find_all('td', class_='dddefault')]))

            instructors = row['instructor'].split(',')
            instructors = ', '.join([prof.split('(')[0].strip() for prof in instructors])
            instructors = whitespace_re.sub(' ', instructors)
            row['instructor'] = instructors

            # TODO support for roman numerals staying capitalized
            row['title'] = row['title'].title()
            row['time'] = whitespace_re.sub('', row['time'])

            # only care about the campus when it's not on WIT
            if row['cmp'] == 'WIT':
                row.pop('cmp')

            if not row['attribute']:
                row.pop('attribute')

            # get rid of those pesky decimals on whole-number credit courses
            if credit_decimal_re.match(row['cred']):
                row['cred'] = credit_decimal_re.sub(r'\1', row['cred'])

            # don't need to keep track of the remainder, we can easily calculate this by subtracting act from cap
            # rem = cap - act
            row.pop('rem')

            data.append(row)

        data = self.cleanup_data(data)

        if outfile_name:
            with open(outfile_name, 'w') as fp:
                fp.write(json.dumps(data, separators=(',', ':')))

        return data

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

    def disconnect(self):
        self._authenticator.close()


if __name__ == '__main__':
    # run the leopard web scraper
    un = input('Enter username: ')
    pw = getpass('Enter password: ')

    scraper = LeopardWebScraper("201601")
    if scraper.authenticate(un, pw):
        scraper.scrape_data('wit.json')
    else:
        print('Authentication failed', file=sys.stderr)
