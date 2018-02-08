from threading import Timer
import time

num = 4
def getNum():
    global num
    num = num - 1
    return num

def waitTillDone():
    if getNum() > 0:
        print('not happening, waiting...')
        #time.sleep(1.0)
        #waitTillDone()
        Timer(1.0, waitTillDone).start()
    else:
        print('Done!')

waitTillDone()
print("this should be second!")
