# -*- coding: utf-8 -*-

import time
from utilities import *
from PySide.QtCore import *
import re

def pr(s):
	print s

# convergence_rate is amount of convergence per second
# convergence_amount is 0..1 to use either the manual value or converged value

class Parameter(QObject):
	'''A parameter manages a value present in the world state and writes it to
	the converged state. It does so by registering a callback to changes
	within the world state.
	'''

	sig_is_converged_valid_changed = Signal(bool)
	sig_is_post_update_statement_valid_changed = Signal(bool)

	def __init__(self, parameter_name, parameter_settings, param_world_state, 
		parameters, log_function):
		''':param world_state: is a dict of the form instrument->value and holds 
		values from incoming OSC data.
		:param parameters: is a dictionary of all parameters (all of which would be 
			subclasses of Parameter) indexed by name.
		'''
		QObject.__init__(self)
		self.name = parameter_name
		self.params = parameters

		# All persistent values should be written to self.settings
		self._settings = parameter_settings
		self._settings.setdefault('convergence_amount',1.)
		self._settings.setdefault('convergence_rate', 0.01)
		# This is what is used to determine 'value', before it is blended with
		# manual_value. Use any python expression as well as:
		# <param-name> for the value of other parameters
		# convergence as short for _converged_value[0].
		# dt for time since the last update in seconds
		# It's not safe - be careful.
		self._settings.setdefault('convergence_transform', 'convergence')
		# This allows us to do pretty much whatever we want via the gui
		# it is a python statement that is run at the end of the update function
		self._settings.setdefault('post_update_statement', '')

		self._log = lambda x: log_function(x, module=self.name)
		self.value = []
		self._param_state = param_world_state
		# manually set target value
		self._manual_value = []
		# value derived through calculating convergence
		self._converged_value = None
		# values exposed on the gui, in addition to self._settings
		self.editable_values = [
		]

		# Readonly values
		self.readonly_values = [
			'value',
			'_converged_value',
		]

		self.is_convergence_transform_valid = True
		self.is_post_update_statement_valid = True

	def _disable_convergence_transform(self):
		'''
		Remove convergence transform variables from settings, etc.
		'''
		del self._settings['convergence_transform']

	@property
	def manual_value(self):
		return self._manual_value

	@manual_value.setter
	def manual_value(self, value):
		'''
		Set the manually controlled value of this parameter. manual_value is always a list
		although this function will attempt to wrap invalid values in a list to see if it works.
		'''
		if self.validate_value(value):
			self._manual_value = value
		elif self.validate_value([value]):
			self._manual_value = [value]
		else:
			self._log('Blocked invalid value for {}: {}'.format(self.name, value))
		# print('{}.manual_value set to {}'.format(self.name, self.manual_value))

	def validate_value(self, value):
		'''Validates whether `value` is valid for this plugin.
		`value` would be the value/list of values passed from a single
		instrument. It is always a list (sometimes with a single value)
		e.g. [4]
		'''
		return True

	def get_transformed_convergence(self):
		'''By default this returns _converged_value but if the user has changed
		self.convergence_transform then that will be evaluated.
		'''
		c = self._converged_value
		if (type(c) is list and len(c)==1):
			c = c[0]
		try:
			val = eval(self._settings['convergence_transform'], globals(), dict(self.params.items()+[('convergence', c)]))
			if not self.is_convergence_transform_valid:
				self.is_convergence_transform_valid = True
				self.sig_is_converged_valid_changed.emit(True)
			return type(val) is list and val or [val]
		except Exception as e:
			if self.is_convergence_transform_valid:
				self.is_convergence_transform_valid = False
				self.sig_is_converged_valid_changed.emit(False)
				self._log('Error in convergence transform: '+e.message)
			return self._converged_value


	def update(self, dt):
		'''Updates self.value. Implemented by derived classes
		'''
		pass

	def _update_complete(self):
		'''Derived classes should call this after they have completed self.update()
		'''
		# Run the post update statement as set in the gui
		c = self._converged_value
		if (type(c) is list and len(c)==1):
			c = c[0]
		# calculate number of active instruments
		num_active = 0
		for value in self.params['activity']._param_state.itervalues():
			if type(value) is list and len(value)==1:
				if value[0] > 0.05:
					num_active += 1
		try:
			exec (self._settings['post_update_statement'], globals(), dict(self.params.items()+[('convergence', c), ('self', self), ('num_active', num_active)]))
			if not self.is_post_update_statement_valid:
				self.is_post_update_statement_valid = True
				self.sig_is_post_update_statement_valid_changed.emit(True)
		except Exception as e:
			if self.is_post_update_statement_valid:
				self.is_post_update_statement_valid = False
				self.sig_is_post_update_statement_valid_changed.emit(False)
				self._log('Error in post_update_statement: '+e.message)


