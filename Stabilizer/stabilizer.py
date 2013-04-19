import sys
import Queue

from PySide import QtCore, QtGui, QtXml
from PySide.QtCore import *

from txosc import osc
from txosc import dispatch
from txosc import async

from time import gmtime, strftime
from datetime import datetime
from datetime import timedelta

from gui import *
from input_processor import *
from state import *
from plugin import *
from output_processor import *
from visualization import *

import twisted

idle_loop = Queue.Queue()

osc_messages = Queue.Queue()

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


class ListModel(QtCore.QAbstractListModel):
    '''
    A simple implementation of logs model
    '''
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


class Stabilizer(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv, True)
        self.event_log = ListModel([])
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        self.osc_receiver = dispatch.Receiver()
        self.osc_receiver.fallback = self.osc_message_callback
        self.is_listening = False
        self._server_port = None
        self.aboutToQuit.connect(self.shutdown)


    def shutdown(self):
        self.log("Shutting down")
        print("Stabilizer.shutdown()")
        self.stop_listening()
        self.dispatcher.stop()
        self.dispatcher.wait()

    def start_listening(self) :
        global PORT
        if self.is_listening:
            stop_listening()
        try:
            self._server_port = reactor.listenUDP(PORT, async.DatagramServerProtocol(self.osc_receiver))
            self.is_listening = True 
            self.log("Listening at %d ..." % PORT)      
        except twisted.internet.error.CannotListenError as e:
            self.log("Error listening: "+e.message)
    
    def stop_listening(self):
        global PORT
        if self._server_port:
            self._server_port.stopListening()
        self.is_listening = False
        self.log("Stopped listening at %d ..." % PORT)         

    def osc_message_callback(self, message, client):
        osc_messages.put(message)
        self.log("%s: %s" % (client, message) )

    def log(self, s, module="Stabilizer"):       
        time = datetime.now()
        self.event_log.addItem("[%s] %s %s" % (time.strftime("%H:%M:%S.%f")[:-3], module, s))

if __name__=='__main__':
    app = Stabilizer()
    # Set up twisted events
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    reactor.addSystemEventTrigger('before', 'shutdown', reactor.stop)
    # Create gui
    main_window = MainWindow(app)
    main_window.show()
    # start event loop
    app.exec_()
    app.shutdown()

