from txosc import osc, async
from twisted.internet import reactor
from random import uniform, sample

sender = async.DatagramClientProtocol()
socket = reactor.listenUDP(0, sender)

default_dest = ('127.0.0.1', 1123)

def send(*args, **kwargs):
	'''
	e.g.
	>> send('/address', 'arg0', 1.0, 37)
	'''
	address = args and args[0] or ''
	dest = kwargs.get('dest', default_dest)
	m = osc.Message(address, *map(osc.createArgument, args[1:]))
	sender.send(m, dest)

def create_instruments(min=0., max=1., num_active=8):
	'''
	Create instruments for the Ensemble project with min and max activity values
	'''
	instruments = ['tim','daniel','rockmore','dom','kacper','ptigas','tadeo','joker']
	values = []
	# nb order is not preserved
	active_instruments = sample(instruments, num_active)
	for i in instruments:
		if i in active_instruments:
			values.append(uniform(min, max))
		else:
			values.append(0.)
		send('/state/{}/activity'.format(i), values[-1])
	print('Instruments created:')
	for i,v in zip(instruments, values):
		print i.ljust(10), v