class FloatParameter(Parameter):
	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)

		# Get initial ('default') value from settings, set a default if we don't have one
		self._settings.setdefault('default_value', 0.)

		#
		self._settings.setdefault('min', 0.)
		self._settings.setdefault('max', 1.)

		# Set operative values to the initial one
		self.value = [self._settings['default_value']]
		self.manual_value = [self._settings['default_value']]
		self._converged_value = [self._settings['default_value']]

		# Readonly values
		self.readonly_values += [

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
			# Get mean value over all instruments
			mean_input = 0.
			for inst in self._param_state:
				mean_input += self._param_state[inst][0]
			mean_input /= len(self._param_state)
			# Smoothly move self._converged_value[0] towards mean
			# In multiplicative steps, moving conv_rate of the way in each step
			if self._converged_value:
				self._converged_value[0] += conv_rate * (mean_input - self._converged_value[0])
			else:
				self._converged_value = [mean_input]

		# Set self.value[0] to linear blend between manual and converged -
		#  at conv_amt == 0, use self.manual_value[0]
		#  at conv_amt == 1, use self.get_transformed_convergence()[0]
		self.value[0] = conv_amt * self.get_transformed_convergence()[0] + (1.-conv_amt)*self.manual_value[0]
		self._update_complete()


class IntParameter(Parameter):
	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)

		# Get initial ('default') value from settings, set a default if we don't have one
		self._settings.setdefault('default_value', 0)

		#
		self._settings.setdefault('min', 0)
		self._settings.setdefault('max', 10)

		# Set operative values to the initial one
		self.value = [self._settings['default_value']]
		self.manual_value = [self._settings['default_value']]
		self._converged_value = [self._settings['default_value']]

		# Readonly values
		self.readonly_values += [

		]

	def validate_value(self, value):
		return type(value)==list and map(type, value)==[int]

	def update(self, dt):
		Parameter.update(self, dt)

		conv_amt = self._settings['convergence_amount']
		conv_rate = min(1,self._settings['convergence_rate'] * dt)

		# print 'self._param_state',self._param_state

		if self._param_state:
			# update using convergence
			# Get mean value over all instruments
			mean_input = 0.
			for inst in self._param_state:
				mean_input += self._param_state[inst][0]
			mean_input /= len(self._param_state)
			# Smoothly move self._converged_value[0] towards mean
			# In multiplicative steps, moving conv_rate of the way in each step
			if self._converged_value:
				self._converged_value[0] += conv_rate * (mean_input - self._converged_value[0])
			else:
				self._converged_value = [mean_input]

		# Set self.value[0] to linear blend between manual and converged -
		#  at conv_amt == 0, use self.manual_value[0]
		#  at conv_amt == 1, use self.get_transformed_convergence()[0]
		self.value[0] = int(round(conv_amt * self.get_transformed_convergence()[0] + (1.-conv_amt)*self.manual_value[0]))
		self._update_complete()


