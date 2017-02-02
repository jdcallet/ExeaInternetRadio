#!/usr/bin/python

# import lirc
import urllib2
import sys
import RPi.GPIO as GPIO
import logging 
import logging.handlers 
from threading import Thread
from lcd import LCD
from subprocess import * 
from time import sleep, strftime
from termcolor import colored
from datetime import datetime

#Script for play the streaming when internet connection is detected. When there isn't internet connection it automatically plays the
#backup selon the  hour of the day(day, evenning or night) 

# Basic commands
cmd_ip = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1" #Prints the IP when is connecting via ethernet
cmd_play_bkp1 = "mpg123 -z /home/pi/Music/Dias/* &" #Plays the music located in the folder Dias
cmd_play_bkp2 = "mpg123 -z /home/pi/Music/Tardes/* &" #Plays the music located in the folder Tardes
cmd_play_bkp3 = "mpg123 -z /home/pi/Music/Noches/* &" #Plays the music located in the folder Noches
cmd_stop_all = "killall mpg123" #Stop the sofware using for play the music
cmd_check_sound = "ps -A | grep mpg123 | wc -l | awk '{print substr($0,1,1)}'" #Shows if there is a mog123 process running
cmd_check_device = "cat /proc/asound/card0/pcm0p/sub0/status | grep state | awk '{print $2}'" #Show if the sound is active or not

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
handler = logging.handlers.RotatingFileHandler(filename='/home/pi/ExeaInternetRadio/logs/player.log', mode='a', maxBytes=1024000, backupCount=30)

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
url = ""
title = ""

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Initialize LIRC connection for IR Remote Control
# sockid = lirc.init('irremote')
#Function for execute commands
def run_cmd(cmd, Output = True):
	p = Popen(cmd, shell=True, stdout=PIPE)
	if Output:
		output = p.communicate()[0]
		return output
	else:
		return
#Function for check internet connection. it tries to open the URL of the streaming.
def checkInternetConnection():
                try:
                        urllib2.urlopen(url).close()
                        logger.info("Checking Internet... [OK]")
                        return True

                except urllib2.URLError:
                        logger.warning("Checking Internet... [Failed]")
                        return False

                except SocketError as e:
                        if e.errno != errno.ECONNRESET:
                                raise
                        pass

#Function for determine the current hour.
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

#Funciton for play the URL of the streaming audio.
def playOnline():
        run_cmd(cmd_stop_all, True)
        cmd_play_streaming = "mpg123 " + url + " &"
        run_cmd(cmd_play_streaming, True)
        logger.info("Playing online")
        return True

#Function for play the music stored in the device.        
def playBackup():
	run_cmd(cmd_stop_all, False)
	logger.info("Playing backup")
	#Plays folder Dias
	if dateInRange(00, 00, 11, 00):
		run_cmd(cmd_play_bkp1, True)
		return "Dias"
	#Plays folder Tardes
	if dateInRange(11, 00, 18, 00):
		run_cmd(cmd_play_bkp2, True)
		return "Tardes"
	#Plays folder Noches
	if dateInRange(18, 00, 23, 59):
		run_cmd(cmd_play_bkp3, True)
		return "Noches"

	return True

#Function for reboot the raspberry pi
def reboot():
	global thread_finished

	logger.info("Button reboot pressed... [OK]")
	command = "/sbin/shutdown -r now"
	run_cmd(command, False)
	print "Reboot pressed!"

	thread_finished = True

#def buttons():
#	global thread_finished
#	
#	buttonShutdown = 11
#	
#	GPIO.setmode(GPIO.BCM)
#
#	GPIO.setup(buttonShutdown, GPIO.IN)

#	while True:
#		if (GPIO.input(buttonShutdown)):
#			lcd = LCD()
#			lcd.clear()
#			lcd.begin(16,1)
#			lcd.message("Apagando\nSistema...")
#			sleep(3)
#			lcd.clear()
#			shutdown()
#			sleep(0.5)
#	thread_finished = True

#This function check if mpg123 is running all time, in case of
# error, the software will be restarted
def checkSoundOutput():
	global thread_finished

	sleep(60) #Wait while the main function load

	while True:
		output = run_cmd(cmd_check_sound, True)
		output = output [:1]
		if (output != "1"):
			print "Error: mpg123 is not running"
			logger.error("mpg123 is not running")
			logger.critical("The software will be restarted")
			run_cmd(cmd_stop_all, False)
			playStreaming()

		sleep(60) #Check each 60 seconds

	thread_finished = True

#Defines the reproduction mode it there is internet connection or not
def playStreaming():

        if checkInternetConnection():
                playOnline()
                return True

        else:
                playBackup()
                return False

