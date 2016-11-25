import time
from RPIO import PWM


servo = PWM.Servo()

sleepTime = 0.005

while True:
    for n in range (10,20000,100):	
        servo.set_servo(17,n)
        time.sleep(sleepTime)
    for n in range (20000,10,-100):	
        servo.set_servo(17,n)
        time.sleep(sleepTime)

#servo.set_servo(13,20000) #red
#servo.set_servo(17,5000) #green
#servo.set_servo(27,20000) #blue
#time.sleep(10)
