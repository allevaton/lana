#!/bin/python
#
#   Lana Class
#
#   Main class for the Lana system
#
#

from LconnectScraper import LconnectScraper
from getpass import getpass

class Lana:
    """Main Lana class for abstraction
    TODO DOCS?
    """
    SCRAPERS = {'lconnect': LconnectScraper}

    _scraper = None

    def __init__(self, scraper):
        """Takes the name of the scraper to instantiate
        """

        # Instantiate a scraper based on the name given
        try:
            self._scraper = (Lana.SCRAPERS[scraper])()
        except (KeyError):
            print('Invalid scraper \'%s\'' % (scraper))

    def run(self):
        """Runs the specified scraper module
        """

        # Make sure the scraper isn't None
        if self._scraper is None:
            return None

        print("Connecting Scraper '%s'..." % (self._scraper.getName()))

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
                    print('\n Canceled .')

            print('Disconnecting Scraper...')

            self._scraper.disconnect()

            print('Disconnected.')

if __name__ == '__main__':
    lana = Lana('lconnect')
    lana.run()
