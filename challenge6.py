#!/usr/bin/env python
#
#    This will create a new CloudFiles container and CDN enable it
#    making the container and its contnets public.

import os
import pyrax
import pyrax.exceptions as e
import sys
import string

# Non-configurable code is below
# Statically configured credentials file
credentials_file = os.path.expanduser('~/.rackspace_cloud_credentials')

db_name = 'db_test'
instance_name = 'Test'

# Check to make sure we can access the credentials file and authenticate.
try:
    pyrax.set_credential_file(credentials_file)
except e.AuthenticationFailed:
    print ('Authentication Failed: Ensure valid credentials in {}'
            .format(credentials_file))
except e.FileNotFound:
    print ('File Not Found: Make sure a valid credentials file is located at'
            '{}'.format(credentials_file))

# Initilize pyrax for cloudfiles
cf = pyrax.cloudfiles

# Get a name for the container to be created
container_name = raw_input("Enter a name for the container: ")
try:
    container = cf.create_container(container_name)
    container.make_public()
    print ('Success! Container {} has been created, and made public on'
            ' the CDN.').format(container_name)
except Exception, e:
    print "Error: {}".format(e)

