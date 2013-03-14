import sys
import Queue

import mainWindows
from PySide import QtCore, QtGui, QtXml
from PySide.QtCore import *
from PySide.QtGui import *

from txosc import osc
from txosc import dispatch
from txosc import async

from time import gmtime, strftime
from datetime import datetime
from datetime import timedelta

idle_loop = Queue.Queue()

PORT = 1123

class ThreadDispatcher(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.parent = parent

    def run(self):
        while True:
            callback = idle_loop.get()
            if callback is None:
                break
            QtGui.QApplication.postEvent(self.parent, _Event(callback))

    def stop(self):
        idle_loop.put(None)
        self.wait()

class _Event(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, callback):
        #thread-safe
        QtCore.QEvent.__init__(self, _Event.EVENT_TYPE)
        self.callback = callback

'''
A simple implementation of logs model
'''
class ListModel(QtCore.QAbstractListModel):
	def __init__(self, mlist):
		QtCore.QAbstractListModel.__init__(self)
		self._items = mlist

	def rowCount(self, parent = QModelIndex()):
		return len(self._items)

	def data(self, index, role = Qt.DisplayRole):
		if role == QtCore.Qt.DisplayRole:
			return str(self._items[index.row()])

	def setData(self, index, value, role = Qt.EditRole):
		return False

	def flags(self, index):
		return Qt.ItemIsSelectable

	def addItem(self, item):
  		# The str() cast is because we don't want to be storing a Qt type in here.
  		self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
  		self._items.insert(0, str(item))
  		self.endInsertRows()

class Main(QtGui.QMainWindow):
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)
		self.ui = mainWindows.Ui_MainWindow()
		self.ui.setupUi(self)

		self._model = ListModel([])

		self.dispatcher = ThreadDispatcher(self)
		self.dispatcher.start()

		self.osc_receiver = dispatch.Receiver()
		self._server_port = reactor.listenUDP(PORT, async.DatagramServerProtocol(self.osc_receiver))
		self.log("Listening at %d ..." % PORT)
		self.osc_receiver.fallback = self.fallback
		
		self.ui.listView.setModel(self._model)

		self.show()		

	def fallback(self, message, address):
		self.log("%s: %s" % (address, message) )

	def log(self, s):
		time = datetime.now()
		self._model.addItem("[%s] %s" % (time.strftime("%H:%M:%S.%f")[:-3], s))

app = QtGui.QApplication(sys.argv)

import qt4reactor
qt4reactor.install()
from twisted.internet import reactor

main = Main()
app.exec_()
main.dispatcher.stop()