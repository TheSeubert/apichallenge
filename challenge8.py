#!/usr/bin/env python
#
#    This script will create a new CDN enables Cloud Files container
#    with a static HTML index page that can be viewed directly like
#    s standard webserver. A CNAME to the container is also created.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

# User configurable settings

# Set varaibles to be used through the program
container_name = "StaticWebsite"

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
cf = pyrax.cloudfiles

# Create the specified container
try:
    container = cf.create_container(container_name)
    container.make_public()
    print ('Success! Container {} has been created, and made public on'
            ' the CDN.').format(container_name)
except Exception, e:
    print "Error: {}".format(e)

# We set the static index page to be served
try:
    index_file = "index.html"
    index_data =    "<html>"
                    "<head>"
                    "<title> My Test Page</title>"
                    "</head>"
                    "<body bgcolor=\"white\" text=\"blue\">"
                    "<h1> My first page </h1>"
                    "A static index page does exist here?"
                    "</body>"
                    "</html>"


    container.set_web_index_page(index_file)
    container.store_object(index_file,index_data,content_type="text/html")
    print "Complete! A static index page has been created. Visit {} to test."
            .format(container.cdn_uri)
except Exception, e:
    print "Error: {}".format(e)
    
# We create CNAME records to make the URL more user friendly
container_name = raw_input("Enter the CNAME you want to create: ")