#!/bin/python2
#
#   Lana main source
#

from __future__ import print_function

import __builtin__
import os
import re
import sqlite3

from mechanize import Browser
from getpass import getpass
from bs4 import BeautifulSoup

#from Class import Class

br = Browser()

time_regex = re.compile(r'([0-9]*:?[0-9]*)\s*(am|pm)\s*\-\s*'
                        + r'([0-9]*:?[0-9]*)\s*(am|pm)\s*')
date_regex = re.compile(r'([0-9]*)[/]([0-9]*)\s*\-\s*([0-9]*)[/]([0-9]*)')

# input hack
input = getattr(__builtin__, 'raw_input', input)


def login():
    """Handles all web scraping to log in to Wentworth's Lconnect.
    """

    br.open('http://leopardweb.wit.edu/')  # Open the page
    if br.title() == 'Sign In':         # Sign in page?
        # Awesome, we're at the sign in page
        for form in br.forms():         # Enumerate the forms. Should only be 1
            if form.name is None:       # Since WIT doesn't name their forms...
                br.form = list(br.forms())[0]

                print('Please login to continue.\n')
                print('Don\'t worry, these credentials are safe.')

                try:
                    username = input('Enter username: ')
                    password = getpass('Enter password: ')
                except (EOFError, KeyboardInterrupt):
                    print('\nCanceled')
                    return False

                print('Authenticating...')

                br['username'] = username
                br['password'] = password

                password = None         # Clear the password you entered

                br.submit()
                print('')

    if br.title() == 'Main Menu':       # Looks like you're already logged in
        # Good to go
        print('Good to go! (successfully logged in)')
        return True
    elif br.title() == 'Sign In':
        # Looks like you entered something wrong. Do it again
        print('Looks like you entered something wrong.\n')
        return login()


def follow_link(link_text):
    """Follows the requested link much more effectively by string matching
    all the links.

    Keyword arguments:
    link_text -- string: the text of the the link to follow

    Returns:
    mechanize response object
    """

    response = None

    for link in br.links():
        if link.text == link_text:
            response = br.follow_link(link)

    return response


def find_data():
    """Follows webpages through Wentworth's Lconnect to get to the large
    classes webpage, and parses that into a SQLite3 file
    """

    print('Loading...')

    follow_link('Student')

    follow_link('Registration')

    follow_link('Course Section Search')

    br.form = list(br.forms())[1]     # Save the controls

    select_control = None               # We want to save the select control

    array = [' ']

    count = 0
    for control in br.form.controls:    # Enumerate controls in the form
        if control.type == 'select':    # Is it a select control?
            select_control = control    # Yes? Awesome.
            for item in control.items:  # Enumerate all the items
                if count > 0:           # The first one is 'None,' so bypass it
                    # Now get the labels and store the actual
                    # data in the background somewhere
                    val = [label.text for label in item.get_labels()][0]
                    print('%d) %s' % (count, val))
                    array.append(item.name)
                count += 1              # Add to the counter

    selection = int(input('Enter selection: '))

    select_control.value = [array[selection]]
    response = br.submit()              # Submit the form
    year = str(array[selection])

    # Course Section Search page
    br.form = list(br.forms())[1]       # Get the new page's form

    # Submit the form
    response = br.submit(name='SUB_BTN', label='Advanced Search')
    array = []

    #print( response.geturl() )

    # Advanced Search page
    br.form = list(br.forms())[1]     # Get the new page's form

    for control in br.form.controls:    # Enumerate controls
        if control.type == 'select':    # Find the select form with classes
            select_control = control

            for item in control.items:  # Enumerate the items
                array.append(item.name)
            break

    select_control.value = array
    response = br.submit()

    del array

    # So now we're on the big page of classes.
    # use response.read() to get the HTML
    soup = BeautifulSoup(response.read())
    #classes = []                        # Create an array of classes

    # We're about good to insert data into the class database
    # Let's create it if it doesn't exist
    conn = sqlite3.connect(year + '.db')
    cur = conn.cursor()

    # TODO clean up this SQL to make more specific types instead
    # of just texts
    with open('create_table.sql') as f:
        cur.execute(f.read())

    count = 0

    for tr in soup.find_all('tr'):      # Get all the trs
        #c = Class()
        temp = tr.contents              # Split it into the children
        td = []
        for i in temp:
            if i != '\n':
                td.append(i)

        try:
            if td[1]['class'][0] == 'dddefault':    # Great, got a row of data!
                # Time to parse the data
                # Ignore the 0th column, it's just a check box
                # First column is CRN
                crn = td[1].text
                if crn == '':                       # Sometimes it's == ''
                    break                           # So don't bother with them

                # Fixes the CRN unique constraint errors
                count += 1

                # Yeah, this is crazy.
                values = \
                    (
                        count,                  # primary key
                        int(crn),               # crn
                        td[2].text,             # subject
                        td[3].text,             # course
                        td[4].text,             # section
                        td[5].text,             # campus
                        float(td[6].text),      # credits
                        td[7].text,             # title
                        td[8].text,             # weekdays
                        parse_time(td[9].text, True),   # start time
                        parse_time(td[9].text, False),  # end time
                        int(td[10].text),     # class max
                        int(td[11].text),     # class current
                        # This eliminates all stupid whitespace:
                        ' '.join(td[13].text.split()),  # instructor
                        td[14].text.split('-')[0],  # start date
                        td[14].text.split('-')[1],  # end date
                        td[15].text,            # location
                        td[16].text             # misc
                    )

                # Insert the data into the database
                cur.execute('INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,'
                            + '?,?,?,?,?,?,?,?,?,?)''', values)
            else:
                continue

        except Exception:       # Handle if it wasn't a tag
            #print( 'Error: {0} '.format( e ) )
            pass

    # Commit the SQL
    conn.commit()
    conn.close()


