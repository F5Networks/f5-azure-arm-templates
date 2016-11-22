#!/bin/bash
apt-get -y update

# install Apache2
apt-get -y install apache2

# write some HTML
 curl k -s -f --retry 5 --retry-delay 10 --retry-max-time 10 https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/master/experimental/reference/standalone/2nic%2Bwebserver/Default.htm > /var/www/html/index.html

# restart Apache
apachectl restart
