#!/bin/python2
#
#   Class Data Scraper
#
#   An abstract class that scrapes ClassData objects from a particular source
#
#

from abc import abstractmethod
from getpass import getpass


class BaseScraper():
    name = 'Unidentified Scraper'
    simple = ''

    _is_auth = False

    @abstractmethod
    def __str__(self):
        """ Returns the name of the scraper
        """
        return self.name

    @abstractmethod
    def connect(self):
        """ Attempts to connect to the data source
        """
        return False

    @abstractmethod
    def disconnect(self):
        """ Disconnects from the data source
        """
        pass

    @abstractmethod
    def authenticate(self, username, password):
        """ Attempts to authenticate the scraper using username and password
        """
        return False

    @abstractmethod
    def scrape_data(self):
        """ TODO design
        """
        return []
