#!/bin/python2
#
#   Class Data Scraper
#
#   An abstract class that scrapes ClassData objects from a particular source
#
#

from abc import abstractmethod


class BaseScraper():
    @abstractmethod
    def __str__(self):
        """ Returns the name of the scraper
        """
        return 'Undefined Scraper'

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
    def requires_auth(self):
        """ Returns whether or not the scraper requires authentication information
        """
        return False

    @abstractmethod
    def authenticate(self, username, password):
        """ Attempts to authenticate the scraper using username and password
        """
        return False

    @abstractmethod
    def class_data(self):
        """ Returns a list of ClassData objects
        """
        return []
