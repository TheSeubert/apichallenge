#!/usr/bin/env python
#
# - Creates two 512mb CentOs servers, supplying your local
#   ~/.ssh/id_rsa.pub ssh key to be installed at /root/.ssh/authorized_keys.
# - Creates a load balancer
# - Adds the 2 new servers to the LB
# - Sets up LB health monitors and custom error page.
# - Creates a DNS record based on a FQDN for the LB VIP.
# - Writes the error page html to a file in cloud files for backup.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

# User configurable settings

server_names = ['web1', 'web2']
clb_name = "TestLB"
container_name = 'ErrorBackup'
ssh_key = "~/.ssh/id_rsa.pub"

# Non-configurable code is below
# Statically configured credentials file
credentials_file = os.path.expanduser('~/.rackspace_cloud_credentials')

# Read in key file
expand_ssh_key = os.path.expanduser(ssh_key)
ssh_key_file = {"/root/.ssh/authorized_keys": open(expand_ssh_key, 'r').read()}

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

# Initilize pyrax for Cloud Load Balancers
clb = pyrax.cloud_loadbalancers

# Set default image for CentOS 6.3
image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'

# Set default flavof of 512M
flavor = '2'

# Initilize out LB nodes
nodes = []

# For each of the server names in server_names, create a server
for server_name in server_names:
    create_server = cs.servers.create(
        server_name, image, flavor, files=ssh_key_file)
    # Server information stored in dictionary for easy access
    server_info = {'id': create_server.id,
                   'name': server_name,
                   'admin_pass': create_server.adminPass}
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
                                 .format(server.status, server.progress))
                sys.stdout.flush()

    # Now that server is ACTIVE present all information
    print ('\nBuild Complete!\n'
           'Name: {}\n'
           'Admin Password: {}\n'
           'Public IPv4: {}\n'
           'Public IPv6: {}\n'
           'SSH Key Added from {}\n'
           .format(server_info['name'],
                   server_info['admin_pass'],
                   server.accessIPv4,
                   server.accessIPv6,
                   ssh_key))
    # Grap the private IP
    ips = server.addresses
    private = ips['private'][0]['addr']

    # Add as a node for the future
    nodes.append(clb.Node(private, port=80, condition="ENABLED"))

# Proceed to create a Cloud Load Balancer
vip = clb.VirtualIP(type="PUBLIC")

create_lb = clb.create(clb_name, port=80, protocol="HTTP",
                       nodes=nodes, virtual_ips=[vip])

# Build out the load balancer
print "\nBuilding Load Balancer {}".format(clb_name)
lb = clb.get(create_lb.id)
while lb.status != 'ACTIVE':
    sleep(5)
    lb = clb.get(create_lb.id)
    if lb.status == 'ERROR' or lb.status == 'UNKNOWN':
        print 'Load Balancer build error! Status: {}'.format(lb.status)
        sys.exit()
    else:
        sys.stdout.write('\rLoad Balancer Status: {}'
                         .format(lb.status))
        sys.stdout.flush()

# Once done we relay all the data to the user
print ("\nSuccess!\nLoad Balancer VIP: {}".format(lb.virtual_ips[0].address))

# Create health monitors on the nodes
print "Adding CONNECT type health monitors to nodes..."
lb.add_health_monitor("CONNECT")
lb = clb.get(lb.id)
while lb.status != 'ACTIVE':
    sleep(1)
    lb = clb.get(lb.id)
    if lb.status == 'ERROR' or lb.status == 'UNKNOWN':
        print 'Load Balancer build error! Status: {}'.format(lb.status)
        sys.exit()
    else:
        sys.stdout.write('\rLoad Balancer ReBuild Status: {}'
                         .format(lb.status))
        sys.stdout.flush()
print "\nSuccess!"

# Create a custom error page
print "Adding custom error page..."
error_html = ('<html>'
              '<head>'
              '<title> Error!</title>'
              '</head>'
              '<body bgcolor=\'white\' text=\'blue\'>'
              '<h1> Something went wrong... </h1>'
              'An error page does exist here?'
              '</body>'
              '</html>')
lb.set_error_page(error_html)
lb = clb.get(lb.id)
while lb.status != 'ACTIVE':
    sleep(1)
    lb = clb.get(lb.id)
    if lb.status == 'ERROR' or lb.status == 'UNKNOWN':
        print 'Load Balancer build error! Status: {}'.format(lb.status)
        sys.exit()
    else:
        sys.stdout.write('\rLoad Balancer ReBuild Status: {}'
                         .format(lb.status))
        sys.stdout.flush()
print "\nSuccess!"

# Set up DNS records pointing to our load balancer IP
fqdn = raw_input("Enter a FQDN to create DNS records that point"
                 " to the new LB: ")
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
    "data": lb.virtual_ips[0].address,
    "ttl": 300,
}]
try:
    new_record = domain.add_record(record)
except e.DomainRecordAdditionFailed as err:
    print "ERROR: {}".format(err)
    sys.exit()

print "Record added!"

# Backup the error page to cloud files
print "Backing up our custom error page to cloud files."
print "Using container name {}.".format(container_name)

# Initilize pyrax for cloudservers
cf = pyrax.cloudfiles

# Create the specified container
try:
    container = cf.create_container(container_name)
    print 'Success! Container {} has been created!'.format(container_name)
except Exception, e:
    print 'Error: {}'.format(e)

# Store our previous custom error page
container.store_object("error.html", error_html, content_type='text/html')
print ("Page has been stored in your cloud files container {}"
       " called error.html").format(container_name)