def get_classes(database):
    """Get classes based on user preferences. This will only pull the
    classes and return an array of rows.

    Keyword arguments:
    database -- file string: the SQLite3 *.db file to reference
    """

    if not os.path.isfile(database):
        return None

    conn = sqlite3.connect(database)
    c = conn.cursor()

    # This is the temporary way of doing it
    f = open('classes.txt')

    courses = []

    # Courses and subjects are separated in the file by space
    # and line
    for line in f:
        s = line.split(' ')

        # trim out the attached \n
        courses.append((s[0], s[1].replace('\n', '')))

    rows = []

    # Let's print out the classes for those types
    for subj_course in courses:
        c.execute('SELECT * FROM courses WHERE SUBJECT=? AND COURSE=?',
                  subj_course)
        rows.append(c.fetchall())

    # Return the array of rows
    return rows


def parse_time(instr, is_start):
    """Parses the given `instr' time string and returns a better one

    Keyword arguments:
    instr -- string: the input time string
    is_start -- boolean: determines whether or not this is a start time or
                end time. This matters for regex parsing.
    """

    m = time_regex.match(instr)         # Match the regex

    index = 1 if is_start else 3        # Used to simplify is_start idea

    if m:                               # Found a match?
        time = m.group(index)           # Get the time
        time = time.replace(':', '')    # Remove that pesky colon
        time = int(time)                # Convert it to an int

        if m.group(index + 1) == 'pm':  # Is this pm?
            if time < 1200:
                time += 1200            # Convert it to 24 hour time
        return time
    else:
        return None


def parse_date(instr, is_start):
    """Parses the given `instr' date string and returns a tuple of month
    and date

    Keyword arguments:
    instr -- string: the input date string
    is_start -- boolean: determines whether or not this is a start date or
                end date. This matters for regex parsing.
    """

    m = date_regex.match(instr)

    index = 1 if is_start else 3

    if m:
        return (m.group(index), m.group(index+1))
    else:
        return None

# Let the fun begin!
if __name__ == '__main__':
    # Login and find the data
    if login():
        find_data()

    print('Pulling these classes for you')
    get_classes('201420.db')
