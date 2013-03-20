class Plugin(object):
	'''A plugin is an object that reads from the world state and writes
	to the converged state. It does so by registering a callback to changes
	within the world state.
	'''
	def setup(self, world_state):
		raise NotImplementedError('This needs to be implemented by a derived class')