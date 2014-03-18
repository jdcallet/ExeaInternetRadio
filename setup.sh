#! /bin/bash

function catch_errors() {
   echo "Error";
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
apt-get install -y python-dev python-setuptools python-pip mpg132

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

pip install rpi.gpio

echo "Installing BTSync..."
mkdir ~/.btsync && cd ~/.btsync
wget http://btsync.s3-website-us-east-1.amazonaws.com/btsync_arm.tar.gz
tar -xvf btsync_arm.tar.gz 
chmod +x ./btsync
./btsync &

echo "Installing git..."
apt-get install git

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

echo "Installing Termcolor..."
cd ~/ExeaInternetRadio/lib/termcolor-1.1.0
./setup.py install

# echo "Installing LogmeIn Hamachi..."
# apt-get install --fix-missing lsb lsb-core
# dpkg --force-architecture --force-depends -i ~/ExeaInternetRadio/bin/logmein-hamachi_2.1.0.101-1_armel.deb
# hamachi login
# hamachi attach soporte@exeamedia.com