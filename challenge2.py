#!/usr/bin/env python
#
#    Based off of user input, will image a cloud server and create a
#    new server from this image.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

# Non-configurable code is below
# Statically configured credentials file
credentials_file = os.path.expanduser('~/.rackspace_cloud_credentials')

# Check to make sure we can access the credentials file and authenticate.
try:
	pyrax.set_credential_file(credentials_file)
except e.AuthenticationFailed:
	print ('Authentication Failed: Ensure valid credentials in {}'
            .format(credentials_file))
except e.FileNotFound:
    print ('File Not Found: Make sure a valid credentials file is located at'
		    '{}'.format(credentials_file))

# Initilize pyrax for cloudservers	
cs = pyrax.cloudservers

# Initilize our dictionary of choices
choices = {}

# Get a list of current servers and display them for selection
servers = cs.servers.list()
print "Select a server from which an image will be created."
print servers
for postion, server in enumerate(servers):
    print "{}: {}".format(position, server.name)
    choices[str(position)] = server.id

# Process which server the end user wants to image    
selection = None
while selection not in choices:
    if selection is not None:
        print "   -- Invalid choice"
    selection = raw_input("Enter the number for your choice: ")
print " You selected {}".format(choices[selection])