class NoteParameter(Parameter):
	'''Parameter that converges over the cycle of fifths'''

	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)

		# Get initial ('default') value from settings, set a default if we don't have one
		self._settings.setdefault('default_value', 0)
		# Set operative values to the initial one
		self.manual_value = [self._settings['default_value']]
		self.value = [self._settings['default_value']]
		self._converged_value = [self._settings['default_value']]

		# Readonly values
		self._converged_octave = self.manual_value[0] / 12.
		#  measured in number of fifths above C
		self._converged_tone = (self.manual_value[0]*7)%12
		self.readonly_values += [
			'_converged_octave',
			'_converged_tone',
		]

		self._disable_convergence_transform()

	def validate_value(self, value):
		return type(value)==list and map(type, value) in ([float], [int])

	def update(self, dt):
		Parameter.update(self, dt)

		conv_amt = self._settings['convergence_amount']
		conv_rate = min(1,self._settings['convergence_rate'] * dt)

		# Notes are considered in terms of letter (with C==0, c#==1, etc) and octave.
		# We normalize all notes to the range [0,12) and then remap them to [0,12) based
		# on how many fifths they are from C. So c->0, c#->7, d->2, etc
		# values are stored as floats to give us a notion of being midway between
		# two notes

		# Note that any variable below named '...note' is a normal count of semitones,
		# and any variable named '...tone' is a count of fifths.

		# Lists for translating from notes (semitones above C) to tones (fifths above C),
		# and vice versa
		to_fifths = {
			0:0, 1:7, 2:2, 3:9, 4:4, 5:11, 6:6, 7:1, 8:8, 9:3, 10:10, 11:5
		}
		from_fifths = {
			to_fifths[x] : x for x in to_fifths
		}

		# Get the current value of this parameter from all instruments into a straight list
		notes = []
		if self._param_state:
			for inst in self._param_state:
				notes.append(self._param_state[inst][0])
		notes = notes or self.manual_value

		# Get the mean octave, and mean tone number of all instruments
		octave = mean([note/12. for note in notes])
		tone = round(modular_mean([to_fifths[note%12] for note in notes])) % 12

		# Smoothly move self._converged_octave/tone towards mean
		# In additive steps, moving by maximum of conv_rate in each step
		if (octave > self._converged_octave):
			self._converged_octave += min(
				conv_rate * (octave - self._converged_octave),
				octave - self._converged_octave
				)
		elif (octave < self._converged_octave):
			self._converged_octave += max(
				conv_rate * (octave - self._converged_octave),
				octave - self._converged_octave
				)

		if (tone > self._converged_tone):
			self._converged_tone += min(
				conv_rate * sign(tone - self._converged_tone),
				tone - self._converged_tone
				)
		elif (tone < self._converged_tone):
			self._converged_tone += max(
				conv_rate * sign(tone - self._converged_tone),
				tone - self._converged_tone
				)

		#
		manual_octave = self.manual_value[0] / 12.
		manual_tone = to_fifths[self.manual_value[0] % 12]

		# Set target_octave/tone to linear blend between manual and converged -
		#  at conv_amt == 0, use self.manual_octave/tone
		#  at conv_amt == 1, use self._converged_octave/tone
		target_octave = conv_amt*self._converged_octave + (1.-conv_amt)*manual_octave
		target_tone = conv_amt*self._converged_tone + (1.-conv_amt)*manual_tone

		# Convert final tone back to note and save it as the value
		# round instead of truncate
		self.value = [int(target_octave*12 + 0.5) + from_fifths[int(target_tone+0.5)]]
		if self.value[0]<0:
			self.value[0] += 12

		# not used except displayed in gui for consistency
		self._converged_value = [self._converged_octave*12 + from_fifths[int(self._converged_tone+0.5)]]
		self._update_complete()


