import re

class InputProcessor(object):
	'''The Input Processor receives OSC messages and updates the world state accordingly.
	'''

	def __init__(self, world_state, instruments, log_function=(lambda message, module: None)):
		'''world_state is a dictionary (probably empty)
		instruments is a dictionary (probably empty)
		log_function is a function for recording log messages
		'''
		self.world_state = world_state
		self.instruments = instruments
		self.log = log_function
		self.state_pattern = re.compile(
			r'''
			 / state / (?P<sender> [^/]+) / (?P<parameter> [^/]+)
			''', re.VERBOSE)
		self.log_pattern = re.compile(
			r'''
			/ (?P<type> (log|warning|error)) / (?P<sender> [^/]+)
		''', re.VERBOSE)
		self.ping_pattern = re.compile(r'/ ping / (<?P<sender> [^/]+)', re.VERBOSE)

	def we_have_heard_from(self, instrument_name):
		if instrument_name not in self.instruments:
			self.log('First message received from '+instrument_name, 'InputProcessor')
		self.instruments[instrument_name] = time.strftime("%H:%M:%S.%f")

	def osc_message_callback(self, message, origin):
		'''message is of type: txosc.osc.Message.
		origin should be in the form (host, port)
		'''
		# to do
		log_match = self.log_pattern(message.address)
		state_match = self.state_pattern(message.address)
		ping_match = self.ping_pattern(message.address)
		match = log_match or state_match or ping_match
		
		if not match:
			self.log("Invalid OSC message received from {}: {}", "InputProcessor")
			return
		sender = match.group('sender')
		we_have_heard_from(sender)

		if log_match:
			log_message = ', '.join(map(str, message.getValues()))
			self.log(log_match.group('type')+': '+log_message, sender)
		else:
			param = state_match.group('parameter')
			value = message.getValues()
			check_valid(param, value)
			if param not in self.world_state:
				self.log('First value received for '+param, 'InputProcessor')
				self.world_state[param] = {}
			self.world_state[param][sender] = values

