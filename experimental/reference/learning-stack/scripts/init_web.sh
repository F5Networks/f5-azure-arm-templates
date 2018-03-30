#!/bin/bash

# Sleep for 30 seconds to allow network initialization before intalling apache
sleep 30
# Update package repository
apt-get -y update
# install Apache2
apt-get -y install apache2
# Download and modify example HTML
if [ -z "$1" ]; then branch="master"; else branch="$1"; fi
curl -fk --retry 5 --retry-delay 10 --retry-max-time 10 https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/$branch/experimental/reference/learning-stack/html/default.html > /var/www/html/index.html
# Download Image
curl -fk --retry 5 --retry-delay 10 --retry-max-time 10 https://raw.githubusercontent.com/F5Networks/f5-azure-arm-templates/$branch/experimental/reference/learning-stack/images/f5_favicon.ico > /var/www/html/favicon.ico
# Replace values in file as needed
webserver=`hostname`
sed -i "s/(hostname)/($webserver)/g" /var/www/html/index.html
sed -i "s/\/master/\/$branch/g" /var/www/html/index.html
# restart Apache
apachectl restart


##### Could also run f5-demo-app #####
# install Docker
#apt-get -y install docker.io
# Spin up Docker Instance
#docker run --name demo_app -p 80:80 -d f5devcentral/f5-demo-app:latest