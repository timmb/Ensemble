# -*- coding: utf-8 -*- 

from PySide.QtCore import *
from txosc.osc import *
from time import time as currentTime
from math import fmod

class OutputProcessor(QThread):
	'''OutputProcessor reads information from the converged state and
	sends it to the clients.'''

	def __init__(self, converged_state, instrument_states, visualizer_state, 
		settings, internal_settings, convergence_manager, osc_send_function,
		log_function):
		'''`converged_state` is a State object (for now, dictionary) 
		containing information to be broadcast to the clients in the form:
		parameter_name -> { instrument_name -> value }
		where `value` is always a list.

		`instrument_states` is a dictionary such that 
		instrument_states[instrument_name]['address'] = (host, port)
		for all instruments in converged_state

		`visualizer_state` is a dictionary containing any parameter
		values that need to be sent to the visualizer. For example
		visualizer_state['connections'] = dict from inst0 -> inst1 -> connection_amount
		visualizer_state['narrative'] = [float]
		It is updated by ConvergenceManager.

		`internal_settings` is a dictionary containing non-persistent program
		settings such as 'visualizer_address'

		`osc_send_function is a function to send osc messages with usage
		osc_send_function(txosc.osc.Message, (host,port))
		'''
		QThread.__init__(self)
		self.converged_state = converged_state
		self.instrument_states = instrument_states
		self.settings = settings
		self.internal_settings = internal_settings
		self.convergence_manager = convergence_manager
		self.visualizer_state = visualizer_state
		self.send = osc_send_function
		self.log = log_function

		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self._update)
		self.update_timer.setInterval(500)

		# Visualizer runs at a faster timer
		self.viz_update_timer = QTimer(self)
		self.viz_update_timer.timeout.connect(self._update_viz)
		self.viz_update_timer.setInterval(200)
		# visualizer sender may print warning message - this is to prevent it spamming too much
		self.viz_last_warning_message_time = 0

		# Calculate instrument order for the visualizer
		self.viz_instrument_order_update_timer = QTimer(self)
		self.viz_instrument_order_update_timer.timeout.connect(self._update_instrument_order)
		self.viz_instrument_order_update_timer.setInterval(413)

		self.elapsed_timer = QElapsedTimer()
		self.elapsed_timer.start()


		self.beat_update_timer = QTimer(self)
		self.beat_update_timer.setInterval(1)
		self.beat_update_timer.timeout.connect(self._update_beat_message)
		self.beat_update_timer.start()
		self.beat_difference_millis = 1.
		self.prev_time_mod = 0

		self.beat_num = 0

	def run(self):
		'''Start the thread sending messages.
		'''
		self.update_timer.start()
		self.viz_update_timer.start()
		self.viz_instrument_order_update_timer.start()
		self.exec_()
		self.viz_instrument_order_update_timer.stop()
		self.viz_update_timer.stop()
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
		tempo = self.convergence_manager.params['tempo'].value[0]
		# print 'tempo', tempo
		self.beat_difference_millis = 1000. / (max(1,tempo) / 60.)

	def _update_viz(self):
		'''Callback for visualiser ('viz') timer, sends updated values to the viz.
		'''
		viz_address = self.internal_settings['visualizer_address']
		if viz_address:
			for param, value in self.visualizer_state.items():
				osc_address = '/viz/' + param
				if param=='connections':
					connections = value
					instruments = self.internal_settings['calculated_instrument_order']
					# see http://timmb.com/ensemblewiki/index.php?title=Protocols#Stabilizer_.E2.86.92_Visualizer
					args = [len(instruments)]
					# right for loop is nested inside left for loop
					args += [connections[instruments[i]][instruments[j]] for i in range(len(instruments)) for j in range(len(instruments))]
					assert len(args) == 1+len(instruments)*len(instruments)
				elif param=='debug':
					args = [int(value)]
					if value:
						# provide instrument names
						args.extend((x.encode('ascii', 'ignore') for x in self.internal_settings['calculated_instrument_order']))
				else:
					args = value
				message = Message(osc_address, *args)
				self.send(message, viz_address)

	def _update_instrument_order(self):
		'''Updates calculated_instrument_order, missing_instruments and surplus_instruments
		based on canonical_instrument_order and the connected instruments.
		'''
		instrument_order = self.settings['instrument_order']
		detected_instruments = self.visualizer_state['connections'].keys()

		calculated_instruments = [i for i in instrument_order if i in detected_instruments]
		surplus_instruments = [i for i in detected_instruments if i not in instrument_order]
		missing_instruments = [i for i in instrument_order if i not in detected_instruments]

		self.internal_settings['calculated_instrument_order'] = calculated_instruments
		self.internal_settings['missing_instruments'] = missing_instruments
		self.internal_settings['surplus_instruments'] = surplus_instruments

		if surplus_instruments:
			t = currentTime()
			if t - self.viz_last_warning_message_time > 10:
				self.log('Warning, the following instruments are missing from the visualization order: {}'.format(surplus_instruments));
				self.viz_last_warning_message_time = t


	def _update_beat_message(self):
		'''Checks to see if a beat message needs to be sent and
		sends it if it does'''
		t_millis = self.elapsed_timer.elapsed()
		time_mod = fmod(t_millis, self.beat_difference_millis)
		# print 'beat_update', t_millis, time_mod, self.beat_difference_millis
		if time_mod < self.prev_time_mod:
			self.send_beat()
		self.prev_time_mod = time_mod

	def send_beat(self):
		'''Send beat message
		'''
		# print 'beat message'
		# print 'beat', self.beat_num
		self.beat_num += 1
		for instrument in self.instrument_states:
			address = self.instrument_states[instrument]['address']
			if address:
				self.send(Message('/beat'), address)





