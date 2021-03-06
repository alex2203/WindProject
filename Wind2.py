# -*- coding: utf-8 -*-
# Wind.py Measures Wind speed.
# Author: Alexander Maennel
# License: Public Domain
# 28.11.2016

# imports
import sched, time
import datetime
import sys,tty,termios, curses
import math
import os


from curses import wrapper
from RPIO import PWM
import logging
logging.basicConfig()

from apscheduler.schedulers.background import BackgroundScheduler


# OnState
OnState = False

# Anemometer:
radius = 0.070 # radius in m
kmh = 0 # kmh
kmhMIN = 0 # kmh Average Mintue 
half_revolutions = 0 #  counter for the anemometer with reset each second
countHalfRev = 0 #  counter for the anemometer without reset
rpm = 0 #rpm
mps = 0 # mps
mpsMIN = 0 # mps Average Minute
temp_revoMIN = 0 #revolution counter Average Minute
WriteAvgMinute = False # Write Average Minute Entry in ResultDataFile
count = 1 #counting for file.
blinkRun = True
DotCounter = 1
MinuteCounter = 0
runningCounter = 0
turnCounter = 0
StarString = ''

# time
dateString = '%d.%m.%Y, %H:%M:%S'
fileDateString = '%Y-%m-%d_%H-%M-%S_results.csv'

#data
WriteFile = '0'

#define Scheduler:
sched = BackgroundScheduler()


# Setup Interrupt GPIO24 for Anemometer
import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)
# GPIO 24 set up as an input, pulled down, connected to 3V3 on button press  
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Interrupt from anemometer
# count function, if there is a half revolution of anemometer.  
def count_function(channel): 
	global half_revolutions 
	half_revolutions = half_revolutions + 1 
	#ToggleGreenLED()
# when a falling edge is detected on port 24, regardless of whatever   
GPIO.add_event_detect(24, GPIO.FALLING, callback=count_function, bouncetime=100)

# Setup Interrupt GPIO23 for Toggle
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def toggle_function(Channel): 
	global OnState
	if OnState is False:
		OnState = True
	elif OnState is True:
		OnState = False
GPIO.add_event_detect(23, GPIO.FALLING, callback=toggle_function, bouncetime=300)



#Setup LED GPIO PINS
#Define RGB LED GPIO CHANNELS
RED = 13
GREEN = 17
BLUE = 27
servo = PWM.Servo()
PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)

# Round function for tens:
def roundup(x):
	return int(math.ceil(x/10.0)) * 10	


def SmoothOn(*args):
	if args[0] is 'YELLOW':
		for n in range (100,args[-1],50):	
			RedCount = roundup(int(0.8*n))
			GreenCount = roundup(int(0.4375*n))	
			servo.set_servo(RED,RedCount)
			servo.set_servo(GREEN,GreenCount)
			time.sleep(0.0008)
	else:
		for n in range (100,args[-1],50):
			servo.set_servo(args[0],n)
			time.sleep(0.0008)

def SmoothOff(*args):
	if args[0]  is 'YELLOW':
		for n in range (args[-1],100,-50):
			RedCount = roundup(int(0.8*n))
			GreenCount = roundup(int(0.4375*n))	
			servo.set_servo(RED,RedCount)
			servo.set_servo(GREEN,GreenCount)
			time.sleep(0.0008)
	else:
		for n in range (args[-1],100,-50):
			servo.set_servo(args[0],n)
			time.sleep(0.0008)


def LEDoff(Smooth): # if Smooth on, red LED turns off slowly. Set Smooth only true, if the red LED is already lighting
	global OnState
	if Smooth is True:
		SmoothOff(13,20000)
	else:
		pass
	servo.set_servo(RED,10)
	servo.stop_servo(RED) #red
	servo.set_servo(GREEN,10)
	servo.stop_servo(GREEN) #green
	servo.set_servo(BLUE,10)
	servo.stop_servo(BLUE) #blue     

def LEDred():
	LEDoff(False)
	SmoothOn(RED,20000)
    
def LEDgreen():
	LEDoff(False)
	SmoothOn(GREEN,20000)


def LEDtoggleYellow(seconds):
	LEDoff(True)
	for n in range(0,seconds):
		time.sleep(0.1)
		SmoothOn('YELLOW',20000)
		time.sleep(0.1)
		SmoothOff('YELLOW',20000)

def ToggleGreenLED():
	LEDoff(False)
	servo.set_servo(GREEN,20000)
       

