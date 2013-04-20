#!/usr/bin/env python
#
#    Creates 512MB CentOS 6.3 servers based off a preconfigured list.
#    The number of servers and names are configured in server_names.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

# User configurable settings

server_names = ['web1','web2','web3']

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

# Set default image for CentOS 6.3
image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'
	
# Set default flavof of 512M
flavor = '2'

# For each of the server names in server_names, create a server
for server_name in server_names:
    create_server = cs.servers.create(server_name, image, flavor)
    # Server information stored in dictionary for easy access
    server_info = {'id' : create_server.id,
                    'name' : server_name,
                    'admin_pass' : create_server.adminPass}
    # Give the end user a status update
    print 'Building Server {}'.format(server_name)

    # Servers take a bit of time to build, the initial information only
    # contains the admin password. We polll every 5 seconds for a
    # complete ACTIVE status which means it is done
    server = cs.servers.get(server_info['id'])
    while server.status != 'ACTIVE':
            sleep(5)
            server = cs.servers.get(server_info['id'])
            if server.status == 'ERROR' or server.status == 'UNKNOWN':
                print 'Server build error! Status: {}'.format(server.status)
                sys.exit()
            else:
                sys.stdout.write('\rServer Status: {} {}%'
                                .format(server.status,server.progress))
                sys.stdout.flush()

    # Now that server is ACTIVE present all information
    print ('\nBuild Complete!\n'
            'Name: {}\n'
            'Admin Password: {}\n'
            'Public IPv4: {}\n'
            'Public IPv6: {}\n'
            .format(server_info['name'],
                    server_info['admin_pass'],
                    server.accessIPv4,
                    server.accessIPv6))