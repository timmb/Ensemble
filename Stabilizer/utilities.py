# -*- coding: utf-8 -*-
'''Generic functions.'''

def mean(l):
	return l and sum(l)/len(l)

def modular_mean(values, modulo=12):
	'''Calculate the mean of a number of values in modular arithmetic.
	With a set of numbers on the clock there are two potential 'mean values'
	opposite each other. We calculate both and then take the one that minimises
	the distance with the input values.

	NB - I'm not entirely this works 100%
	'''
	m0 = mean([float(x)%modulo for x in values])
	m1 = (m0+modulo/2.)%modulo
	m0_dist = sum([min((v-m0)%12,(m0-v)%12) for v in values])
	m1_dist = sum([min((v-m1)%12,(m1-v)%12) for v in values])
	if m0_dist < m1_dist:
		return m0
	else:
		return m1

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
