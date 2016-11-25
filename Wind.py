# -*- coding: utf-8 -*-
# Wind.py Measures Wind speed.
# Author: Alexander Maennel
# License: Public Domain
# 16.11.2016

# imports
import sched, time
import datetime
import sys,tty,termios, curses
import math
import os

from curses import wrapper
from RPIO import PWM

# OnState
OnState = False

# Anemometer:
radius = 0.070 # radius in m
kmh = 0 # kmh
half_revolutions = 0 #  counter for the anemometer with reset each second
countHalfRev = 0 #  counter for the anemometer without reset
mps = 0 # rpm
count = 1 #counting for file.
blinkRun = True
DotCounter = 1

#Diffrenent measurement Intervalls
#for slow measurements:
TwoSecCounter = 0
FourSecCounter = 0
SixSecCounter = 0
TenSecCounter = 0
MinuteCounter = 0


# Command line commands:
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

# time
dateString = '%d.%m.%Y, %H:%M:%S'
fileDateString = '%Y-%m-%d_%H-%M-%S_results.csv'

#data
WriteFile = '0'


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


actualstdout =sys.stdout
sys.stdout = open(os.devnull,'w')
#Setup LED GPIO PINS
servo = PWM.Servo()
PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
#GPIO.setup(13, GPIO.OUT) #RED LED
#GPIO.setup(17, GPIO.OUT) #YELLOW LED
#GPIO.setup(27, GPIO.OUT) #GREEN LED


#result = foobar()
#sys.stdout = actualstdout
#sys.stdout.write(str(result))
#sys.stdout.flush()
#sys.exit(0)

def LEDoff():
    servo.set_servo(13,10)
    servo.stop_servo(13) #red
    servo.set_servo(17,10)
    servo.stop_servo(17) #green
    servo.set_servo(27,10)
    servo.stop_servo(27) #blue     
#    GPIO.output(13,False) #Red on
#    GPIO.output(17,False) #Yellow off
#    GPIO.output(27,False) #Green off

def LEDred():
    servo.set_servo(13,2000) #red 10 to 20000 is maximum    
    servo.set_servo(17,10)
    servo.stop_servo(17) #green
    servo.set_servo(27,10)
    servo.stop_servo(27) #blue   
#    GPIO.output(13,True) #Red on
#    GPIO.output(17,False) #Yellow off
#    GPIO.output(27,False) #Green off
    
def LEDgreen():
    GPIO.output(13,False) #Red off
#    GPIO.output(17,True) #Yellow off
#    GPIO.output(27,False) #Green on

def LEDtoggleYellow(seconds):
 #   GPIO.output(13,False) #Red off
#    GPIO.output(17,False) #Red off
#    GPIO.output(27,False) #Green off
#    for n in range(0,seconds):
#       GPIO.output(17,True)
#       GPIO.output(27,True)
#       time.sleep(0.5)
#       GPIO.output(17,False)
#       GPIO.output(27,False)
#       time.sleep(0.5)
       

