readme.txt
####################################
Programs of Wind Measurement Drone:
Editor: Alexander Maennel
2017-01-12
####################################

Ethernet:
IP Address 210.98.2.20

Wi-Fi:
IP Address 192.168.1.1

####################################
Programs:

Wind.py -> Program which records the wind speeds every second. 

Wind2.py -> Program which records the wind speeds every tenth second (recommended).

ClearGPIO.py -> Program to clear and reset the GPIO interface. (only use in case of error)



Test / Example / Old Programs:

Wind2-OLD.py -> Program which records the wind speeds every tenth second, older version (not recommended)

round.py -> Program for testing round function.

Sched.py -> Program for testing the scheduler.

####################################

INSTRUCTION:

In order to perform a new measurement with the drone anemometer, the Raspberry Pi must be controlled with a Wi-Fi-capable device via an SSH tunnel.
The operating system is rasbian, a linux derivate, thus all lunix commands can be interpreted.

	1.	CONNECT TO DEVICE:

	-	After you prepared the drone and the anemometer, start the Raspberry Pi by connecting 
		it with a power supply (either battery pack or micro-usb phone charger).
		
	-	You will need a phone or laptop to connect with the Raspberry. Please download following software in order to connect to Raspberry Pi.

		PC:
			Terminal use: Putty -> http://www.putty.org/
			SFTP use: WinSCP -> https://winscp.net
			
		Android:
			Terminal use: JuiceSSH -> https://play.google.com/store/apps/details?id=com.sonelli.juicessh&hl=de
			SFTP use: TurboClient -> https://play.google.com/store/apps/details?id=turbo.client&hl=de
			
		iOS:
			Terminal use: Termius -> https://itunes.apple.com/us/app/termius-ssh-shell-console/id549039908?mt=8
			SFTP use: FTP OnConnect Free -> https://itunes.apple.com/us/app/ftp-onconnect-free-ftp-sftp/id594722236?mt=8
					

	-	Wait until Raspberry Pi boots, it takes some time. After the the Raspberry booted, it will provide a Wi-Fi similar to a Wi-Fi HotSpot.
		Connect to this Wi-Fi by using a phone or Laptop. SSID: "Pi3-AP", Password: "raspberry". Your device obtains an IP Address like: 192.168.1.xxx,
		where xxx is in the range of 2-255. The Wi-Fi IP Address of the Raspberry is 192.168.1.1.
		
	-	After Phone / PC has a Wi-Fi connection to the Raspberry it is possible to establish a SSH connection with the above mentioned apps / programs: 	
		Putty, WinSCP, JuiceSSH, TurboClient, Termius, FTP OnConnect Free.
		
		All these programs work very similar, a general approach to open an SSH tunnel is following:
			- open a SSH program / app
			- find the button for a "New connection" an click on it.
			- Type as host address, the IP of the Raspberry: "192.168.1.1" (without ") and as port number 22.
			- The SSH connection requires a username and password. The username is "pi" and the password is "raspberry". (uncapitalised and without")
			- Click connect
			
	-	Terminal or SFTP connection is running
			
	2.	START A NEW MEASUREMENT:
	
	- 	Connect your phone / pc with the Raspberry via SSH as described in "CONNECT TO DEVICE". USE Putty, JuiceSSH or FTP OnConnect, to use the terminal.
	
	-	Check whether the current location is the root directory (/home/pi) or not.
		If it is not, use the "cd ~" command.
	
	-	Check date and time of the raspberry, with the command "date". 
		The time must be probably set new, because the internal clock of the raspberry always stops running when the power supply is disconnected.
		
	-	Set the correct date and time by typing the command: ' sudo date --set="10 Jan 2017 10:10:00" ' in order to set the date to 10. January of 2017 10:10:00. 
		Do not forget the 'sudo' command for obtaining admin rights.
	
	- 	After date and time is corrected, start a Terminal Multiplexer session with command "tmux".
		Note:	A program which is running in a tmux session keeps running in the background also when the terminal is closed. 
				A program which does not run in a tmux session stops running when the terminal is closed.
				During a drone flight the Wi-Fi connection could be disconnected, due to the large distances. 
				Thus, the terminal session is also interrupted. A measurement which is not running in a tmux session is interrupted then as well.
				For this reason, it is highly recommended to run the program within a tmux session.
		
	-	Start the wind measurement program in the tmux session by typing the command "sudo python Wind.py" for starting Wind.py or
		"sudo python Wind2.py"(RECOMMENDED) for starting Wind2.py.
		Note: It is recommended to use Wind2.py because it measures wind speed only every ten seconds.
	
	-	The LED is red, when the program has been started  
		Follow the instructions of the program. 
		Press "s" (or the hardware button on the Raspberry Pi) for starting the program (the LED blinks yellow 3 times, afterwards it lights green) 
		or "q" for quit the program (The LED turns off).
		Note: DO NOT PRESS "s" SEVERAL TIMES, BUT ONLY ONE TIME, AS LONG AS THE PROGRAM INITIALIZES. IT TAKES SOME TIME.

	-	The program started correctly, when you can see the wind speed which is refreshed every 10 seconds (Wind2.py).
	
	-	Now the tmux session can be closed, until the end of the measurement. The program keep running in the background.
		To detach the tmux session press "CTRL + B" and afterwards "d". The tmux session is now closed. 
		The terminal can be closed. The measurement is still running.
		
	3.	FINISH A MEAESUREMENT:
		
	- 	Connect your phone / pc with the Raspberry via SSH as described in "CONNECT TO DEVICE". USE Putty, JuiceSSH or FTP OnConnect, to use the Terminal.
	
	-	Open the tmux session by typing "tmux attach", to come back to the measurement program.
	
	-	Press "s" to stop the current measurement.
		NOTE: AFTER "s" WAS PRESSED THE PROGRAM NEEDS SOME TIME TO SHUT DOWN. IN THIS TIME THE PROGRAM DOES NOT RESPOND FOR UP TO 20 SECONDS.
			  DO NOT PRESS ANY BUTTON IN THAT TIME!
	
	-	Press "q" to quit the program, or start a new measurement by pressing "s" again.
	
	-	If you quitted the program, the tmux session can be closed by pressing "CTRL + B" and afterwards "d".
		After that, kill the tmux session with the command: "tmux kill-session"
		
	-	The terminal can be closed or if you do not want to use the Raspberry Pi anymore, you can shut down with the command: "sudo halt".
	
	4.	COPY MEASUREMENT DATA FROM RASPBERRY PI
	
	After a measurement is done, the program saves .csv data file in the /home/pi/results, which can easily imported to Excel or Matlab.
	The data file is named after the starting point in time. For example: a measurement which was started at 10. January of 2017 10:10:00 is called 2017-01-10_10-10-00_results.csv.
	The .csv data file is structured as follows:
		1. Column: empty	2. Column: Counting number of sample	3. Column: Date of sample	4. Column: Point in time of sample	5. Column: Wind speed in m/s	6. Column: Wind speed in km/h	7. Column: Wind speed in m/s (every minute average)	8. Column: Wind speed in km/h (every minute average)	9. Column: Half revolution counter (increments every half revolution of the anemometer)
	
	How to copy data file from Raspberry Pi:	
	
	- 	Connect your phone / pc with the Raspberry via SSH as described in "CONNECT TO DEVICE". 
	
	-	Start a SFTP software as WinSCP (Windows), TurboClient (Android), FTP OnConnect Free (iOS) and connect as described in "CONNECT TO DEVICE".
	
	-	Go to raspberry's directory "/home/pi/results".
