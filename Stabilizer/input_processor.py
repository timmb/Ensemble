import re
import time

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
		self.ping_pattern = re.compile(r'/ ping / (?P<sender> [^/]+)', re.VERBOSE)
		
		type_tags_regex = {
			'activity' : r'f',
			'tempo' : r'f',
			'loudness' : r'f',
			'immediate_pitch' : r'i+',
			'root' : r'i',
			'harmony' : r'i+',
			'detune' : r'f',
			'note_on' : r'fi?',
			'note_frequency' : r'f',
			'note_density' : r'f',
			'attack' : r'f',
			'brightness' : r'f',
			'roughness' : r'f',
		}
		self.valid_message_type_tags = {
			param : re.compile(type_tags_regex[param]) for param in type_tags_regex
		}

	def osc_message_callback(self, message, origin):
		'''message is of type: txosc.osc.Message.
		origin should be in the form (host, port)
		'''
		# to do
		log_match = self.log_pattern.match(message.address)
		state_match = self.state_pattern.match(message.address)
		ping_match = self.ping_pattern.match(message.address)
		match = log_match or state_match or ping_match
		
		if not match:
			self.log("Invalid OSC message received from {}: {}".format(origin, message), "InputProcessor")
			return
		sender = match.group('sender')
		self.we_have_heard_from(sender)

		if log_match:
			log_message = ', '.join(map(str, message.getValues()))
			self.log(log_match.group('type')+': '+log_message, sender)
		elif state_match:
			param = state_match.group('parameter')
			value = message.getValues()
			if self.check_valid(param, message.getTypeTags(), value):
				if param not in self.world_state:
					self.log('First value received for '+param, 'InputProcessor')
					self.world_state[param] = {}
				self.world_state[param][sender] = value
				self.instruments[sender]['state'][param] = value
			else:
				self.log('Invalid parameter/value combination from '
					+'{} for parameter {}: {}'.format(sender, param, value))

	def we_have_heard_from(self, instrument_name):
		if instrument_name not in self.instruments:
			self.log('First message received from '+instrument_name, 'InputProcessor')
			self.instruments[instrument_name] = {}
			self.instruments[instrument_name]['state'] = {}
		self.instruments[instrument_name]['last heard at'] = time.strftime("%H:%M:%S")

	def check_valid(self, param, type_tags, arguments):
		if param in self.valid_message_type_tags:
			return self.valid_message_type_tags[param].match(type_tags)
		else:
			return True