# Schedule function, to do something every second.
s = sched.scheduler(time.time, time.sleep)
#def refresh(sc):
def refresh(sc):
    global half_revolutions
    global countHalfRev
    global f
    global count
    global OnState
    global WriteFile
    global blinkRun
    global DotCounter
	
    global TwoSecCounter
    global FourSecCounter
    global SixSecCounter
    global TenSecCounter 
    global MinuteCounter

    # refresh every second the command line
    screen = curses.initscr()
    screen.clear()  
    printInitScreen(screen)
    
    # stop interrupt while calculating
    GPIO.remove_event_detect(24)
    temp_revo = half_revolutions
    countHalfRev += temp_revo
    half_revolutions = 0
    GPIO.add_event_detect(24, GPIO.FALLING, callback=count_function, bouncetime=100)
    
    # calculate rpm with half_revolution
    rpm = temp_revo * 30
    revolutions = temp_revo/2
  
    #mps = 2*radius*math.pi*(rpm/60)    
    #kmh = mps *3.6

    # test
    kmh = 2.4*temp_revo
    mps = kmh/3.6
    temp_revo = 0

    #increase counters: 
    TwoSecCounter += 1
    FourSecCounter +=1
    SixSecCounter +=1
    TenSecCounter +=1
    MinuteCounter +=1

    #Counter Reset, worksqss
    if TwoSecCounter > 2:
	TwoSecCounter = 1
    if FourSecCounter > 4:
	FourSecCounter = 1
    if SixSecCounter > 6:
	SixSecCounter = 1
    if TenSecCounter > 10:
	TenSecCounter = 1
    if MinuteCounter > 60:
	MinuteCounter = 1
    screen.addstr(11,1,str(MinuteCounter))

    # print to screen
    screen.addstr(12,1,'Press button or s to stop the measurement...')
    if blinkRun is True:
	MeasStr = 'Measurement running'
	DotStr = '.'
	if DotCounter < 30:
		DotCounter+=DotCounter
	if DotCounter >30:
		DotCounter = 1
	for n in range(0, DotCounter):
		DotStr = DotStr + '.'
    	screen.addstr(14,1, MeasStr+DotStr)
    else:
	screen.addstr(14,1,'' )
    screen.addstr(15,1,'Result data can be found in')
    screen.addstr(16,1, '\''+WriteFile+'\'')
    screen.addstr(17,1,datetime.datetime.now().strftime(dateString))
    screen.addstr(19,1,'Count  of half revolutions = '+str(countHalfRev))
    screen.addstr(20,1,'Frequency (Hz) = '+str(revolutions))
    screen.addstr(21,1,'Anemometer rpm = '+str(rpm))
    screen.addstr(22,1,'Wind speed in m/s = '+str(round(mps,2))+'; in km/h = '+str(round(kmh,2)))
    screen.refresh()
    
    #print to file
    ToWrite = ',' + str(count) +','+ datetime.datetime.now().strftime(dateString) + ',' + str(mps) + ',' + str(kmh) + ',\n'
    f.write(ToWrite)
    count = count + 1
    
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

    # still in OnState Check
    if OnState is True:
    	s.enter(1,1, refresh, (s,))
    else:
	countHalfRev = 0
	pass

    
# Setup Keyboard toggle
def keyboard_toggle():
    global OnState
    if OnState is False:
	OnState = True
    elif OnState is True:
	OnState = False

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


# main program######################################################################
#start print
def main(stdscr):
    global f    
    global OnState
    global WriteFile
    global blinkRun
    global count

    global TwoSecCounter
    global FourSecCounter
    global SixSecCounter
    global TenSecCounter 
    global MinuteCounter

    LEDoff() #turn all LEDs off
    OnState = False
    #open clear screen
    stdscr.clear()  
    curses.noecho()
    curses.curs_set(0)
    printInitScreen(stdscr)
    printOffScreen(stdscr)
    stdscr.refresh()
    stdscr.nodelay(True) #doesn't wait for keyboard inputs    
    try:
        LEDred()
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
			    TwoSecCounter = 0
			    FourSecCounter = 0
			    SixSecCounter = 0
			    TenSecCounter = 0
			    MinuteCounter = 0

                            LEDtoggleYellow(3)
                            LEDgreen()
                            #open or creat file:
                            filedir = '/home/pi/results/'
                            filename = datetime.datetime.now().strftime(fileDateString)
                            WriteFile = filedir+filename 
                            try:
                                f = open(WriteFile, "w")
                                f.write('Anemometer Result Data File - results.csv,\n,Nr., Date, Time, Windspeed in m/s,Windspeed in km/h,\n')
                            except IOError:
                                CleanUp()
                                sys.exit('Could not create file! Program stopped!')

                            
                            # refresh command line every second
                            f.write('New Meas')
			    blinkRun = True
                            s.enter(1,1, refresh, (s,))
                            s.run()

                            #set screen back to off state.
			    stdscr.clear()  
                            printInitScreen(stdscr)
                            printOffScreen(stdscr)
   			    stdscr.refresh()
			    #close current file
                            f.close()
                            LEDred()
                
    # kill programm after pressing ctrl+c
    except KeyboardInterrupt:
        CleanUp()
    CleanUp()

#Function:
wrapper(main)
