# -*- coding: utf-8 -*-

import time
from utilities import *
from PySide.QtCore import *
import re

class Parameter(object):
	'''A parameter manages a value present in the world state and writes it to
	the converged state. It does so by registering a callback to changes
	within the world state.
	'''

	def __init__(self, parameter_name, parameter_settings, param_world_state):
		'''world_state is a dict of the form instrument->value and holds 
		values from incoming OSC data.'''
		self.name = parameter_name
		# All persistent values should be written to self.settings
		self._settings = parameter_settings
		self._settings.setdefault('convergence_amount',1.)
		self._settings.setdefault('convergence_rate', 0.01)
		self.value = []
		self._param_state = param_world_state
		# manually set target value
		self.manual_value = []
		# value derived through calculating convergence
		self._converged_value = None
		# values exposed on the gui, in addition to self._settings
		self.editable_values = [
		]
		self.readonly_values = [
			'value',
			'_converged_value',
		]

	def set_manual_value(self, value):
		if validate_value(value):
			self.manual_value = value

	def validate_value(self, value):
		'''Validates whether `value` is valid for this plugin.
		`value` would be the value/list of values passed from a single
		instrument. It is always a list (sometimes with a single value)
		e.g. [4]
		'''
		return True

	def update(self, dt):
		'''Updates self.value.
		'''
		pass


class FloatParameter(Parameter):
	def __init__(self, parameter_name, parameter_settings, param_world_state):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state)
		self._settings.setdefault('default_value', 0.)
		self._settings.setdefault('min', None)
		self._settings.setdefault('max', None)
		self.value = [self._settings['default_value']]
		self.manual_value = [self._settings['default_value']]
		self._converged_value = None
		self.readonly_values += [
			'_converged_value',
		]

	def validate_value(self, value):
		return type(value)==list and map(type, value)==[float]

	def update(self, dt):
		Parameter.update(self, dt)
		conv_amt = self._settings['convergence_amount']
		conv_rate = min(1,self._settings['convergence_rate'] * dt)

		# print 'self._param_state',self._param_state

		if self._param_state:
			# update using convergence
			mean_input = 0.
			for inst in self._param_state:
				mean_input += self._param_state[inst][0]
			mean_input /= len(self._param_state)
			if self._converged_value:
				# smoothly move converged value
				self._converged_value[0] += conv_rate * (mean_input - self._converged_value[0])
			else:
				self._converged_value = [mean_input]
			self.value[0] = conv_amt * self._converged_value[0] + (1.-conv_amt)*self.value[0]
		else:
			# if nothing to converge then just update using manual value
			self.value[0] = self.manual_value[0]


class NoteParameter(Parameter):
	'''Parameter that converges over the cycle of fifths'''

	def __init__(self, parameter_name, parameter_settings, param_world_state):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state)
		self._settings.setdefault('default_value', 0)
		self.manual_value = [self._settings['default_value']]
		self.value = [self._settings['default_value']]
		self._converged_octave = self.manual_value[0] / 12.
		# measured in number of fifths above C
		self._converged_tone = (self.manual_value[0]*7)%12
		self.readonly_values += [
			'_converged_octave',
			'_converged_tone',
		]

	def validate_value(self, value):
		return type(value)==list and map(type, value)==[float]

	def update(self, dt):
		Parameter.update(self, dt)
		conv_amt = self._settings['convergence_amount']
		conv_rate = min(1,self._settings['convergence_rate'] * dt)

		# Notes are considered in terms of letter (with C==0, c#==1, etc) and octave.
		# We normalize all notes to the range [0,12) and then remap them to [0,12) based
		# on how many fifths they are from C. So c->0, c#->7, d->2, etc
		# values are stored as floats to give us a notion of being midway between
		# two notes
		to_fifths = {
			0:0, 1:7, 2:2, 3:9, 4:4, 5:11, 6:6, 7:1, 8:8, 9:3, 10:10, 11:5
		}
		from_fifths = {
			to_fifths[x] : x for x in to_fifths
		}
		notes = []
		if self._param_state:
			for inst in self._param_state:
				notes.append(self._param_state[0])
		notes = notes or self.manual_value

		octave = mean([note/12. for note in notes])
		tone = modular_mean([to_fifths[note%12] for note in notes])

		self._converged_octave += min(
			conv_rate*sign(octave-self._converged_octave),
			octave - self._converged_octave
			)
		self._converged_tone += min(
			conv_rate*sign(tone-self._converged_tone),
			tone - self._converged_tone
			)

		manual_octave = self.manual_value[0] / 12.
		manual_tone = to_fifths[self.manual_value[0] % 12]

		target_octave = conv_amt*self._converged_octave + (1.-conv_amt)*manual_octave
		target_tone = conv_amt*self._converged_tone + (1.-conv_amt)*manual_tone

		# round instead of truncate
		self.value = [int(target_octave*12 + 0.5) + from_fifths[int(target_tone+0.5)]]
		if self.value[0]<0:
			self.value[0] += 12

		# not used except displayed in gui for consistency
		self._converged_value = [self._converged_octave*12 + from_fifths[int(self._converged_tone+0.5)]]


