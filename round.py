import math


# Round function for tens:
def roundup(x):
	return int(math.ceil(x/10.0)) * 10	

for n in range (100,20000,50):	
        RedCount = roundup(int(0.8*n))
        GreenCount = roundup(int(0.4375*n))
        print int(GreenCount)
