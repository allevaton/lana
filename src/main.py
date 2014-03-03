#!/bin/python2
#
#   Lana main source
#

from __future__ import print_function
import re, os, sqlite3
from mechanize import Browser
from getpass import getpass
from bs4 import BeautifulSoup
from Class import Class

br = Browser()
br.open( 'http://leopardweb.wit.edu/' ) # Open the page

time_regex = re.compile( r"([0-9]*:?[0-9]*)\s*(am|pm)\s*\-\s*([0-9]*:?[0-9]*)\s*(am|pm)\s*" )
date_regex = re.compile( r"([0-9]*)[/]([0-9]*)\s*\-\s*([0-9]*)[/]([0-9]*)" )

def login():
    if br.title() == 'Sign In':             # Sign in page?
        # Awesome, we're at the sign in page
        for form in br.forms():             # Enumerate the forms. Should only be one
            if form.name == None:           # Since WIT doesn't name their forms...
                br.form = list( br.forms() )[0]

                print( 'Please login to continue.\n' )
                print( 'Don\'t worry, these credentials are safe.' )

                try:
                    username = raw_input( 'Enter username: ' )
                    password = getpass( 'Enter password: ' )
                except (EOFError, KeyboardInterrupt):
                    print( '\nCanceled' )
                    return False

                print( 'Authenticating...' )

                br['username'] = username
                br['password'] = password

                password = None         # Clear the password you entered

                response = br.submit()
                print( '' )

    if br.title() == 'Main Menu':       # Looks like you're already logged in
        # Good to go
        print( 'Good to go! (successfully logged in)' )
        return True
    elif br.title() == 'Sign In':
        # Looks like you entered something wrong. Do it again
        print( 'Looks like you entered something wrong.\n' )
        return login()

def follow_link( link_text ):
    response = None

    for link in br.links():
        if link.text == link_text:
            response = br.follow_link( link )

    return response

