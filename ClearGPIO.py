# -*- coding: utf-8 -*-
# CleanUp.py Measures Wind speed.
# Author: Alexander Maennel
# License: Public Domain
# 16.11.2016

# imports
import sched, time
import datetime
import sys,tty,termios, curses
import math
import subprocess, signal
import RPi.GPIO as GPIO
from curses import wrapper


#kill Wind.py if it is still running.
import psutil
from subprocess import Popen

for process in psutil.process_iter():
    if process.cmdline == ['python', 'Wind.py']:
        print('Process found. Terminating it.')
        process.terminate
        break
    else:
        #print('Process is not running')
        pass

p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
out, err = p.communicate()

# Setup Interrupt GPIO24 for Anemometer

GPIO.setmode(GPIO.BCM)

#Setup LED GPIO PINS
GPIO.setup(4, GPIO.OUT) #RED LED
GPIO.setup(17, GPIO.OUT) #YELLOW LED
GPIO.setup(27, GPIO.OUT) #GREEN LED

def LEDoff():
    GPIO.output(4,False) #Red on
    GPIO.output(17,False) #Yellow off
    GPIO.output(27,False) #Green off

# CleanUp function, should be executed before program is quitted
# It cleans up all the LED, GPIOs and closes all files
def CleanUp():
    global f
    LEDoff()        #Turn off all LED
    GPIO.cleanup()  # clean up GPIO on normal exit  while True:
    try:
        f.close()       # close the file
    except NameError:
        pass
    #curses.endwin()
    sys.exit('Program quitted!')

CleanUp()
