#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BOARD)	

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

buttonReset = 21
buttonShutdown = 19
buttonRestart = 23

GPIO.setmode(GPIO.BOARD)
GPIO.setup(buttonReset, GPIO.IN)
GPIO.setup(buttonShutdown, GPIO.IN)
GPIO.setup(buttonRestart, GPIO.IN)

while True:
	
	#if the last reading was low and this one high, print
	if (GPIO.input(buttonReset)):
		reset()
		time.sleep(0.5)

	if (GPIO.input(buttonShutdown)):
		shutdown()
		time.sleep(0.5)

	if (GPIO.input(buttonRestart)):
		restart()
		time.sleep(0.5)
