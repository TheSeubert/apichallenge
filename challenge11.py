#!/usr/bin/env python
#
# Create an SSL terminated load balancer (Create self-signed certificate.)
# Create a DNS record that should be pointed to the load balancer.
# Create Three servers as nodes behind the LB.
#      Each server should have a CBS volume attached to it.
#      (Size and type are irrelevant.)
#      All three servers should have a private Cloud Network
#      shared between them.
# Login information to all three servers returned in a readable format as
# the result of the script, including connection information.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

# User configurable settings

server_names = ['LBaaSWeb1', 'LBaaSWeb2', 'LBaaSWeb3']
clb_name = "TestLB"
new_network_name = 'MY_NETWORK'
new_network_cidr = '192.168.0.0/24'

lb_cert = ('-----BEGIN CERTIFICATE-----\n'
           'MIIDqzCCAxSgAwIBAgIJAOzGQ/iHv6qNMA0GCSqGSIb3DQEBBQUAMIGWMQswCQYD\n'
           'VQQGEwJVUzEOMAwGA1UECBMFVGV4YXMxFDASBgNVBAcTC1NhbiBBbnRvbmlvMRIw\n'
           'EAYDVQQKEwlSYWNrc3BhY2UxDzANBgNVBAsTBkRldk9wczEWMBQGA1UEAxMNcmFj\n'
           'a3NwYWNlLmNvbTEkMCIGCSqGSIb3DQEJARYVc3VwcG9ydEByYWNrc3BhY2UuY29t\n'
           'MB4XDTEzMDQyNjIwNTI1OVoXDTE0MDQyNjIwNTI1OVowgZYxCzAJBgNVBAYTAlVT\n'
           'MQ4wDAYDVQQIEwVUZXhhczEUMBIGA1UEBxMLU2FuIEFudG9uaW8xEjAQBgNVBAoT\n'
           'CVJhY2tzcGFjZTEPMA0GA1UECxMGRGV2T3BzMRYwFAYDVQQDEw1yYWNrc3BhY2Uu\n'
           'Y29tMSQwIgYJKoZIhvcNAQkBFhVzdXBwb3J0QHJhY2tzcGFjZS5jb20wgZ8wDQYJ\n'
           'KoZIhvcNAQEBBQADgY0AMIGJAoGBAKu4yQm4Lp9HSxprgWYsoW2xsGEe+1+s8TFM\n'
           'kSx6rucMHMxouPf/xUS/i1LzJmfDRFiJXifnKIgdbwO7nPFyJDjfmvPIdg592syT\n'
           '4qGWB3NwTG6rNtL9gGNQekbMFeCBzIhoLJO1NCN9KFXyv7nuEhe/MXGOQ33RoIe1\n'
           '6TZXsvGdAgMBAAGjgf4wgfswHQYDVR0OBBYEFGZJe8tBjWIj7HmdPe74ugGlmd03\n'
           'MIHLBgNVHSMEgcMwgcCAFGZJe8tBjWIj7HmdPe74ugGlmd03oYGcpIGZMIGWMQsw\n'
           'CQYDVQQGEwJVUzEOMAwGA1UECBMFVGV4YXMxFDASBgNVBAcTC1NhbiBBbnRvbmlv\n'
           'MRIwEAYDVQQKEwlSYWNrc3BhY2UxDzANBgNVBAsTBkRldk9wczEWMBQGA1UEAxMN\n'
           'cmFja3NwYWNlLmNvbTEkMCIGCSqGSIb3DQEJARYVc3VwcG9ydEByYWNrc3BhY2Uu\n'
           'Y29tggkA7MZD+Ie/qo0wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQUFAAOBgQAF\n'
           '0hE38+tEKP9agaHWqOfiD4+rJNdTgjX+h1kmIAAXiRK7TCyNQC8VmqkL86hyi7GV\n'
           'TV+Wy1bsPoFU2jBpKHKdV5/bzbFIW+xi5zxYibjPN2Re3zhX42hnrt73x9fVZ5/v\n'
           'i3V6lqQ1OiECO4UpbsJMl7RRuIqscJ8tsKG7jzUAeA==\n'
           '-----END CERTIFICATE-----')

