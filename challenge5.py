#!/usr/bin/env python
#
#    This will create a cloud database instance with, 512MB RAM and 1GB
#    disk space. A user of admin is created with a random password.

import os
import pyrax
import pyrax.exceptions as e
import sys
import time
from time import sleep
from time import gmtime, strftime
import string
import random

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

# Initilize pyrax for cloud databases
dbass = pyrax.cloud_databases

# Try to create an instance
print 'Creating a 512MB Database Instance with 1GB of Disk Space.'
try:
    instance = dbass.create('Test', flavor=1, volume=1)
except e:
    print 'Error creating instance.'
    sys.exit()

instance_info = dbass.get(instance.id)

while instance_info.status != 'ACTIVE':
        sleep(10)
        now = strftime('%Y-%m-%d %H:%M:%S UTC', gmtime())
        instance_info = dbass.get(instance.id)
        sys.stdout.write('\rInstance Status at {}: {}'
                        .format(now,instance_info.status))
        sys.stdout.flush()

# Create a new database on the instance
print '\n\nCreating database {}.'.format(db_name)
try:
    create_db = instance.create_database(db_name)
except e:
    print 'Error creating database: {}.'.format(e)
    sys.exit()

# Generate random password for user account
password = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in range(8))

# Create 'admin' user account for the database
print 'Creating user \'admin\' with a random password.'
try:
    create_user = instance.create_user('admin',password,
                 database_names=[db_name])
except e:
    print 'Error creating user: {}'.format(e)
    sys.exit()

# Once all is done, relay information to user
print ('\nDatabase created successfully!\n'
        'Hostname: {}\n'
        'Database: {}\n'
        'Username: admin\n'
        'Password: {}'
        .format(instance_info.hostname,
                db_name,
                password))