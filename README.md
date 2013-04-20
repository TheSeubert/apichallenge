Rackspace API Challenge
============

    == For all challenges, you can assume that a valid credentials file with the username and API key exist at ~/.rackspace_cloud_credentials ==

Week 1 -
Challenge 1: Write a script that builds three 512 MB Cloud Servers that following a similar naming convention. (ie., web1, web2, web3) and returns the IP and login credentials for each server. Use any image you want. Worth 1 point
Challenge 2: Write a script that clones a server (takes an image and deploys the image as a new server). Worth 2 Point
Challenge 3: Write a script that accepts a directory as an argument as well as a container name. The script should upload the contents of the specified directory to the container (or create it if it doesn't exist). The script should handle errors appropriately. (Check for invalid paths, etc.) Worth 2 Points
Challenge 4: Write a script that uses Cloud DNS to create a new A record when passed a FQDN and IP address as arguments. Worth 1 Point
Challenge 5: Write a script that creates a Cloud Database instance. This instance should contain at least one database, and the database should have at least one user that can connect to it. Worth 1 Point

Week 2 -
Challenge 6: Write a script that creates a CDN-enabled container in Cloud Files. Worth 1 Point
Challenge 7: Write a script that will create 2 Cloud Servers and add them as nodes to a new Cloud Load Balancer. Worth 3 Points
Challenge 8: Write a script that will create a static webpage served out of Cloud Files. The script must create a new container, cdn enable it, enable it to serve an index file, create an index file object, upload the object to the container, and create a CNAME record pointing to the CDN URL of the container. Worth 3 Points

Week 3 -
Challenge 9: Write an application that when passed the arguments FQDN, image, and flavor it creates a server of the specified image and flavor with the same name as the fqdn, and creates a DNS entry for the fqdn pointing to the server's public IP. Worth 2 Points
Challenge 10: Write an application that will:
- Create 2 servers, supplying a ssh key to be installed at /root/.ssh/authorized_keys.
- Create a load balancer
- Add the 2 new servers to the LB
- Set up LB monitor and custom error page. 
- Create a DNS record based on a FQDN for the LB VIP. 
- Write the error page html to a file in cloud files for backup.
Whew! That one is worth 8 points!

Week 4 -
Challenge 11: Write an application that will:
Create an SSL terminated load balancer (Create self-signed certificate.)
Create a DNS record that should be pointed to the load balancer.
Create Three servers as nodes behind the LB.
     Each server should have a CBS volume attached to it. (Size and type are irrelevant.)
     All three servers should have a private Cloud Network shared between them.
     Login information to all three servers returned in a readable format as the result of the script, including connection information.
Worth 6 points

Week 5 -
Challenge 12: Write an application that will create a route in mailgun so that when an email is sent to <YourSSO>@apichallenges.mailgun.org it calls your Challenge 1 script that builds 3 servers.
Assumptions: 
Assume that challenge 1 can be kicked off by accessing http://cldsrvr.com/challenge1 (I am aware this doesn't work. You just need to make sure that your message is getting posted to that URL)
We have an internal mailgun account for this challenge. The API key is "key-0iu6onb4dr30s9jaea7yjktcj29zz-q0".
DO NOT PUT THE API KEY IN YOUR SCRIPT. Assume the Mailgun API key exists at ~/.mailgunapi. Assume no formatting, the api key will be the only data in the file. This should go without saying, but I'm going to say it: Do not put the API key in public github. If you happen to make that mistake by accident, let me know so I can rotate the key please.
Worth 3 points

