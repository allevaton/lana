#!/bin/python2
#
#   Lana main source
#

import re, mechanize
from getpass import getpass

br = mechanize.Browser()
#br.set_all_readonly( False )           # Everything is writable
br.open( 'http://leopardweb.wit.edu/' ) # Open the page

def login():
    if br.title() == 'Sign In':             # Sign in page?
        # Awesome, we're at the sign in page
        for form in br.forms():             # Enumerate the forms. Should only be one
            if form.name == None:           # Since WIT doesn't name their forms...
                br.form = list( br.forms() )[0]
                
                print 'Please login to continue.\n'
                print 'Don\'t worry, these credentials are safe.'
                
                try:
                    username = raw_input( 'Enter username: ' )
                    password = getpass( 'Enter password: ' )
                except EOFError as e:
                    print '\nCanceled'
                    return False
                except KeyboardInterrupt as e:
                    print '\nCanceled'
                    return False
                finally:
                    print 'Authenticating...'
                
                br['username'] = username
                br['password'] = password

                # Clear the password you entered
                # I sure hope this isn't your actual password
                password = None
                
                response = br.submit()
                print ''
                
    if br.title() == 'Main Menu':            # Looks like you're already logged in
        # Good to go
        print 'Good to go! (successfully logged in)'
        return True
    elif br.title() == 'Sign In':
        # Looks like you entered something wrong. Do it again
        print 'Looks like you entered something wrong.\n'
        login()

def follow_link( link_text ):
    response = None

    for link in br.links():
        if link.text == link_text:
            response = br.follow_link( link )

    return response

def find_data():
    print 'Loading...'

    follow_link( 'Student' ).geturl()
    
    follow_link( 'Registration' ).geturl()
    
    follow_link( 'Course Section Search' ).geturl()

    br.form = list( br.forms() )[1]     # Save the controls
    
    select_control = None               # We want to save the control
    
    array = [' ']

    count = 0
    for control in br.form.controls:    # Enumerate controls in the form
        if control.type == 'select':    # Is it a select control?
            select_control = control
            for item in control.items:  # Enumerate all the items
                if count > 0:           # The first one is 'None,' so bypass it
                    val = [label.text  for label in item.get_labels()][0]
                    print '%d) %s' % (count, val )
                    array.append( item.name )
                count += 1              # Add to the counter
    
    selection = int( raw_input( 'Enter selection: ' ) )
    
    select_control.value = [array[selection]]

    response = br.submit()

    print response.read()

# Let the fun begin!
if __name__ == '__main__':
    # Need to login first
    if login():
        find_data()
