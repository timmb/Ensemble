# -*- coding: utf-8 -*-

import json
from PySide.QtCore import *
from PySide.QtGui import *
import datetime
from collections import Mapping

class Settings(dict):
	'''
	Settings is a special type of dictionary that can read and write its values to
	a json file.

	It has a special json file called 'settings.json' that it defaults to but settings
	may also be loaded and saved to other 'snapshot' files.
	'''
	sig_settings_loaded = Signal()

	def __init__(self, initial_value={}, log_function=None):
		dict.__init__(self)
		self.settings_filename = 'settings.json'
		self.log = log_function or self.log
		self.update(initial_value)

	def log(self, message):
		print('Settings:',message)

	def save(self):
		self.save_snapshot(self.settings_filename)

	def reload(self):
		self.load_snapshot(self.settings_filename)

	def save_snapshot_auto(self):
		date_string = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
		filename = self.settings_filename[:-5]+'.'+date_string+'.json'
		save_snapshot(filename)

	def save_snapshot(self, filename):
		with open(filename, 'w') as out:
			out.write(json.dumps(self, indent=4))
			self.log('Settings saved to '+filename)

	def load_snapshot(self, filename):
		with open(filename, 'r') as f:
			try:
				d = json.load(f)
				self.update(d)
				self.log('Settings successfully loaded from {}'.format(filename))
			except Exception as e:
				self.log('Error loading settings from {}: {} {}'.format(filename, e, e.message))

	def update(self, new_dict):
		'''Updates values in this dictionary using soft_update to maintain references
		to mappings where they exist.
		'''
		soft_update(self, new_dict)

def soft_update(dest, d):
	'''Recursively update dest with values from d without overwriting any references.
	See http://stackoverflow.com/a/14048316/794283
	'''
	# TODO: check this is right... something seems wrong.
	# Also, prevent mappings from being added to dest if they were not there previously
	for k,v in d.iteritems():
		if isinstance(v, Mapping):
			r = soft_update(dest.get(k, {}), v)
			dest[k] = r
		elif isinstance(d, Mapping):
			dest[k] = d[k]
		else:
			dest = {k: d[k]}
	return dest



