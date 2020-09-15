#!/bin/bash

apt-get -y update

# install Docker
apt-get -y install docker.io

# install demo app
docker run --name f5demo -p 80:80 -p 443:443 -d f5devcentral/f5-demo-app:1.0.1
