ExeaInternetRadio
=================

Scripts for convert a Raspberry Pi into an Internet Radio.

About
=====

The ExeaInternetRadio is a python script that allows the user plays music from an URL, or locally when the URL isn't available, for example, when the raspberry pi doesn't have internet connection or when the streming source isn't available.
The ExeaInternetRadio also has a script for detecting output sound. When it detects silence, it automatically restart the player.

Quickstart
==========

Install the latest raspbian lite image on a raspberry pi.

Run the file "setup.sh"

Change the configuration file "config.ini" with the URL of your streaming and the name of your radio.

Upload the music backup on the folder "Music" classified in "Dias", "Tardes" and "Noches".

If you wanna have remote access to your raspberry pi, configure the weaved installer selon this guide: https://www.weaved.com/installing-weaved-raspberry-pi-raspbian-os/

If you wanna automatically refresh your backup, configure syncthing following this guide http://www.htpcguides.com/install-syncthing-raspberry-pi-bittorrent-sync-alternative/.

Fix the desired volume executing the command "alsamixer". Save your settings with the command "sudo alsactl store".

 