class HarmonyParameter(Parameter):
	'''Parameter for handling sets of integers which measure harmony'''

	def __init__(self, parameter_name, parameter_settings, param_world_state):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state)
		self._settings.setdefault('default_value', [0,5,3])
		self.value = self._settings['default_value']
		self.manual_value = self._settings['default_value']
		self._converged_value = []

	def validate_value(self, value):
		return type(value)==list and all((type(x)==int and 0<=x and x<12 for x in value))

	def update(self, dt):
		conv_amt = clamp(self._settings['convergence_amount'])

		harmonies = []
		if self._param_state:
			for inst in self._param_state:
				harmonies.append(self._param_state[0])
		# find converged harmony
		self._converged_value = []
		if harmonies:
			l = int(mean(map(len, harmonies)))
			i = 0
			while harmonies and len(self._converged_value) < l:
				if harmonies[i]:
					self._converged_value.append(harmonies[i][0])
					harmonies[i] = harmonies[i][1:]
					i = (i+1)%len(harmonies)
				else:
					harmonies.remove(harmonies[i])

		# now combine converged harmony with manual value - for now just simple splice
		if conv_amt==1 and self._converged_value:
			self.value = self._converged_values
		elif conv_amt==0 and self.manual_value:
			self.value = self.manual_value
		else:
			self.value = unique(splice(self.manual_value, self._converged_value))
		if not self.value:
			self.value = self._settings['default_value']


class NarrativeParameter(Parameter):
	'''ManualParameter is a Parameter that is set only using manual_value (i.e. no
		convergence).
	'''

	def __init__(self, parameter_name, parameter_settings, param_world_state):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state)
		self._settings.setdefault('default_value',0.)
		self._settings.setdefault('change_speed', 0.1)
		self.manual_value = [self._settings['default_value']]
		self.value = self.manual_value[:]

	def validate_value(self, value):
		return type(value) is list and map(type, value)==[float]

	def update(self, dt):
		# gradually move towards target value
		amt = min(1,dt * clamp(self._settings['change_speed']))
		self.value[0] += amt * (self.manual_value[0] - self.value[0])



