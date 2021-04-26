#!/bin/bash

# Sleep for 30 seconds to allow network initialization before intalling apache
sleep 30

apt-get -y update

# install Apache2
apt-get -y install apache2

# write some HTML
 curl k -s -f --retry 5 --retry-delay 10 --retry-max-time 10 https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/master/experimental/reference/standalone/2nic%2Bwebserver/Default.htm > /var/www/html/index.html

# Add unique entity into default web page
webserver=`hostname`
sed -i.orig "/Demo/c\<h1>Demo Web Page($webserver)</h1>" /var/www/html/index.html
# restart Apache
apachectl restart
