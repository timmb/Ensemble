from PySide.QtCore import *

class OutputProcessor(QThread):
	'''OutputProcessor reads information from the converged state and
	sends it to the clients.'''

	def __init__(self, converge_state, client_addresses):
		'''`converge_state` is a State object containing information to be
		broadcast to the clients. Clients are referred to by a name
		and client_addresses should be a dictionary resolving these
		names to an IP address.
		'''
		QThread.__init__(self)
		self.converge_state = converge_state
		self.client_addresses = client_addresses
		self.is_running = False
		self.update_period = 0.5 # how frequently in seconds clients are updated

	def run(self):
		'''Start the thread sending messages.
		'''
		self.is_running = True
		while self.is_running:
			# to do
			pass

	def stop(self):
		'''Stop the thread sending messages.
		'''
		self.is_running = False