class ConvergenceManager(QObject):
	def __init__(self, settings_dict, log_function, world_state, connections, converged_state, parent=None):
		'''
		:param settings_dict: a dictionary of persistent

		:param log_function: a function for logging messages

		:param world_state: dictionary of incoming state in the form:
		param -> instrument -> [values]
		All parameters must be recognised.

		:param connections: dictionary of how connected instruments are in the form:
		inst1 -> inst2 -> float_between_0_and_1

		:param converged_state: dictionary of the state to be sent out to instruments
		Same form as world_state. Also includes the 'narrative' parameter
		'''
		QObject.__init__(self, parent)

		self.log = log_function
		self.settings = settings_dict
		self.world_state = world_state
		self.connections = connections
		self.converged_state = converged_state

		param_settings = self.settings.setdefault('parameters',{})
		param_types = {
			'activity': FloatParameter,
			'tempo': FloatParameter,
			'loudness': FloatParameter,
			'root': NoteParameter,
			'harmony': HarmonyParameter,
			'detune': FloatParameter,
			'note_frequency': FloatParameter,
			'note_density': FloatParameter,
			'attack': FloatParameter,
			'brightness': FloatParameter,
			'roughness': FloatParameter,
			'narrative': NarrativeParameter,
		}
		self.params = {
			name : typ(
				parameter_name = name,
				parameter_settings = param_settings.setdefault(name, {}),
				param_world_state = self.world_state.setdefault(name, {}),
				)
			for name,typ in param_types.iteritems()
		}
		self.elapsed_timer = QElapsedTimer()
		self.elapsed_timer.start()
		self.time_of_last_update = 0.

		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self.update)
		self.update_timer.setInterval(200)
		self.update_timer.start()

		self.enable_calculate_convergence = True

		self.osc_pattern = re.compile(
			r'''
			 /convergence/ (?P<parameter> [^/]+)
			''', re.VERBOSE)

		# self.default_values = {
		# 	'activity': [0.],
		# 	'tempo': [89.],
		# 	'loudness': [0.5],
		# 	'root': [24],
		# 	'harmony': [0, 7, 3, 10, 8],
		# 	'detune': [0.],
		# 	'note_frequency': [2.],
		# 	'note_density': [0.5],
		# 	'attack': [0.1],
		# 	'brightness': [0.5],
		# 	'roughness': [0.2],
		# }
		# self.single_valued_parameters = [
		# 	'activity',
		# 	'tempo',
		# 	'loudness',
		# 	'immediate_pitch',
		# 	'root',
		# 	'detune',
		# 	'note_density',
		# 	'note_frequency',
		# 	'attack',
		# 	'brightness',
		# 	'roughness',
		# ]

		# # this is used for the universal convergence method (temp function)
		# self.converged_values = dict(self.default_values)
		# self.last_time_of_universal_convergence = None

	def set_manual_value(self, param_name, value):
		if type(value) is list:
			self.params[param_name].manual_value = value
		else:
			self.params[param_name].manual_value = [value]

	def update(self):
		elapsed_time = self.elapsed_timer.elapsed()
		dt = elapsed_time - self.time_of_last_update
		dt = clamp(0.0001, 0.5)
		self.time_of_last_update = elapsed_time

		if self.enable_calculate_convergence:
			self.update_narrative()
			# print 'self.world_state',self.world_state
			for param in self.params.itervalues():
				param.update(dt)
			self.update_converged_state()

	def update_narrative(self):
		'''Update narrative parameter based on instrument connections'''
		instruments = self.connections.keys()
		narrative = 0.
		count = 0.
		for inst1 in instruments:
			for inst2 in (x for x in instruments if x!=inst1):
				narrative += self.connections[inst1][inst2]
				count += 1.
		if count:
			narrative /= count
		self.set_manual_value('narrative', narrative)

	def update_converged_state(self):
		'''Write values from self.params to self.converged_state.
		'''
		# apply this converged_values to all instruments
		for inst in self.connections.keys():
			for param in self.params:
				self.converged_state.setdefault(param,{})[inst] = self.params[param].value



	def osc_message_callback(self, message, origin_address):
		print 'message',message

		match = self.osc_pattern.match(message.address)
		if match:
			param = match.group('parameter')
			if param not in self.params:
				self.log('Unrecognised parameter received over OSC: {}'.format(param))
			else:
				self.set_manual_value(param, message.getValues())
				print param,'set to',self.params[param].manual_value


	# def universal_convergence_method(self, world_state, connections, converged_state):
	# 	'''This is called by stabilizer on a timer.

	# 	converged_values are updated based on world_state regardless of connections.
	# 	converged_state is set for all instruments based on converged_values
	# 	'narrative' is updated based on connections
	# 	'''
	# 	convergence_speed = self.settings['convergence_speed']
	# 	narrative_speed = self.settings['narrative_speed']
	# 	narrative_decay = self.settings['narrative_decay']

	# 	self.last_time_of_universal_convergence = self.last_time_of_universal_convergence or time.time()
	# 	t = time.time()
	# 	dt = t - self.last_time_of_universal_convergence
	# 	self.last_time_of_universal_convergence = t
	# 	alpha = max(0,min(1,convergence_speed*dt))
	# 	narrative_alpha = max(0,min(1,narrative_speed*dt))

	# 	params = set(world_state.keys() + self.converged_values.keys())
	# 	instruments = connections.keys()

	# 	# update converged state for those parmaeters that we've received
	# 	for p in set(world_state.keys()).intersection(self.single_valued_parameters):
	# 		# import pdb; pdb.set_trace()
	# 		set_values = [x[0] for x in world_state[p].values()]
	# 		if set_values:
	# 			value = sum(set_values)/len(set_values)
	# 			self.converged_values[p][0] += alpha*(value - self.converged_values[p][0])

	# 	# todo: parameters that aren't single valued

	# 	# update narrative
	# 	narrative = 0.
	# 	count = 0.
	# 	for inst1 in instruments:
	# 		for inst2 in (x for x in instruments if x!=inst1):
	# 			narrative += connections[inst1][inst2]
	# 			count += 1.
	# 	if count:
	# 		narrative /= count
	# 	old_narrative = self.converged_values.setdefault('narrative', [0.])[0]
	# 	old_narrative *= 1. - (1.-narrative_decay)*dt
	# 	self.converged_values['narrative'][0] += narrative_alpha*(narrative - old_narrative)

	# 	# apply this converged_values to all instruments
	# 	for inst in instruments:
	# 		for param in self.converged_values:
	# 			converged_state.setdefault(param,{})[inst] = self.converged_values[param]
