#!/usr/bin/env python
#
#    Based off of user input, will image a cloud server and create a
#    new 512MB server from this image.

import os
import pyrax
import pyrax.exceptions as e
import sys
from time import sleep

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

# Initilize pyrax for cloudservers in DFW
cs_dfw = pyrax.cloudservers

# Initilize pyrax for cloudservers in ORD
cs_ord = pyrax.connect_to_cloudservers(region="ORD")

# Initilize our dictionary of choices
choices = {}

# Get a list of current servers and display them for selection
# We do this for both US regions just in case
servers_dfw = cs_dfw.servers.list()
servers_ord = cs_ord.servers.list()

print "Select a server from which an image will be created."
print "Servers in DFW Region:"
for position, server in enumerate(servers_dfw):
    print "1.{}: {}".format(position, server.name)
    choices["1."+str(position)] = server.id

print "Servers in ORD Region:"
for position, server in enumerate(servers_ord):
    print "2.{}: {}".format(position, server.name)
    choices["2."+str(position)] = server.id

# Process which server the end user wants to image    
selection = None
while selection not in choices:
    if selection is not None:
        print "   -- Invalid choice"
    selection = raw_input("Enter the number for your choice: ")
if float(selection) < 2:
    cs = cs_dfw
    server = cs_dfw.servers.get(choices[selection])
else:
    cs = cs_ord
    server = cs_ord.servers.get(choices[selection])

# Gather name for image from user input
image_name = raw_input("Enter a name for the image: ")

# Create the image and provide a blocked status update
print "\nCreating a new image off of the selected server."

create_image = server.create_image(image_name)
image = cs.images.get(create_image)
while image.status != 'ACTIVE':
        sleep(5)
        image = cs.images.get(image.id)
        if image.status == 'ERROR' or image.status == 'UNKNOWN':
            print 'Image build error! Status: {}'.format(image.status)
            sys.exit()
        else:
            sys.stdout.write('\rImage Status: {} {}%'
                            .format(image.status,image.progress))
            sys.stdout.flush()

# Create a server off of this new image
print "\nCreating a new server off of this iamge now..."

create_server = cs.servers.create(image_name, image, "2")

# Server information stored in dictionary for easy access
server_info = {'id' : create_server.id,
                'name' : image_name,
                'admin_pass' : create_server.adminPass}
# Give the end user a status update
print 'Building Server {}'.format(image_name)

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
print ('\n\nBuild Complete!\n'
        'Name: {}\n'
        'Admin Password: {}\n'
        'Public IPv4: {}\n'
        'Public IPv6: {}\n'
        .format(server_info['name'],
                server_info['admin_pass'],
                server.accessIPv4,
                server.accessIPv6))