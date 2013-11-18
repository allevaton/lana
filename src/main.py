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
                
                br['username'] = username
                br['password'] = password

                # Clear the password you entered
                # I sure hope this isn't your actual password
                password = 'cats'
                
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

def find_data():
    pass

# Let the fun begin!
if __name__ == '__main__':
    # Need to login first
    if login():
        find_data()
