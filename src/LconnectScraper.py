#!/bin/python
#
#   Lconnect Scraper
#
#   An implementation of ClassDataScraper. Scrapes ClassData from Lconnect
#
#

from ClassDataScraper import ClassDataScraper
import http.cookiejar
import urllib.request
import urllib.parse
import html.parser


class LconnectScraper(ClassDataScraper):
    LCONNECT_URL = 'http://leopardweb.wit.edu/'
    USERAGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.1) ' \
                + 'Gecko/20100122 firefox/3.6.1'

    # Saves the value of the tag that is passed in the constructor
    class _PageDataParser(html.parser.HTMLParser):
        def __init__(self, tagName):
            self._tagName = tagName
            self._data = None
            self._lastOpenTag = None
            super().__init__()

        def getData(self):
            return self._data

        def handle_starttag(self, tag, attrs):
            self._lastOpenTag = tag

        def handle_data(self, data):
            if self._lastOpenTag == self._tagName and self._data is None:
                self._data = data

    class _LoginPageParser(html.parser.HTMLParser):
        def __init__(self):
            self._data = dict()
            super().__init__()

        def getData(self, name):
            return str(self._data.get(name))

        def _getValueFromAttrs(self, attrs, name):
            values = [x for x in attrs if x[0] == name]
            if len(values) > 0:
                return values[0][1]
            else:
                return None

        def handle_starttag(self, tag, attrs):
            if tag == 'form':
                self._data['postUrl'] = self._getValueFromAttrs(attrs, 'action')
            elif tag == 'input':
                tagName = self._getValueFromAttrs(attrs, 'name')
                if tagName == 'lt':
                    self._data['lt'] = self._getValueFromAttrs(attrs, 'value')
                elif tagName == 'execution':
                    self._data['execution'] = self._getValueFromAttrs(attrs, 'value')
                elif tagName == '_eventId':
                    self._data['_eventId'] = self._getValueFromAttrs(attrs, 'value')

    def __init__(self):
        # Create a cookie jar and a browser
        self._cookieJar = http.cookiejar.CookieJar(http.cookiejar.DefaultCookiePolicy())
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookieJar))

        self._opener.addheaders = [('User-agent', LconnectScraper.USERAGENT)]
        self._connection = None

    def getName(self):
        return 'Lconnect Scraper'

    def connect(self):
        """Attempts to connect to the data source
        """
        try:
            # Try to open a connection. 8 Second timeout
            self._connection = self._opener.open(LconnectScraper.LCONNECT_URL, timeout=8)
            return True
        except URLError:
            return False

    def disconnect(self):
        """Disconnects from the data source
        """
        if self._connection:
            self._connection.close()

    def requiresAuthentication(self):
        """Returns whether or not the scraper requires authentication
        information
        """

        return True

    def authenticate(self, username, password):
        """Attempts to authenticate the scraper using username and password
        """

        loginParser = LconnectScraper._LoginPageParser()
        loginParser.feed(self._connection.read().decode())

        postData = urllib.parse.urlencode(
            {'lt': loginParser.getData('lt'),
             'execution': loginParser.getData('execution'),
             '_eventId': loginParser.getData('_eventId'),
             'username': username,
             'password': password})

        postData = postData.encode('utf-8')
        postUrl = urllib.parse.urljoin('https://cas.wit.edu', loginParser.getData('postUrl'))
        print('Post URL: %s' % (postUrl))
        request = urllib.request.Request(postUrl)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')

        response = self._opener.open(request, postData, timeout=8)
        responseText = response.read().decode('utf-8', errors='ignore')
        titleParser = LconnectScraper._PageDataParser('title')
        titleParser.feed(responseText)

        titleValue = titleParser.getData()

        return titleValue == 'Main Menu'

    def getClassData(self):
        """Returns a list of ClassData objects
        """

        return []
