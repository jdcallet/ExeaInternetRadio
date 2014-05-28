#!/usr/bin/python

import urllib2
import sys
import RPi.GPIO as GPIO
import logging 
import logging.handlers 
import thread
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
cmd_play_bkp5 = "mpg123 -z /home/pi/Music/05\ FDS\ Almuerzo/* &"
cmd_play_bkp6 = "mpg123 -z /home/pi/Music/06\ FDS\ Cena/* &"
cmd_stop_all = "killall mpg123"

# Initialize log system
	
logger = logging.getLogger('ExeaMediaPlayer') 

# Max level of security for messages
# Levels are:
# DEBUG - Higher level
# INFO 
# WARNING 
# ERROR 
# CRITIAL - lower lever
logger.setLevel(logging.DEBUG) 

# If maxBytes=0, the file will not rotate by size 
# If backupCount=0, any file rotated will be deleted
handler = logging.handlers.RotatingFileHandler(filename='/home/pi/ExeaInternetRadio/logs/player.log', mode='a', maxBytes=1024, backupCount=15)

# Define the formater
formatter = logging.Formatter(fmt='[%(asctime)s] %(name)s [%(levelname)s]: %(message)s',datefmt='%y-%m-%d %H:%M:%S') 
handler.setFormatter(formatter)

# Add the handler
logger.addHandler(handler) 

# Use for logging messages:
# logger.debug('message debug') 
# logger.info('message info') 
# logger.warning('message warning') 
# logger.error('message error') 
# logger.critical('message critical')

# Control for threads
thread_finished = False

def run_cmd(cmd, Output = True):
	p = Popen(cmd, shell=True, stdout=PIPE)
	if Output:
		output = p.communicate()[0]
		return output
	else:
		return

def checkInternetConnection():
	try:
		urllib2.urlopen("http://www.exeamedia.com").close()
	except urllib2.URLError:
		print "Checking Internet...\t", colored('[Warning]', 'yellow')
		logger.warning("Checking Internet... [Failed]")
		return False
	else:
		print "Checking Internet...\t", colored('[OK]', 'green')
		logger.info("Checking Internet... [OK]")
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
	
	logger.info("Playing backup")
	
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

def reset():
	command = "/sbin/shutdown -r now"
	import subprocess
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print "Reset pressed!"

def shutdown():
	command = "/sbin/shutdown -h now"
	import subprocess
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print "Shutdown pressed!"

def restart():
	command = "/etc/init.d/player restart"
	import subprocess
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print "Restart pressed!"

def buttons():
	global thread_finished
	
	buttonReset = 10
	buttonShutdown = 11
	buttonRestart = 9

	GPIO.setmode(GPIO.BCM)

	GPIO.setup(buttonReset, GPIO.IN)
	GPIO.setup(buttonShutdown, GPIO.IN)
	GPIO.setup(buttonRestart, GPIO.IN)

	while True:
		
		# if the last reading was low and this one high, print
		if (GPIO.input(buttonReset)):
			reset()
			sleep(0.5)

		if (GPIO.input(buttonShutdown)):
			shutdown()
			sleep(0.5)

		if (GPIO.input(buttonRestart)):
			restart()
			sleep(0.5)

	thread_finished = True

def main():
	global thread_finished

	logger.info('Player started!')

	# Read arguments
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
		logger.error("Usage: player.py {url} {title}")
		return

	print "The url of the streaming is:",colored(url, "green")
	print "The name of the radio is:", colored(title, "green")
	logger.info('The url of the streaming is: ' + url)
	logger.info('The name of the radio is: ' + title)


	# Initialize variables

	# No warnings for GPIO use
	GPIO.setwarnings(False) 

	# Basic commands for play the music
	cmd_play_streaming = "mpg123 " + url + " &"
	currentBackup = ""

	# Initialize LCD
	lcd = LCD()
	lcd.clear()
	lcd.begin(16,1)

	# Stop all players
	run_cmd(cmd_stop_all, False)

	# Start radio or backup
	playingRadio = True
	if checkInternetConnection():
		run_cmd(cmd_play_streaming, False)
		logger.info("Playing streamming from " + url)
	else:
		playBackup()
		playingRadio = False


	# Start the main program in an infinite loop

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
				logger.info('Playing streamming from ' + url)
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

	thread_finished = True

if __name__ == '__main__':
	try:
		thread.start_new_thread(buttons, ())
		thread.start_new_thread(main, ())
		while (not thread_finished):
			pass
	except KeyboardInterrupt:
		print "Bye!"
		logger.info('Bye!')
	except Exception:
		logger.info('Program finished')
