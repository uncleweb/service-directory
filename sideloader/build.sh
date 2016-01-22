#!/bin/bash

cd $REPO

docker build -t service-directory .

docker tag -f service-directory qa-mesos-persistence.za.prk-host.net:5000/service-directory

docker push qa-mesos-persistence.za.prk-host.net:5000/service-directory
