#!/usr/bin/env python
#
#    Creates a server based off a provided FQDN, image and flavor.
#    A DNS record is also added of the FQDN to point to the public IP.

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
parser = argparse.ArgumentParser(description='Creates a server based '
                                 'off of a FQDN complete with DNS.')
parser.add_argument('fqdn', metavar='fqdn', type=str,
                    help='The fully qualified domain name to use')
parser.add_argument('image', type=str,
                    help='ID of image to build server with.')
parser.add_argument('flavor', type=int,
                    help='ID of flavor to build server with.')
# Set varaibles to be used through the program
args = parser.parse_args()
fqdn = args.fqdn
image = args.image
flavor = args.flavor

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

# Create a server off of the users input
print "\nCreating a new server."

create_server = cs.servers.create(fqdn, image, flavor)

# Server information stored in dictionary for easy access
server_info = {'id': create_server.id,
               'name': fqdn,
               'admin_pass': create_server.adminPass}
# Give the end user a status update
print 'Building Server {}'.format(fqdn)

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
                             .format(server.status, server.progress))
            sys.stdout.flush()

# Now that server is ACTIVE present all information
print ('\n\nBuild Complete!\n'
       'Name: {}\n'
       'Admin Password: {}\n'
       'Public IPv4: {}\n'
       'Public IPv6: {}\n'
       .format(server_info['name'],
               server_info['admin_pass'],
               server.accessIPv4,
               server.accessIPv6))

# Create DNS record based off of the FQDN that was received
# Initilize pyrax for clouddns
dns = pyrax.cloud_dns

print ('\nCreating an A record based off of the provided FQDN and'
       'the new server.')
# Check to see if domain exist
try:
    domain = dns.find(name=fqdn)
    print "Domain found: Continuing"
except e.NotFound as err:
    print "Domain not found: Creating domain."
    try:
        domain = dns.create(name=fqdn, emailAddress="admin@" + fqdn,
                            ttl=900, comment="automaticly added domain")
    except e.DomainCreationFailed as e:
        print "Domain creation failed:", e
        sys.exit()
print "Adding DNS A record."
record = [{
    "type": 'A',
    "name": fqdn,
    "data": server.accessIPv4,
    "ttl": 300,
}]
try:
    new_record = domain.add_record(record)
except e.DomainRecordAdditionFailed as err:
    print "ERROR: {}".format(err)
    sys.exit()

print ("DNS Record added pointing from {} to {}"
       .format(fqdn, server.accessIPv4))