class TempoParameter(Parameter):
	'''Parameter that converges tempos.
	
	Splits tempos into 'octave' and 'offset' where eg. 120 BPM is one octave above 60 BPM
	so that their similarity can be recognised. The code is quite similar to NoteParameter.'''
	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)

		# Get initial ('default') value from settings, set a default if we don't have one
		self._settings.setdefault('default_value', 0.1)

		#
		self._settings.setdefault('min', 1.)
		self._settings.setdefault('max', 400.)

		# Set operative values to the initial one
		self.value = [self._settings['default_value']]
		self.manual_value = [self._settings['default_value']]
		self._converged_value = [self._settings['default_value']]

		# Readonly values
		linear_manual_tempo = math.log(self.manual_value[0], 2)
		self._converged_octave = linear_manual_tempo
		self._converged_offset = linear_manual_tempo - int(linear_manual_tempo)
		self._target_offset = self._converged_offset
		self.readonly_values += [
			'_converged_octave',
			'_converged_offset',
			'_target_offset',
		]

		self._disable_convergence_transform()

	def validate_value(self, value):
		return type(value)==list and map(type, value)==[float]

	def update(self, dt):
		Parameter.update(self, dt)

		conv_amt = self._settings['convergence_amount']
		conv_rate = min(1,self._settings['convergence_rate'] * dt)

		# print 'self._param_state',self._param_state

		if True: #self._param_state:
			# Get all the current values of this parameter from all instruments
			# into a straight list
			tempos = []
			for inst in self._param_state:
				tempos.append(self._param_state[inst][0])
			tempos = tempos or self.manual_value

			# Get the mean 'temporal octave',
			# and mean offset from that octave of all instruments
			linear_tempos = [math.log(tempo, 2) for tempo in tempos]
			mean_octave = mean(linear_tempos)
			mean_offset = modular_mean([tempo - int(tempo) for tempo in linear_tempos], 1.0)
			#print("tempo mean: " + str(mean_octave) + ", " + str(mean_offset))

			# Smoothly move self._converged_octave/offset towards mean
			# In additive steps, moving by maximum of conv_rate in each step
			if (mean_octave > self._converged_octave):
				self._converged_octave += min(
					conv_rate * (mean_octave - self._converged_octave),
					mean_octave - self._converged_octave
					)
			elif (mean_octave < self._converged_octave):
				self._converged_octave += max(
					conv_rate * (mean_octave - self._converged_octave),
					mean_octave - self._converged_octave
					)

			if (mean_offset > self._converged_offset):
				self._converged_offset += min(
					conv_rate * sign(mean_offset - self._converged_offset),
					mean_offset - self._converged_offset
					)
			elif (mean_offset < self._converged_offset):
				self._converged_offset += max(
					conv_rate * sign(mean_offset - self._converged_offset),
					mean_offset - self._converged_offset
					)
			#print("tempo converged: " + str(self._converged_octave) + ", " + str(self._converged_offset))

			#
			linear_manual_tempo = math.log(self.manual_value[0], 2)
			manual_octave = linear_manual_tempo
			manual_offset = linear_manual_tempo - int(linear_manual_tempo)
			#print("tempo manual: " + str(manual_octave) + ", " + str(manual_offset))

			# Set target_octave/offset to linear blend between manual and converged -
			#  at conv_amt == 0, use self.manual_octave/offset
			#  at conv_amt == 1, use self._converged_octave/offset
			target_octave = conv_amt*self._converged_octave + (1.-conv_amt)*manual_octave
			target_offset = conv_amt*self._converged_offset + (1.-conv_amt)*manual_offset
			#print("tempo target: " + str(target_octave) + ", " + str(target_offset))

			# Save target offset specifically, as we may use it per-instrument in
			# update_converged_state() below
			self._target_offset = target_offset

			# Convert final octave/offset back to tempo
			# and save it as the value
			# round instead of truncate
			self.value = [2 ** (round(target_octave) + target_offset)]

			# Also convert converged octave/offset back to note (in same way as target octave/offset above)
			# and save it (not used except displayed in gui for consistency)
			self._converged_value = [2 ** (round(self._converged_octave) + self._converged_offset)]
		self._update_complete()


