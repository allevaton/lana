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

    class _LoginPageParser(html.parser.HTMLParser):
        def __init__(self):
            self._data = dict()
            html.parser.HTMLParser.__init__(self)

        def getData(self, name):
            return str(self._data.get(name))

        def _getValueFromAttrs(self, attrs, name):
            values = [ x for x in attrs if x[0] == name ]
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
                    self._data['lt'] = self._getValueFromAttrs(attrs,'value')
                elif tagName == 'execution':
                    self._data['execution'] = self._getValueFromAttrs(attrs,'value')
                elif tagName == '_eventId':
                    self._data['_eventId'] = self._getValueFromAttrs(attrs,'value')

    def __init__(self):
        # Create a cookie jar and a browser
        self._cookieJar = http.cookiejar.CookieJar(http.cookiejar.DefaultCookiePolicy())
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookieJar))

        self._opener.addheaders = [('User-agent', LconnectScraper.USERAGENT)]
        self._connection = None

    def getName(self):
        return "Lconnect Scraper"

    def connect(self):
        """
        Attempts to connect to the data source
        """
        try:
            # Try to open a connection. 8 Second timeout
            self._connection = self._opener.open(LconnectScraper.LCONNECT_URL, timeout=8)
            return True
        except URLError:
            return False

    def disconnect(self):
        """
        Disconnects from the data source
        """
        if self._connection:
            self._connection.close()

    def requiresAuthentication(self):
        """
        Returns whether or not the scraper requires authentication information
        """

        return True

    def authenticate(self, username, password):
        """
        Attempts to authenticate the scraper using username and password
        """

        loginParser = LconnectScraper._LoginPageParser()
        loginParser.feed(self._connection.read().decode())

        postData = urllib.parse.urlencode({'lt' : loginParser.getData('lt'),
                                            'execution' : loginParser.getData('execution'),
                                            '_eventId' : loginParser.getData('_eventId'),
                                            'username' : username,
                                            'password' : password })

        postData = postData.encode('utf-8')
        postUrl = urllib.parse.urljoin('https://cas.wit.edu', loginParser.getData('postUrl'))
        print("Post URL: %s" % postUrl)
        request = urllib.request.Request(postUrl)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')

        response = self._opener.open(request, postData, timeout=8)
        print(response.read().decode('utf-8', errors='ignore'))
        return

        # If we're on the sign in page, try to sign in
        if self._browser.title() == 'Sign In':
            for form in self._browser.forms():
                if form.name is None:
                    self._browser.form = list(self._browser.forms())[0]
                    self._browser['username'] = username
                    self._browser['password'] = password

                    self._browser.submit()

        # If the browser's title is 'Main Menu',
        # we've either successfully logged in, or we were already
        if self._browser.title() == 'Main Menu':
            return True
        else:
            return False

    def getClassData(self):
        """
        Returns a list of ClassData objects
        """

        return []
