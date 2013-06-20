class ConnectionDetector(object):
	'''Detects connections between instruments based on the world_state.
	'''

	def __init__(self, connections, instruments):
		'''
		`connections` is a two dimensional dictionary of the form:
			connections[instrument1][instrument2] -> connection_strength
			where instrument1 and instrument2 are instrument names (string)
			and connection_strength is a float in [0,1]
			and x==y => connections[x][y] == 1
		`instruments` is a dictionary where the keys are instrument names (string)
			and the values are dictionaries where one key is 'state' mapped to a 
			dicitionary mapping parameter names to parameter values
			so:
			instruments[inst_name]['state'][param] = value
			iff
			world_state[param][inst_name] = value

		'''
		self.connections = connections
		self.instruments = instruments


	def update(self):
		names = [inst_name for inst_name in self.instruments]
		for i in range(len(names)):
			for j in range(i,len(names)):
				state_i = self.instruments[names[i]]['state']
				state_j = self.instruments[names[j]]['state']
				# NB all values should be floats
				connection = 0.
				if 'activity' in state_i and 'activity' in state_j:
					# remember all state values are lists
					connection = min(state_i['activity'][0], state_j['activity'][0])
				# instruments are always connected to themselves
				if names[i] == names[j]:
					connection = 1.
				# instrument names might not yet be in the connections list
				# so use default value of {}
				self.connections.setdefault(names[i],{})[names[j]] = connection
				self.connections.setdefault(names[j],{})[names[i]] = connection