class HarmonyParameter(Parameter):
	'''Parameter for handling sets of integers which measure harmony'''

	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)

		# Get initial ('default') value from settings, set a default if we don't have one
		self._settings.setdefault('default_value', [0,5,3])
		# Set operative values to the initial one
		self.value = self._settings['default_value']
		self.manual_value = self._settings['default_value']
		self._converged_value = self._settings['default_value']

		self._disable_convergence_transform()

	def validate_value(self, value):
		return type(value)==list and all((type(x)==int and 0<=x and x<12 for x in value))

	def update(self, dt):
		conv_amt = clamp(self._settings['convergence_amount'])

		# Get the current value of this parameter from all instruments into a straight list
		harmonies = []
		if self._param_state:
			for inst in self._param_state:
				harmonies.append(self._param_state[inst])
		# find converged harmony
		self._converged_value = []
		if harmonies:
			# Give it a length that is the mean of the lengths of the individual harmonies
			l = int(mean(map(len, harmonies)))
			# Take one note from each harmony in turn until we have the right length
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
			self.value = self._converged_value
		elif conv_amt==0 and self.manual_value:
			self.value = self.manual_value
		else:
			self.value = unique(splice(self.manual_value, self._converged_value))

		if not self.value:
			self.value = self._settings['default_value']
		self._update_complete()


class NarrativeParameter(Parameter):
	'''ManualParameter is a Parameter that is set only using manual_value (i.e. no
		convergence).
	'''

	def __init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function):
		Parameter.__init__(self, parameter_name, parameter_settings, param_world_state, parameters, log_function)
		del self._settings['convergence_amount']
		del self._settings['convergence_rate']
		self._settings.setdefault('default_value',0.)
		self._settings.setdefault('change_speed', 0.1)
		self._settings.setdefault('max_change_per_second', 0.05)
		self._settings.setdefault('amount_controlled_by_connections', 0.)
		self.manual_value = [self._settings['default_value']]
		self._target_value = [self._settings['default_value']]
		self.value_from_connections = [self._settings['default_value']]
		self.value = self.manual_value[:]
		self.readonly_values.remove('_converged_value')
		self.readonly_values.append('_target_value')
		self.readonly_values.append('value_from_connections')
		self._disable_convergence_transform()


	def validate_value(self, value):
		return type(value) is list and map(type, value)==[float]

	def update(self, dt):
		# gradually move towards target value
		amt = min(1,dt * clamp(self._settings['change_speed']))
		a = self._settings['amount_controlled_by_connections']
		max_change = dt * self._settings['max_change_per_second']
		self.target_value = [a * self.value_from_connections[0] + (1. - a) * self.manual_value[0]]
		change_amount = amt * (self.target_value[0] - self.value[0])
		if abs(change_amount) > max_change:
			change_amount = sign(change_amount) * max_change
		self.value[0] += change_amount
		self._update_complete()



