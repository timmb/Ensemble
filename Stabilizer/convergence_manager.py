import time

class ConvergenceManager(object):
	def __init__(self, settings_dict):
		self.settings = settings_dict
		self.default_values = {
			'activity': [0.],
			'tempo': [120.],
			'loudness': [0.5],
			'root': [24],
			'harmony': [0, 7, 3, 10, 8],
			'detune': [0.],
			'note_frequency': [2.],
			'note_density': [0.5],
			'attack': [0.1],
			'brightness': [0.5],
			'roughness': [0.2],
		}
		self.single_valued_parameters = [
			'activity',
			'tempo',
			'loudness',
			'immediate_pitch',
			'root',
			'detune',
			'note_density',
			'note_frequency',
			'attack',
			'brightness',
			'roughness',
		]

		# this is used for the universal convergence method (temp function)
		self.converged_values = dict(self.default_values)
		self.last_time_of_universal_convergence = None




	def universal_convergence_method(self, world_state, connections, converged_state):
		'''This is called by stabilizer on a timer.

		converged_values are updated based on world_state regardless of connections.
		converged_state is set for all instruments based on converged_values
		'narrative' is updated based on connections
		'''
		convergence_speed = self.settings['convergence_speed']
		narrative_speed = self.settings['narrative_speed']
		narrative_decay = self.settings['narrative_decay']

		self.last_time_of_universal_convergence = self.last_time_of_universal_convergence or time.time()
		t = time.time()
		dt = t - self.last_time_of_universal_convergence
		self.last_time_of_universal_convergence = t
		alpha = max(0,min(1,convergence_speed*dt))
		narrative_alpha = max(0,min(1,narrative_speed*dt))

		params = set(world_state.keys() + self.converged_values.keys())
		instruments = connections.keys()

		# update converged state for those parmaeters that we've received
		for p in set(world_state.keys()).intersection(self.single_valued_parameters):
			# import pdb; pdb.set_trace()
			set_values = [x[0] for x in world_state[p].values()]
			if set_values:
				value = sum(set_values)/len(set_values)
				self.converged_values[p][0] += alpha*(value - self.converged_values[p][0])

		# todo: parameters that aren't single valued

		# update narrative
		narrative = 0.
		count = 0.
		for inst1 in instruments:
			for inst2 in (x for x in instruments if x!=inst1):
				narrative += connections[inst1][inst2]
				count += 1.
		if count:
			narrative /= count
		old_narrative = self.converged_values.setdefault('narrative', [0.])[0]
		old_narrative *= 1. - (1.-narrative_decay)*dt
		self.converged_values['narrative'][0] += narrative_alpha*(narrative - old_narrative)

		# apply this converged_values to all instruments
		for inst in instruments:
			for param in converged_values:
				converged_state.setdefault(param,{})[inst] = converged_values[param]
