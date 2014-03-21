#!/bin/python2
#
#   Class Data Scraper
#
#   An abstract class that scrapes ClassData objects from a particular source
#
#

from abc import ABCMeta, abstractmethod


class ClassDataScraper:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getName(self):
        """
        Returns the name of the scraper
        """

        return "Undefined Scraper"

    @abstractmethod
    def connect(self):
        """
        Attempts to connect to the data source
        """

        return False

    @abstractmethod
    def disconnect(self):
        """
        Disconnects from the data source
        """

    @abstractmethod
    def requiresAuthentication(self):
        """
        Returns whether or not the scraper requires authentication information
        """

        return False

    @abstractmethod
    def authenticate(self, username, password):
        """
        Attempts to authenticate the scraper using username and password
        """

        return False

    @abstractmethod
    def getClassData(self):
        """
        Returns a list of ClassData objects
        """

        return []
