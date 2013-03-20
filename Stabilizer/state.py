from PySide.QtCore import *

class State(QThread):
	'''A state is a set of key, value pairs with functionality to register
	callbacks to when these elements change. Callbacks are called from a 
	separate thread.
	'''

	def __init__(self):
		QThread.__init__(self)
		self._state = {}
		self._callbacks = {}
		self.is_running = False

	def add_callback(self, key, callback):
		'''Register callback `callback` to be called when `key` changes within
		this state.
		'''
		self._callbacks.setdefault(key, []).append(callback)

	def set(key, new_value):
		'''Set the value of key to new_value in this state. Callbacks will be
		called from a different thread.
		'''
		# to do
		pass

	def run(self):
		'''Called when the thread is started. Every n seconds any callbacks that need
		calling are called.'''
		self.is_running = True
		while self.is_running:
			# to do
			pass

	def stop(self):
		'''Stop the thread from processing callback events.
		'''
		self.is_running = False

world_state = State()
converged_state = State()