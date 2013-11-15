#!/bin/bash


if [[ `whoami` != 'root' ]]
then

echo "You must be root to run this script"
exit 1
fi

apt-get install -y `cat req_software.txt | tr "\n" " "` || exit $?



