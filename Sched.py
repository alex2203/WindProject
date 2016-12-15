import time
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()

temp = 0
OnState = True

def some_job():
    global temp
    global OnState
    
    print('Every ten sec')
    temp = temp+1
    if temp == 4:
        OnState = False
    
replace_existing=True

sched.start()
sched.add_job(some_job, 'interval', seconds = 2,id='test')

while OnState is True:
    time.sleep(1)
    
sched.remove_job('test')
sched.shutdown()






