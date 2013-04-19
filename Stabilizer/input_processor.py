import re

class InputProcessor(object):
	'''The Input Processor receives OSC messages and updates the world state accordingly.
	'''

	def __init__(self, world_state, log_function=lambda message, module: None):
		self.world_state = world_state
		self.log = log_function
		self.address_pattern = re.compile(
			r'''
			/ (?P<type> log)
			 |(?P<type> error)
			 |((?P<type> state)/(?P<sender> [^/]*)/(?P<parameter> [^/]*)
			  )
			''', re.VERBOSE)

	def osc_message_callback(self, message, origin):
		'''message is of type: txosc.osc.Message.
		origin should be in the form (host, port)
		'''
		# to do
		if not is_valid(message):
			log("Invalid OSC message received from {}: {}", "InputProcessor")
		else:
			match = re.match(self.address_pattern, message.address)
			;;asdf # continue from here matching different message types
			self.world_state

