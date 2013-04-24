# -*- coding: utf-8 -*- 

from PySide.QtCore import *
from txosc.osc import *

class OutputProcessor(QThread):
	'''OutputProcessor reads information from the converged state and
	sends it to the clients.'''

	def __init__(self, converged_state, instrument_states, osc_send_function, 
		log_function):
		'''`converged_state` is a State object (for now, dictionary) 
		containing information to be broadcast to the clients in the form:
		parameter_name -> { instrument_name -> value }
		where `value` is always a list.

		`instrument_states` is a dictionary such that 
		instrument_states[instrument_name]['address'] = (host, port)
		for all instruments in converged_state

		`osc_send_function is a function to send osc messages with usage
		osc_send_function(txosc.osc.Message, (host,port))
		'''
		QThread.__init__(self)
		self.converged_state = converged_state
		self.instrument_states = instrument_states
		self.send = osc_send_function
		self.log = log_function

		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self._update)
		self.update_timer.setInterval(500)

	def run(self):
		'''Start the thread sending messages.
		'''
		self.update_timer.start()
		self.exec_()
		self.update_timer.stop()

	def _update(self):
		'''Callback for timer, sends updated values to all clients
		'''
		for instrument in self.instrument_states:
			destination = self.instrument_states[instrument]['address']
			if not destination:
				self.log('Error: no destination address found for instrument {}'.format(instrument))
				continue
			# inst_state is for this given instrument: { param -> value }
			# as things run asynchronously it's possible we don't yet have
			# a converged value for all parameters - hence the extra if
			# in this list comp.
			inst_state = { param : self.converged_state[param][instrument]
							for param in self.converged_state
							if instrument in self.converged_state[param]
						 }
			for param in inst_state:
				osc_address = '/state/{}/{}'.format(instrument, param)
				args = []
				for v in inst_state[param]:
					args.append(createArgument(v))
				message = Message(osc_address, *args)
				self.send(message, destination)







