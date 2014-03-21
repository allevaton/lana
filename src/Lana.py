#!/bin/python2
#
#   Lana Class
#
#   Main class for the Lana system
#
#

from __future__ import print_function
from LconnectScraper import LconnectScraper
from getpass import getpass
import __builtin__

# Python3's input() hack
input = getattr(__builtin__, 'raw_input', input)


class Lana:
    SCRAPERS = {'lconnect': LconnectScraper}

    def __init__(self, scraper):
        """
        Takes the name of the scraper to instantiate
        """

        # Instantiate a scraper based on the name given
        self._scraper = Lana.SCRAPERS.get(scraper, LconnectScraper)()

    def run(self):
        print("Connecting Scraper '%s'..." % self._scraper.getName())
        if self._scraper.connect():
            print('Connected Successfully!')
            if self._scraper.requiresAuthentication():
                print('Scraper Requires Authentication.')
                try:
                    username = input('Enter username: ')
                    password = getpass('Enter password: ')
                    print('Authenticating...')
                    if self._scraper.authenticate(username, password):
                        print('Authentication Successful!')
                    else:
                        print('Authentication Failed!')
                except (EOFError, KeyboardInterrupt):
                    print('\nCancelled.')
            print('Disconnecting Scraper...')
            self._scraper.disconnect()
            print('Disconnected.')

if __name__ == '__main__':
    lana = Lana('lconnect')
    lana.run()