def find_data():
    print( 'Loading...' )

    follow_link( 'Student' ).geturl()

    follow_link( 'Registration' ).geturl()

    follow_link( 'Course Section Search' ).geturl()

    br.form = list( br.forms() )[1]     # Save the controls

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
                    val = [label.text  for label in item.get_labels()][0]
                    print( '%d) %s' % (count, val ) )
                    array.append( item.name )
                count += 1              # Add to the counter

    selection = int( raw_input( 'Enter selection: ' ) )

    select_control.value = [array[selection]]
    response = br.submit()              # Submit the form
    year =  str( array[selection] )

    # Course Section Search page
    br.form = list( br.forms() )[1]     # Get the new page's form

    # Submit the form
    response = br.submit( name='SUB_BTN', label='Advanced Search' )
    array = []

    print( response.geturl() )

    # Advanced Search page
    br.form = list( br.forms() )[1]     # Get the new page's form

    for control in br.form.controls:    # Enumerate controls
        if control.type == 'select':    # Find the select form with all the classes
            select_control = control
            for item in control.items:  # Enumerate the items
                array.append( item.name )
            break

    select_control.value = array
    response = br.submit()

    del array

    # So now we're on the big page of classes.
    # use response.read() to get the HTML

    soup = BeautifulSoup( response.read() )
    classes = []                        # Create an array of classes

    # We're about good to insert data into the class database
    # Let's create it
    conn = sqlite3.connect( year + '.db' )
    cur = conn.cursor()

    # TODO clean up this SQL to make more specific types instead of just texts
    cur.execute( """CREATE TABLE IF NOT EXISTS courses
    (
        CID INTEGER PRIMARY KEY,
        CRN INTEGER,
        SUBJECT TEXT,
        COURSE TEXT,
        SECTION TEXT,
        CAMPUS TEXT,
        CREDITS REAL,
        TITLE TEXT,
        WEEKDAYS TEXT,
        START_TIME TEXT,
        END_TIME TEXT,
        CLASS_MAX INTEGER,
        CLASS_CURRENT INTEGER,
        INSTRUCTOR TEXT,
        START_DATE TEXT,
        END_DATE TEXT,
        LOCATION TEXT,
        MISC TEXT
    )""" )

    for tr in soup.find_all( 'tr' ):    # Get all the trs
        c = Class()
        temp = tr.contents              # Split it into the children
        td = []
        for i in temp:
            if i != '\n':
                td.append( i )

        try:
            if td[1]['class'][0] == 'dddefault':    # Great, got a row of data!
                # Time to parse the data
                # Ignore the 0th column, it's just a check box
                # First column is CRN
                crn = td[1].text
                if crn == '':                       # Sometimes it's == ''
                    break                           # So don't bother with them

                #c.crn = crn

                #c.subject = td[2].text
                #c.course = td[3].text
                #c.section = td[4].text
                #c.campus = td[5].text
                #c.credits = float( td[6].text )
                #c.title = td[7].text
                #c.weekdays = list( td[8].text )
                #c.start_time = parse_time( td[9].text, True )
                #c.end_time = parse_time( td[9].text, False )
                #c.class_max = int( td[10].text )
                #c.class_cur = int( td[11].text )
                ## Skip 12; it's class remainder
                #c.instructor = td[13].text
                #c.start_date = parse_date( td[14].text, True )
                #c.end_date = parse_date( td[14].text, False )
                #c.location = td[15].text

                #c.misc = td[16].text

                #print( '---------------------------------------' )
                #print( 'Subject: ', c.subject )
                #print( 'Course: ', c.course )
                #print( 'Section: ', c.section )
                #print( 'Campus: ', c.campus )
                #print( 'Credits: ', c.credits )
                #print( 'Title: ', c.title )
                #print( 'Days: ', c.weekdays )
                #print( 'Start time: ', c.start_time )
                #print( 'End time: ', c.end_time )
                #print( 'Instructor: ', c.instructor )
                #print( 'Start date: ', c.start_date )
                #print( 'End date: ', c.end_date )
                #print( 'Location: ', c.location )

                values = ( int( crn ),
                        td[2].text,
                        td[3].text,
                        td[4].text,
                        td[5].text,
                        float( td[6].text ),
                        td[7].text,
                        td[8].text,
                        parse_time( td[9].text, True ),
                        parse_time( td[9].text, False ),
                        int( td[10].text ),
                        int( td[11].text ),
                        td[13].text,
                        td[14].text.split('-')[0],
                        td[14].text.split('-')[1],
                        td[15].text,
                        td[16].text )

                cur.execute( "INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values )
                #classes.append( c )
            else:
                continue

        except Exception as e:          # Handle if it wasn't a tag
            #print( "Caught an exception: " + str(e.args[0]) )
            pass

    conn.commit()
    # Output the classes array to a file
    #f = open( 'output.class', 'w' )
    #f.close();

    # Test reading them from the file.
    #f = open( 'output.class', 'r' )
    #newClasses = pickle.load( f )
    #print( newClasses[80].instructor )

# is_start: Is this the start time or end time of the class?
def parse_time( instr, is_start ):
    m = time_regex.match( instr )       # Match the regex

    index = 1 if is_start else 3        # Used to simplify is_start idea

    if m:                               # Found a match?
        time = m.group( index )         # Get the time
        time = time.replace( ':', '' )  # Remove that pesky colon
        time = int( time )              # Convert it to an int

        if m.group( index+1 ) == 'pm':  # Is this pm?
            if time < 1200:
                time += 1200            # Convert it to 24 hour time
        return time
    else:
        return None

# is_start: Is this the start date or end date of the class?
def parse_date( instr, is_start ):
    m = date_regex.match( instr )

    index = 1 if is_start else 3

    if m:
        return ( m.group( index ), m.group( index+1 ) )
    else:
        return None

# Let the fun begin!
if __name__ == '__main__':
    if login():                         # Login first
        find_data()                     # Then go find the data

