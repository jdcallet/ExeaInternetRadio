#! /bin/bash

function catch_errors() {
   echo "setup aborted, because of errors";
   exit 1;
}

trap catch_errors ERR;

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Updating system..."
apt-get -y update

echo "Installing some tools..."
apt-get install -y python-dev python-setuptools python-pip

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

easy_install -U distribute
pip install rpi.gpio

echo "Installing git..."
apt-get install git

echo "Installing BTSync..."
mkdir ~/.btsync && cd ~/.btsync
wget http://btsync.s3-website-us-east-1.amazonaws.com/btsync_arm.tar.gz
tar -xvf btsync_arm.tar.gz 
chmod +x ./btsync
/btsync &

echo "Cloning repositories from http://github.com/sdtorresl/ExeaInternetRadio..."
cd ~
git clone http://github.com/sdtorresl/ExeaInternetRadio

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

echo "Copying files for automatic initialization of software..."
cp ~/ExeaInternetRadio/scripts/player /etc/init.d/

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

chmod +x /etc/init.d/player

echo "Installing Termcolor"
cd ~/ExeaInternetRadio/lib/termcolor-1.1.0
./setup.py install