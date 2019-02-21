import random
import time

def randint(start, end):
	random.seed()
	return random.randint(start, end)

def waitfor(context, getter, duration, interval=1, flag=False):
	starttime = time.time()
	timeout = duration * context.time_weight
	while time.time() - starttime < timeout:
		if getter(context, flag):
			return
		time.sleep(interval)
	else:
		raise Exception

def generate_id():
	return str(int(time.time() * 10000))
