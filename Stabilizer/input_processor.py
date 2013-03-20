

class InputProcessor(object):
	'''The Input Processor receives OSC messages and updates the world state accordingly.
	'''

	def __init__(self, world_state):
		self.world_state = world_state

	def osc_message_callback(self, message, origin):
		'''message is of type: txosc.osc.Message.
		origin should be in the form (host, port)
		'''
		# to do
		pass