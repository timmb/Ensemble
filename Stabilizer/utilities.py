# -*- coding: utf-8 -*-
'''Generic functions.'''

def mean(l):
	return l and sum(l)/len(l)

import math
def modular_mean(values, modulo=12):
	'''Calculate the mean of a number of values in modular arithmetic.
	'''
	# Convert polar round-the-clock inputs to rectangular (x,y)s
	angle_of_one_step = 2*math.pi / modulo
	rectangular_xs = [math.cos(float(v) * angle_of_one_step)  for v in values]
	rectangular_ys = [math.sin(float(v) * angle_of_one_step)  for v in values]
	# Get mean
	mean_rectangular_x = mean(rectangular_xs)
	mean_rectangular_y = mean(rectangular_ys)
	# If input values were exactly balanced around the circle,
	# eg. modular_mean2([0, 6]) or modular_mean2([1, 11, 5, 7])
	# then mean_rectangular_x & y will be near-as-dammit zero.
	# In this case let's just return a normal non-modular mean
	# and hope for the best, rather than trying to find the angle
	# of tiny ill-conditioned floats.
	if abs(mean_rectangular_x < 0.0001) and abs(mean_rectangular_y) < 0.0001:
		return mean(values) % modulo
	# Convert rectangular back to angle
	mean_angle = math.atan2(mean_rectangular_y, mean_rectangular_x)
	# Convert angle back to number, round to nearest integer, modulo to stay positive
	return round(mean_angle / angle_of_one_step) % modulo

def clamp(x, min_x=0, max_x=1):
	return max(min_x, min(max_x, x))

def splice(a, b, truncate=False):
	'''Interleaves two lists. Return type is list.
	
	>>> a
	[1, 2, 3]
	>>> b
	[6, 7, 8, 9, 10]
	>>> splice(a, b)
	[1, 6, 2, 7, 3, 8, 9, 10]
	>>> splice(a, b, truncate=True)
	[1, 6, 2, 7, 3, 8]
	'''
	l = list(sum(zip(a,b),())) 
	if truncate:
		return l
	else:
		return l + a[len(b):] + b[len(a):]

def unique(seq):
	'''Returns unique elements in lst maintaining original order.
	From http://www.peterbe.com/plog/uniqifiers-benchmark
	'''
	seen = set()
	seen_add = seen.add
	return [x for x in seq if x not in seen and not seen_add(x)]

def sign(x):
	return x<0 and -1 or x>0 and 1 or 0


