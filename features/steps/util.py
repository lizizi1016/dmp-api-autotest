import random
import time

def randint(start, end):
	random.seed()
	return random.randint(start, end)

def generate_id():
	return str(int(time.time() * 10000))