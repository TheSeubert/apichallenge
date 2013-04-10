#!/usr/bin/env python
#
#    Uploads a local directory to a Cloud Files container.
#    If the container does not exist, it will be created.

import os
import pyrax
import pyrax.exceptions as e
import sys
import argparse
from time import sleep

# Non-configurable code is below
# Statically configured credentials file
credentials_file = os.path.expanduser('~/.rackspace_cloud_credentials')

# Configure arguments to run this script
parser = argparse.ArgumentParser(description='Upload a directory to Cloud '
                                    'Files.')
parser.add_argument('directory', metavar='directory', type=str,
                   help='A directory to upload')
parser.add_argument('container', type=str,
                   help='Name of Cloud Files container to use. If this '
                        'does not exist, it will be created.')
# Set varaibles to be used through the program
args = parser.parse_args()
directory = args.directory
container = args.container

# Simple check if the directory exist or not
if not os.path.isdir(directory):
    print 'Error: {} is not a directory!'.format(directory)
    sys.exit()

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

# Perform the upload with an exception check
try:
    print ('Uploading contents of {} to container {}'
            .format(directory, container))
    upload_key, total_bytes = cf.upload_folder(directory, container=container)
except e.FolderNotFound:
    print 'Error: Directory {} does not exist'.format(directory)

# We initilize our upload variable at 0%
uploaded = 0
# Count the upload bytes total in percent for status to the end user here
while uploaded < total_bytes:
    uploaded = cf.get_uploaded(upload_key)
    progress = (uploaded * 100) / total_bytes
    sys.stdout.write('\rProgress: {:.1f}%'.format(progress))
    sys.stdout.flush()
    sleep(1)

print '\nUpload complete'