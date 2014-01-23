#!/usr/bin/env python
#
#    After taking a FQDN and IP as arguments, will create the
#    domain in Cloud DNS and add an A record with these values.

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
parser = argparse.ArgumentParser(description='Creates a DNS A record '
                                 'with provided domain and creates '
                                 'if needed')
parser.add_argument('fqdn', metavar='FQDN', type=str,
                    help='A Fully Qualified Domain Name')
parser.add_argument('ip', type=str,
                    help='IP that A record should point to for FQDN')
# Set varaibles to be used through the program
args = parser.parse_args()
fqdn = args.fqdn
ip = args.ip

# Check to make sure we can access the credentials file and authenticate.
try:
    pyrax.set_credential_file(credentials_file)
except e.AuthenticationFailed:
    print ('Authentication Failed: Ensure valid credentials in {}'
           .format(credentials_file))
except e.FileNotFound:
    print ('File Not Found: Make sure a valid credentials file is located at'
           '{}'.format(credentials_file))

# Initilize pyrax for clouddns
dns = pyrax.cloud_dns

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
    "data": ip,
    "ttl": 300,
}]
try:
    new_record = domain.add_record(record)
except e.DomainRecordAdditionFailed as err:
    print "ERROR: {}".format(err)
    sys.exit()

print ("Record added!\n"
       "Domain: {}\n"
       "Type: {}\n"
       "Data: {}\n"
       "TTL: {}"
       .format(new_record[0].name,
               new_record[0].type,
               new_record[0].data,
               new_record[0].ttl))