#Restart the device if there is not internet connection for play the backup mode
def stateoff():
        global thread_finished

        while True:
                if not checkInternetConnection():
                        if playStreaming():
                                print "Error: There is not internet connection"
                                logger.info("Changing to backup mode")
                                run_cmd(cmd_stop_all, False)
                                playStreaming()
        	sleep(60)
        thread_finished = True

#Restart the device if the internet is back for play again the online mode
def stateon():
        global thread_finished

        while True:
                if checkInternetConnection():
                        if not playStreaming():
                                print "Error: There is internet connection"
                                logger.info("Changing to online mode")
                                run_cmd(cmd_stop_all, False)
                                playStreaming()
        	sleep(60)
        thread_finished = True  

#Loop for display the execution process in the LCD screen
def main():
	logger.info('Player started!')
	
	# Basic commands for play the music
	currentBackup = ""

	# Initialize LCD
	lcd = LCD()
	lcd.clear()
	lcd.begin(16,1)

	# Start radio or backup
	ledConnection = 2
	ledCheck = 3

	GPIO.setup(ledConnection, GPIO.OUT)

	# Start the main program in an infinite loop
	while True: 
		status = run_cmd(cmd_check_device, True)
		status = status[:4]
		lcd.clear()
		lcd.message("ExeaMusicPlayer\n")
		lcd.message( 'Estado: ' + status )
		sleep(2)
		
		lcd.clear()
		lcd.message("Escuchas:\n")
		lcd.message(title)
		sleep(2)

		#Show IP info 
		lcd.clear()
		ipaddr = run_cmd(cmd_ip)

		if not ipaddr:
			lcd.message('Sin Internet\n')
		else:
			lcd.message( ipaddr )

		#Show date for 10 seconds
		i = 0
		while i<10:
			lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
			sleep(1)
			i = i+1
			pass

	thread_finished = True

# def setup():
# 	global thread_finished

# 	while True:
# 		code = lirc.nextcode()
# 		if (len(code) > 0):
# 			code = code[0]
# 			if(code == 'MENU'):
# 				print 'Ha presionado el boton Menu!'
# 			elif(code == 'BACK'):
# 				print 'Ha presionado el boton Back!'
# 			elif(code == 'SELECT'):
# 				print 'Ha presionado el boton Select!'
# 			elif(code == 'NUMBER_0'):
# 				print 'Ha presionado el boton 0!'
# 			elif(code == 'NUMBER_1'):
# 				print 'Ha presionado el boton 1!'
# 			elif(code == 'NUMBER_2'):
# 				print 'Ha presionado el boton 2!'
# 			elif(code == 'NUMBER_2'):
# 				print 'Ha presionado el boton 2!'
# 			elif(code == 'NUMBER_3'):
# 				print 'Ha presionado el boton 3!'
# 			elif(code == 'NUMBER_4'):
# 				print 'Ha presionado el boton 4!'
# 			elif(code == 'NUMBER_5'):
# 				print 'Ha presionado el boton 5!'
# 			elif(code == 'NUMBER_6'):
# 				print 'Ha presionado el boton 6!'
# 			elif(code == 'NUMBER_7'):
# 				print 'Ha presionado el boton 7!'
# 			elif(code == 'NUMBER_8'):
# 				print 'Ha presionado el boton 8!'
# 			elif(code == 'NUMBER_9'):
# 				print 'Ha presionado el boton 9!'
# 		pass

# 	thread_finished = True

def blinker():

	global thread_finished

	ledTest = 4
	GPIO.setup(ledTest, GPIO.OUT)
	
	while True:
		GPIO.output(ledTest, 0)
		sleep(0.5)
		GPIO.output(ledTest, 1)
		sleep(0.5)

	thread_finished = True

if __name__ == '__main__':

	# Read arguments
	if len(sys.argv) >= 3:
		url = sys.argv[1]
		for x in xrange(2, len(sys.argv)):
			title = title + sys.argv[x] + " "

		print "The url of the streaming is:",colored(url, "green")
		print "The name of the radio is:", colored(title, "green")
		logger.info('The url of the streaming is: ' + url)
		logger.info('The name of the radio is: ' + title)

	else:
		print "Usage: player.py {url} {title}";
		logger.error("Usage: player.py {url} {title}")

	try: #Initialization of all the threads.
                Thread(target=playStreaming, args=()).start()
                Thread(target=blinker, args=()).start()
                Thread(target=main, args=()).start()
                Thread(target=stateoff, args=()).start()
                Thread(target=stateon, args=()).start()
                Thread(target=checkSoundOutput, args=()).start()
	except KeyboardInterrupt:
		print "Bye!"
	 	logger.info('Bye!')
	except Exception, errtxt:
		logger.info('Program finished by external exception')
		logger.error(errtxt)
	
