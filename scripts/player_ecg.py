#!/usr/bin/python

import urllib2
import sys
import RPi.GPIO as GPIO
from lcd import LCD
from subprocess import * 
from time import sleep, strftime
from termcolor import colored
from datetime import datetime

# Basic commands
cmd_ip = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
cmd_play_bkp1 = "mpg123 -z /home/pi/Music/01\ ALMUERZO/* &"
cmd_play_bkp2 = "mpg123 -z /home/pi/Music/02\ HAPPY/* &"
cmd_play_bkp3 = "mpg123 -z /home/pi/Music/03\ CENA/* &"
cmd_play_bkp4 = "mpg123 -z /home/pi/Music/04\ BRUNCH/* &"
cmd_play_bkp5 = "mpg123 -z /home/pi/Music/05\ FDS\ ALMUERZO/* &"
cmd_play_bkp6 = "mpg123 -z /home/pi/Music/06\ FDS\ CENA/* &"
cmd_stop_all = "killall mpg123"

def run_cmd(cmd, Output = True):
	p = Popen(cmd, shell=True, stdout=PIPE)
	if Output:
		output = p.communicate()[0]
		return output
	else:
		return

def checkInternetConnection():
	try:
		urllib2.urlopen("http://www.google.com").close()
	except urllib2.URLError:
		print "Checking Internet...\t", colored('[Warning]', 'yellow')
		return False
	else:
		print "Checking Internet...\t", colored('[OK]', 'green')
		return True

def dateInRange(initialHour, initialMinute, finalHour, finalMinute):
	currentHour = hour = datetime.now().hour
	currentMinute = datetime.now().minute

	if initialHour <= currentHour and finalHour >= currentHour:
		if currentHour == initialHour:
			if currentMinute >= initialMinute:
				return True
			else:
				return False
		if currentHour == finalHour:
			if currentMinute <= finalMinute:
				return True
			else:
				return False
		return True
	else:
		return False

def playBackup():
	run_cmd(cmd_stop_all, False)
	
	today = datetime.today().weekday() 

	# Weekend
	if today == 6 or today == 5:
		# Music for lunch
		if dateInRange(6, 00, 12, 00):
			run_cmd(cmd_play_bkp4, False)
			return "Brunch"
		if dateInRange(12, 00, 16, 00):
			run_cmd(cmd_play_bkp5, False)
			return "FDS Almuerzo"
		# Music for happy hour
		if dateInRange(16, 00, 21, 00):
			run_cmd(cmd_play_bkp2, False)
			return "Happy Hour"
		# Music for dinner
		if dateInRange(21, 00, 23, 59):
			run_cmd(cmd_play_bkp6, False)
			return "FDS Cena"
		# Music for dawn
		if dateInRange(00, 00, 6, 00):
			run_cmd(cmd_play_bkp5, False)
			return "FDS Amanecer"
	else:
		# Music for lunch
		if dateInRange(11, 30, 16, 00):
			run_cmd(cmd_play_bkp1, False)
			return "Almuerzo"
		# Music for happy hour
		if dateInRange(16, 00, 21, 00):
			run_cmd(cmd_play_bkp2, False)
			return "Happy Hour"
		# Music for dinner
		if dateInRange(21, 00, 23, 59):
			run_cmd(cmd_play_bkp3, False)
			return "Cena"
		# Music for dawn
		if dateInRange(00, 00, 9, 00):
			run_cmd(cmd_play_bkp1, False)
			return "Amanecer"
	return

def main():

	if len(sys.argv) >= 3:	
		url = sys.argv[1]
		# Read the title of the streaming
		if len(sys.argv) > 3:
			title = sys.argv[2]
			for x in xrange(3,len(sys.argv)):
				title = title + " " + sys.argv[x]
		else:
			title = sys.argv[2]
	else:
		print "Usage: player.py {url} {title}";
		return

	print "The url of the streaming is:",colored(url, "green")
	print "The name of the radio is:", colored(title, "green")
	GPIO.setwarnings(False) 

	cmd_play_streaming = "mpg123 " + url + " &"
	currentBackup = ""

	# Initialize LCD
	lcd = LCD()
	lcd.clear()
	lcd.begin(16,1)

	# Stop all players
	run_cmd(cmd_stop_all, False)

	playingRadio = True
	if checkInternetConnection():
		run_cmd(cmd_play_streaming, False)
	else:
		playBackup()
		playingRadio = False

	# Infinite loop
	while 1:
		lcd.clear()
		lcd.message("ExeaMusicPlayer")
		sleep(2)
		
		if playingRadio:
			# Check Internet status
			if checkInternetConnection():
				lcd.clear()
				lcd.message("Escuchas:\n")
				lcd.message(title)
				sleep(2)
				pass
			else:
				# Play backup
				lcd.clear()
				lcd.message("Reproduciendo\nrespaldo")
				sleep(1)
				currentBackup = playBackup()
				lcd.clear()
				lcd.message("Respaldo\n")
				lcd.message(currentBackup)
				sleep(2)
				playingRadio = False
				pass
			pass
		else:
			# Restore streaming radio or show status of "backup"
			if checkInternetConnection():
				run_cmd(cmd_stop_all, False)
				run_cmd(cmd_play_streaming, False)
				playingRadio = True
				pass
			else:
				lcd.clear()
				lcd.message("Respaldo\n")
				lcd.message(currentBackup)
				sleep(2)

		#Show IP info 
		lcd.clear()
		ipaddr = run_cmd(cmd_ip)
		if not ipaddr:
			lcd.message('Sin Internet\n')
		else:
			lcd.message('IP %s' % ( ipaddr ))

		#Show date for 10 seconds
		i = 0
		while i<10:
			lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
			sleep(1)
			i = i+1
			pass

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print "Bye!"