# Schedule function, to do something every second.
#s = sched.scheduler(time.time, time.sleep)
#def refresh(sc):
def MeasurementRun():
	global half_revolutions
	global countHalfRev
	global f
	global count
	#global OnState
	global WriteFile
	global blinkRun
	global DotCounter	

	global MinuteCounter
	global temp_revoMIN
	global kmhMIN
	global mpsMIN
	global WriteAvgMinute
	global WriteFile
	global rpm
	global kmh
	global mps

      
    # stop interrupt while calculating
	GPIO.remove_event_detect(24)
	temp_revo = half_revolutions
	countHalfRev += temp_revo
	half_revolutions = 0
	GPIO.add_event_detect(24, GPIO.FALLING, callback=count_function, bouncetime=100)
     # calculate rpm with half_revolution
	rpm = temp_revo * 30 * 0.10
	#revolutions = temp_revo/2  
	#mps = 2*radius*math.pi*(rpm/60)    
	#kmh = mps *3.6

    # test
	kmh = 2.4*temp_revo*0.10
	mps = kmh*0.277778
	temp_revoMIN = temp_revo + temp_revoMIN
	temp_revo = 0

    #increase counters: 
	MinuteCounter +=1

	if MinuteCounter > 6:
                kmhMIN = 2.4*temp_revoMIN*0.0166667
                mpsMIN = kmhMIN*0.277778
                temp_revoMIN = 0
		MinuteCounter = 1
		WriteAvgMinute = True
	
	# Write to file
	if WriteAvgMinute is False:
                ToWrite = ',' + str(count) +','+ datetime.datetime.now().strftime(dateString) + ',' + str(round(mps,2)) + ',' + str(kmh) + ',,,' + str(countHalfRev) + ',\n'
        else:
                ToWrite = ',' + str(count) +','+ datetime.datetime.now().strftime(dateString) + ',' + str(round(mps,2)) + ',' + str(kmh) + ',' + str(round(mpsMIN,2)) + ',' + str(kmhMIN) + ',' + str(countHalfRev) + ',\n'
                WriteAvgMinute = False
        #
        try:
                f = open(WriteFile, "a")        
                f.write(ToWrite)
                f.close()
        except IOError:
                pass
        
	
	count = count + 1

    
def PrintMeasurementRun():
	global half_revolutions
	global countHalfRev
	global f
	global count
	global OnState
	global WriteFile
	global blinkRun
	global DotCounter

	global MinuteCounter
	global temp_revoMIN
	global kmhMIN
	global mpsMIN
	global kmh
	global mps
	global WriteAvgMinute
	global WriteFile
	global rpm
	global runningCounter
	global turnCounter
	global StarString

	screen = curses.initscr()
	screen.clear()  
	printInitScreen(screen)

    # print to screen
	#if OnState is True:
	screen.addstr(11,1,'Measurement running')
	screen.addstr(13,1, 'Press button or s to stop the measurement...')	
	


	turnCounter = turnCounter+1
	if turnCounter > 5:
		turnCounter = 0
		MeasString = '/'
	elif turnCounter == 0:
		MeasString = '/'
	elif turnCounter == 1:
		MeasString = '\ '
	elif turnCounter == 2:
		MeasString = '-'
	elif turnCounter == 3:
		MeasString = '/ '
	elif turnCounter == 4:
		MeasString = '\ '
	elif turnCounter == 5:
		MeasString = '-'
	else:
		pass
	
	screen.addstr(11,20,StarString+MeasString)

	if runningCounter > 34:
		runningCounter = 0
		StarString = ''
	else:
		runningCounter = runningCounter+1
		StarString = StarString + '*'

	screen.addstr(15,1,'Result data can be found in')
	screen.addstr(16,1, '\''+WriteFile+'\'')
	screen.addstr(17,1,datetime.datetime.now().strftime(dateString))	
	screen.addstr(19,1,'Count  of half revolutions = '+str(countHalfRev))
	#screen.addstr(20,1,'Frequency (Hz) = '+str(revolutions))
	screen.addstr(20,1,'Anemometer rpm = '+str(rpm))
	screen.addstr(21,1,'Wind speed in m/s = '+str(round(mps,2))+'; in km/h = '+str(round(kmh,2)))
       	screen.addstr(22,1,'Wind speed (Avg Min) in m/s = '+str(round(mpsMIN,2))+'; in km/h = '+str(round(kmhMIN,2)))
	screen.refresh()



    #Any keyboard inputs?	
	try:
		inChr = '0' # 0 is default
		inChr = screen.getkey()	
	except curses.error:
		inChr = '0'		
	if inChr == 's':
    		keyboard_toggle()
	else:		
		pass  

	if blinkRun is True:
		blinkRun = False
	else:
		blinkRun = True
	
    
# Setup Keyboard toggle
def keyboard_toggle():
	global OnState
	if OnState is False:
		OnState = True
	elif OnState is True:
		OnState = False

# Generate IsRunningString
def IsRunningPrint(TempStr):
	PrintedString = TempStr
	return PrintedString


