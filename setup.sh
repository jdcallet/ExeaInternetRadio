#! /bin/bash

# Show errors
function catch_errors() {
   echo "Error";
}

trap catch_errors ERR;

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Global variables
HOME_PI="/home/pi"
RADIO="corral"

echo "Installing git..."
apt-get install git

echo "Cloning repositories from http://github.com/sdtorresl/ExeaInternetRadio..."
cd $HOME_PI
git clone http://github.com/sdtorresl/ExeaInternetRadio

# Verify that git work fine
rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

echo "Updating system..."
apt-get -y update

echo "Installing some tools..."
apt-get install -y python-dev python-setuptools python-pip mpg123

rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

pip install rpi.gpio

echo "Installing BTSync..."
mkdir $HOME_PI/.btsync && cd $HOME_PI/.btsync
wget http://btsync.s3-website-us-east-1.amazonaws.com/btsync_arm.tar.gz
tar -xvf btsync_arm.tar.gz
chmod +x ./btsync
./btsync &

echo "Copying files for automatic initialization of software..."
cp $HOME_PI/ExeaInternetRadio/scripts/player /etc/init.d/

# Verify command
rc=$?
if [[ $rc != 0 ]] ; then
    exit $rc
fi

# Permisions of the file
chmod +x /etc/init.d/player
update-rc.d player defaults

echo "Installing Termcolor..."
cd $HOME_PI/ExeaInternetRadio/lib/termcolor-1.1.0
./setup.py install

echo "Installing LogmeIn Hamachi..."
apt-get install -y --fix-missing lsb lsb-core
dpkg --force-architecture --force-depends -i $HOME_PI/ExeaInternetRadio/bin/logmein-hamachi_2.1.0.101-1_armel.deb
/etc/init.d/logmein-hamachi start
hamachi login
hamachi attach soporte@exeamedia.com
hamachi set-nick popsy68

echo "Creating Music directory..."
mkdir $HOME_PI/Music

chown -Rf pi $HOME_PI/*

echo "Copyng script file..."
echo "This radio will be configured: "$RADIO

case $RADIO in
	corral)
		cp $HOME_PI/ExeaInternetRadio/scripts/player_ecg.py $HOME_PI/ExeaInternetRadio/scripts/player.py
		;;
	popsy)
		cp $HOME_PI/ExeaInternetRadio/scripts/player_popsy.py $HOME_PI/ExeaInternetRadio/scripts/player.py
		;;
	*)
		echo "Error copying the script player.py. Default will not be modified."
esac
