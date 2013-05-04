import re
import time

class InputProcessor(object):
	'''The Input Processor receives OSC messages and updates the world state accordingly.
	'''

	def __init__(self, world_state, instruments, log_function=(lambda message, module: None)):
		'''world_state is a dictionary (probably empty)
		instruments is a dictionary (probably empty):
			{ instrument_name -> { parameter_name -> parameter_value } }
		log_function is a function for recording log messages
		'''
		self.world_state = world_state
		self.instruments = instruments
		self.log = log_function
		
		self.state_pattern = re.compile(
			r'''
			 / (?P<type> state ) / (?P<sender> [^/]+) / (?P<parameter> [^/]+)
			''', re.VERBOSE)
		self.log_pattern = re.compile(
			r'''
			/ (?P<type> (log|warning|error)) / (?P<sender> [^/]+)
			''', re.VERBOSE)
		self.ping_pattern = re.compile(r'''
			/ (?P<type> ping ) / (?P<sender> [^/]+)
			''', re.VERBOSE)
		self.listen_port_pattern = re.compile(r'''
			/ (?P<type> listen_port) / (?P<sender> [^/]+)
			''', re.VERBOSE)
		
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

	def osc_message_callback(self, message, origin_address):
		'''message is of type: txosc.osc.Message.
		origin should be in the form (host, port)
		'''
		match = (
			   self.state_pattern.match(message.address)
			or self.ping_pattern.match(message.address)
			or self.log_pattern.match(message.address)
			or self.listen_port_pattern.match(message.address)
			)
		if not match:
			self.log("Invalid OSC message received from {}: {}".format(origin_address, message), "InputProcessor")
			return
		
		message_type = match.group('type')
		sender = match.group('sender')
		self.we_have_heard_from(sender, origin_address)

		if message_type == 'state':
			param = match.group('parameter')
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
		
		elif message_type in ('log', 'warning', 'error'):
			log_message = ', '.join(map(str, message.getValues()))
			self.log(message_type+': '+log_message, sender)
		
		elif message_type=='listen_port':
			values = message.getValues()
			if values:
				port = values[0]
				if 0<port and port<65536:
					host = self.instruments[sender]['address'][0]
					self.instruments[sender]['address'] = (host,port)
				else:
					self.log('Error: {} sent invalid listen_port of {}'.format(sender, port), 'InputProcessor')
			else:
				self.log('Error: {} sent listen_port without any arguments', 'InputProcessor')		


	def we_have_heard_from(self, instrument_name, instrument_address):
		'''
		instrument_address is of form (host, port).

		host is updated within the instrument states dictionary by this function.
		(port is updated elsewhere using listen_port messages)
		'''
		if instrument_name not in self.instruments:
			self.log('First message received from '+instrument_name, 'InputProcessor')
			self.instruments[instrument_name] = {}
			self.instruments[instrument_name]['state'] = {}
			self.instruments[instrument_name]['address'] = instrument_address
		self.instruments[instrument_name]['last heard at'] = time.strftime("%H:%M:%S")
		old_address = self.instruments[instrument_name]['address']
		new_host = instrument_address[0]
		if old_address[0] != new_host:
			self.log('Host for {} changed from {} to {}'.format(instrument_name, old_address[0], new_host), 'InputProcessor')
			port = old_address[1]
			self.instruments[instrument_name]['address'] = (new_host, port)

	def check_valid(self, param, type_tags, arguments):
		if param in self.valid_message_type_tags:
			return self.valid_message_type_tags[param].match(type_tags)
		else:
			return True