# CleanUp function, should be executed before program is quitted
# It cleans up all the LED, GPIOs and closes all files
def CleanUp():
	global f
	LEDoff(True)        #Turn off all LED
	GPIO.cleanup()  # clean up GPIO on normal exit  while True:
 	sched.shutdown()  #Shutdown Scheduler
	try:
		f.close()       # close the file
	except NameError:
		pass
	curses.endwin()
	sys.exit('Program quitted!')

# Screen segments:
def printInitScreen(stdscr):
	stdscr.addstr(0,1,'#######################################################')    
	stdscr.addstr(1,1,'#                                                     #')    
	stdscr.addstr(2,1,'#                       Wind.py                       #')    
	stdscr.addstr(3,1,'#                                                     #')    
	stdscr.addstr(4,1,'#        Author: Alexander Maennel, 18.11.2016        #')
	stdscr.addstr(5,1,'#                                                     #')
	stdscr.addstr(6,1,'# Program to determine the wind speed with anemometer #')
	stdscr.addstr(7,1,'#                                                     #')
	stdscr.addstr(8,1,'#       Results will be stored in /results/           #')
	stdscr.addstr(9,1,'#######################################################')
    

def printOffScreen(stdscr):
	stdscr.addstr(11,1,'Press q to quit...')
	stdscr.addstr(13,1,'Waiting for measqurement')
	stdscr.addstr(15,1,'Press Button or s to start new measurement')

def printStartScreen(stdscr):
	stdscr.addstr(11,1,'Program started')
	stdscr.addstr(13,1,'Please, wait until initialization has been completed')
	stdscr.addstr(15,1,'Do not press any button')

def 	printStartScreenProg():
	screenStart = curses.initscr()
	screenStart.clear()  
	printInitScreen(screenStart)			
	printStartScreen(screenStart)
	screenStart.refresh()

# main program######################################################################
#start print
def main(stdscr):
	global f    
	global OnState
	global WriteFile
	global blinkRun
	global count
	global countHalfRev
	global WriteFile

    	LEDoff(False) #turn all LEDs off
	OnState = False
	stdscr.clear()  
	curses.noecho()
	curses.curs_set(0)
	printInitScreen(stdscr)
	printOffScreen(stdscr)
	stdscr.refresh()
	stdscr.nodelay(True) #doesn't wait for keyboard inputs    3
	sched.start() # Start Scheduler
	LEDred()
	try:        	
		while True:
			if OnState is False:			
				try:
					inChr = '0' # 0 is default
					inChr = stdscr.getkey()	
				except curses.error: 
					inChr = '0' 						
				if inChr == 's':
					keyboard_toggle()
				elif inChr == 'q':
					CleanUp()
					sys.exit('Program quitted')
				else:
					pass     
			elif OnState is True:  
				count = 1
				MinuteCounter = 0 
				printStartScreenProg()
				LEDtoggleYellow(3)
				LEDgreen()
				#open or creat file:
				filedir = '/home/pi/results/'
				filename = datetime.datetime.now().strftime(fileDateString)
				WriteFile = filedir+filename                 
				try:
					f = open(WriteFile, "w")
					f.write('Anemometer Result Data File - results.csv,\n,Nr., Date, Time, Windspeed in m/s,Windspeed in km/h,Windspeed in m/s (Minute Average),Windspeed in km/h (Minute Average),Half Revolution counter,\n')
                                        f.write('New Meas')
                                        f.close()
				except IOError:
					CleanUp()
					sys.exit('Could not create file! Program stopped!')                           
				# refresh command line every second
				blinkRun = True
				
				#start scheduler:
				sched.add_job(MeasurementRun,'interval', seconds = 10, id='meas')		
				#sched.add_job(PrintMeasurementRun,'interval', seconds = 1, id='measScreen')				
                                #infinite loop as long as OnState is True				
				while OnState is True:
					#pass
                                        #time.sleep(100)
					PrintMeasurementRun()
					time.sleep(2)
                                sched.remove_job('meas')
				#sched.remove_job('measScreen')
                               
				# Reset Measurement Variables
				countHalfRev = 0
				runningCounter = 0
				turnCounter = 0
				kmh = 0 
				kmhMIN = 0  
				half_revolutions = 0 
				rpm = 0 
				mps = 0
				mpsMIN = 0 
				temp_revoMIN = 0 
				StarString = ''
				
				#set screen back to off state.
				stdscr.clear()  
				printInitScreen(stdscr)
				printOffScreen(stdscr)
				stdscr.refresh()
				SmoothOff(GREEN,20000) # Smooth off Green.			
				LEDred()
                
    # kill programm after pressing ctrl+c
	except KeyboardInterrupt:
		CleanUp()
	CleanUp()

#Function:
wrapper(main)