lb_key = ('-----BEGIN RSA PRIVATE KEY-----\n'
          'MIICXQIBAAKBgQCruMkJuC6fR0saa4FmLKFtsbBhHvtfrPExTJEseq7nDBzMaLj3\n'
          '/8VEv4tS8yZnw0RYiV4n5yiIHW8Du5zxciQ435rzyHYOfdrMk+KhlgdzcExuqzbS\n'
          '/YBjUHpGzBXggcyIaCyTtTQjfShV8r+57hIXvzFxjkN90aCHtek2V7LxnQIDAQAB\n'
          'AoGAXKa20aeugAHXY8ndZ2NtNeJJaB1vQ4/sEs1dBsKq276NSzy1kBlQNmeipH7M\n'
          'me+hUKPNSXpPRCGdZEY1x4/uOl8p0nwRGCzzeWlUQz4vAx0UXFuGsXQxhzLAUBz0\n'
          'Q7LK7tqcBUkwyITO+2xcZmbD9Zgx7unBHaVJ70p4S0rzNAECQQDSeQ+k8Wvdw9Ec\n'
          '3PRoYNRynwHg3C9D2dBrm3iGtX9bzk7mRcdHFqPgVfSObIyDEBe3EBxamkMClSpv\n'
          '1hvMRAQJAkEA0N3iAtN9VwcusCWOdrpN0UH5w9hYPIZnijs5F7R49bLrKVLCbi/n\n'
          'el0mz+GFbmhtLZtfqIpdDNi123MXRxmt9QJBAJ4xU6rbsgFKrp+NCz5wmP1Vuemy\n'
          'VOwgiGB4yEwnmoP8Op0lETTDNYTl1hw+RhY0QD7doxIOJBOK3gyU1uveq1ECQQDJ\n'
          '17LDMmgtAxbeSNz85Zuv/ocE+PyEOQq0LflFbDV8kxPokj6sxwR2XrDUMceFY8sm\n'
          'SMFPma7EbGSKFxXGsw1FAkAZdRUlvpqReTw0kglGTjYKW5hH9iw/eKE1g5dED/8+\n'
          'sR/YRuq3eevZGqpq8YpPtZEsx8QkFh+w8K7T8hyz/Q9I\n'
          '-----END RSA PRIVATE KEY-----')

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

# Initilize pyrax for Cloud Servers
cs = pyrax.cloudservers
# Initilize pyrax for Cloud Load Balancers
clb = pyrax.cloud_loadbalancers
# Initilize pyrax for Cloud Block Storage
cbs = pyrax.cloud_blockstorage
# Initilize pyrax for Cloud Networks
cnw = pyrax.cloud_networks

# Set default image for CentOS 6.3
image = 'c195ef3b-9195-4474-b6f7-16e5bd86acd0'

# Set default flavof of 512M
flavor = '2'

# Initilize out LB nodes
nodes = []

# Create the new network
my_net = cnw.create(new_network_name, cidr=new_network_cidr)
print 'Created Cloud Network:', my_net

# For each of the server names in server_names, create a server
for server_name in server_names:
    # Add our Cloud Network interface
    networks = my_net.get_server_networks(public=True, private=True)
    create_server = cs.servers.create(server_name, image, flavor,
                                      nics=networks)
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
           'Public IPv6: {}'
           .format(server_info['name'],
                   server_info['admin_pass'],
                   server.accessIPv4,
                   server.accessIPv6))

    # Crate and attach a CBS volume
    print 'Creating a Cloud Block Storage Volume and attaching...'
    create_cbs = cbs.create(name=server_info['name'] + 'CBS',
                            size=100, volume_type='SATA')
    create_cbs.attach_to_instance(server_info['id'], '/dev/xvdb')
    print 'Success!\n'

    # Grab the private IP
    ips = server.addresses
    private = ips['private'][0]['addr']

    # Add as a node for the future
    nodes.append(clb.Node(private, port=80, condition='ENABLED'))

# Proceed to create a Cloud Load Balancer
vip = clb.VirtualIP(type="PUBLIC")

create_lb = clb.create(clb_name, port=80, protocol="HTTP",
                       nodes=nodes, virtual_ips=[vip])

# Build out the load balancer
print "Building Load Balancer {}".format(clb_name)
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

# Add SSL terminiation with certificate and key
print "Adding SSL termination with a self signed certificate..."
lb.add_ssl_termination(securePort=443, secureTrafficOnly=False,
                       certificate=lb_cert, privatekey=lb_key)
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
