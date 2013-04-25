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
container_name = 'StaticWebsite'

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
    print 'Error: {}'.format(e)

# We set the static index page to be served
try:
    index_file = 'index.html'
    index_data = ('<html>'
                  '<head>'
                  '<title> My Test Page</title>'
                  '</head>'
                  '<body bgcolor=\'white\' text=\'blue\'>'
                  '<h1> My first page </h1>'
                  'A static index page does exist here?'
                  '</body>'
                  '</html>')


    container.set_web_index_page(index_file)
    container.store_object(index_file,index_data,content_type='text/html')
    print ('A static index page has been created. Visit {}'
            ' to test.').format(container.cdn_uri)
except Exception, e:
    print 'Error: {}'.format(e)

# Initilize pyrax for clouddns
dns = pyrax.cloud_dns

# We create CNAME records to make the URL more user friendly
fqdn = raw_input('Enter the CNAME you want to create: ')
split_fqdn = fqdn.split('.')
root_fqdn = split_fqdn[1]+'.'+split_fqdn[2]

# Check to see if domain exist
try:
    domain = dns.find(name=root_fqdn)
    print 'Domain found: Continuing'
except e.NotFound as err:
    print 'Domain not found: Creating domain {}.'.format(root_fqdn)
    try:
        domain = dns.create(name=root_fqdn,
                emailAddress='admin@'+root_fqdn,
                ttl=900, comment='automaticly added domain')
    except e.DomainCreationFailed as e:
        print 'Domain creation failed:', e
        sys.exit()
print 'Adding DNS CNAME record.'
record = [{
            'type': 'CNAME',
            'name': fqdn,
            'data': container.cdn_uri,
            'ttl': 300,
            }]
try:
    new_record = domain.add_record(record)
except e.DomainRecordAdditionFailed as err:
    print 'ERROR: {}'.format(err)
    sys.exit()

print ('Record added!\n'
        'Domain: {}\n'
        'Type: {}\n'
        'Data: {}\n'
        'TTL: {}'
        .format(new_record[0].name,
                new_record[0].type,
                new_record[0].data,
                new_record[0].ttl))
