#!/bin/bash

function timeout(){
	echo "Silence detected. Player is going to be restarted"
	service player restart
}

timeout_sec=20
freq_sec=120
substream=card0/pcm0p/sub0

last_usage=`date +%s`

while true; do
        now=`date +%s`
        if [ "`cat /proc/asound/${substream}/status`" == "running" ]; then
                last_usage=${now}
        fi;
        if [ `expr ${now} - ${last_usage}` -gt ${timeout_sec} ]; then
                timeout
        fi;
        sleep ${freq_sec}
done
