class Plugin(object):
	'''A plugin is an object that reads from the world state and writes
	to the converged state. It does so by registering a callback to changes
	within the world state.
	'''

	def __init__(self, parameter_name):
		self.name = parameter_name

	def validate_value(self, value):
		'''Validates whether `value` is valid for this plugin.
		`value` would be the value/list of values passed from a single
		instrument. It is always a list (sometimes with a single value)
		e.g. [4]
		'''
		return True

	def setup(self, world_state, converged_state):
		raise NotImplementedError('This needs to be implemented by a derived class')


