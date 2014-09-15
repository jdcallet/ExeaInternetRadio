TEMP="/opt/vc/bin/vcgencmd measure_temp"
LOG=/home/pi/ExeaInternetRadio/logs/temp.log

DATE="/bin/date +%d-%m-%Y\t%T\t"

echo $($DATE) $($TEMP) >> $LOG