class ConvergenceManager(QObject):
	def __init__(self, settings_dict, log_function, world_state, 
		connections, converged_state, visualizer_state, parent=None):
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
		self.visualizer_state = visualizer_state

		param_settings = self.settings.setdefault('parameters',{})
		param_types = {
			'activity': FloatParameter,
			# 'tempo': TempoParameter,
			'tempo' : FloatParameter,
			'loudness': FloatParameter,
			'root': NoteParameter,
			'harmony': HarmonyParameter,
			# 'detune': FloatParameter,
			# 'note_frequency': FloatParameter,
			# 'note_density': FloatParameter,
			# 'attack': FloatParameter,
			'brightness': FloatParameter,
			'roughness': FloatParameter,
			'narrative': NarrativeParameter,
			'narrative_slot': IntParameter,
			'narrative_rhythm_volume': FloatParameter,
			'narrative_harmony_volume': NarrativeParameter,
		}
		self.params = {}
		# Keys: (str) Parameter name
		# Values: Instance of a Parameter subclass

		# For each parameter
		# instantiate parameter object subclass,
		# and store in self.params
		self.params.update({
			name : typ(
				parameter_name = name,
				parameter_settings = param_settings.setdefault(name, {}),
				param_world_state = self.world_state.setdefault(name, {}),
				parameters = self.params,
				log_function = lambda x, module=name: self.log(x, module=name)
				)
			for name,typ in param_types.iteritems()
		})

		#
		self.elapsed_timer = QElapsedTimer()
		self.elapsed_timer.start()
		self.time_of_last_update = 0.

		# Every 0.2 seconds, run self.update()
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
		#	'activity': [0.],
		#	'tempo': [89.],
		#	'loudness': [0.5],
		#	'root': [24],
		#	'harmony': [0, 7, 3, 10, 8],
		#	'detune': [0.],
		#	'note_frequency': [2.],
		#	'note_density': [0.5],
		#	'attack': [0.1],
		#	'brightness': [0.5],
		#	'roughness': [0.2],
		# }


	def set_manual_value(self, param_name, value):
		# print 'set_manual_value({},{})'.format(param_name, value)
		# Wrap the value in a list if it isn't already
		if type(value) is list:
			self.params[param_name].manual_value = value
		else:
			self.params[param_name].manual_value = [value]

	def update(self):
		# Get time since last update
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
		self.update_visualizer_state()

	def update_narrative(self):
		'''Update narrative parameter based on instrument connections'''
		# Get the mean connection level across every pair of instruments
		# (not including self-connections)
		#  UPDATE : Now just take highest three connection values
		def sq(x):
			return x*x
		instruments = self.connections.keys()
		narrative = 0.
		count = 0.
		connection_values = [0., 0., 0.] + [
		self.connections[inst1][inst2] for inst1 in instruments  
			for inst2 in instruments if inst1!=inst2]
		connection_values.sort()
		#narrative = sum(connection_values[-3:])/3.
		top_three = [min(1., x) for x in connection_values[-3:]]
		# print 'top_three', top_three, sum(top_three)
		narrative = sum(top_three)/3.
		# for inst1 in instruments:
		# 	for inst2 in (x for x in instruments if x!=inst1):
		# 		if self.connections[inst1][inst2] > 0.4:
		# 			narrative += 1.
		# 		else:
		# 			narrative += self.connections[inst1][inst2]
		# 		count += 1.
		# if count:
		# 	narrative /= count
		# # Save it in the NarrativeParameter in self.params['narrative']
		self.params['narrative'].value_from_connections = [narrative]

	def update_converged_state(self):
		'''Write values from self.params to self.converged_state.
		'''
		# apply this converged_values to all instruments
		for inst in self.connections.keys():
			for param in self.params:
				# # If it's the tempo param, it requires special treatment
				# # as different instruments may get different converged value
				# if param == "tempo":
				# 	self.converged_state.setdefault("tempo", {})
				# 	# If instrument doesn't already have a tempo value then give it the
				# 	# full converged tempo made of both averaged octave and averaged offset.
				# 	if inst not in self.world_state[param]:
				# 		self.converged_state["tempo"][inst] = self.params[param].value
				# 	# Else if instrument already has a tempo then just slide it (up or down,
				# 	# whichever is the shortest modular distance) to the the averaged offset
				# 	else:
				# 		existing_tempo = self.world_state[param][inst][0]
				# 		linear_existing_tempo = math.log(existing_tempo, 2)
				# 		existing_offset = linear_existing_tempo - int(linear_existing_tempo)
				# 		self.converged_state["tempo"][inst] = [existing_tempo * 2**modular_distance(existing_offset, self.params[param]._target_offset, 1.0)]
				# # For all other params, all instruments get the same converged value
				# else:
				self.converged_state.setdefault(param,{})[inst] = self.params[param].value

	def update_visualizer_state(self):
		'''Copy over whichever parameters are needed by the
		Visualizer'''
		self.visualizer_state['narrative'] = self.params['narrative'].value

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
