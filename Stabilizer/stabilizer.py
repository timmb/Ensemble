# -*- coding: utf-8 -*- 

import sys
import Queue

from PySide import QtCore, QtGui, QtXml
from PySide.QtCore import *

from txosc import osc
from txosc import dispatch
from txosc import async

import time
from time import gmtime, strftime
from datetime import datetime
from datetime import timedelta
from collections import deque

from gui import *
from input_processor import *
# from state import *
from output_processor import *
from visualization import *
from connection_detector import *
from ConvergenceManager import ConvergenceManager
from Settings import Settings

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
    def __init__(self, mdeque):
        QtCore.QAbstractListModel.__init__(self)
        self._items = mdeque

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
        self._items.appendleft(str(item))
        self.endInsertRows()








class Stabilizer(QApplication):

    def __init__(self):
        QApplication.__init__(self, sys.argv, True)

        # ** All persistent settings need to be put in here **
        self.settings = Settings({
            # Counter clockwise order starting at instrument 0 (from visualizer's point of view)
           'instrument_order' : ['tim','daniel','sus','dom','kacper','panos','tadeo','wallace']
        }, log_function=lambda x, module="Settings": self.log(x, module))

        self.event_log = ListModel(deque(maxlen=1000))
        self.dispatcher = ThreadDispatcher(self)
        self.dispatcher.start()
        
        # OSC input
        self.osc_receiver = dispatch.Receiver()
        self.osc_receiver.fallback = self.osc_message_callback
        self.is_listening = False
        self._input_socket = None
        # OSC output over UDP
        self.osc_sender = async.DatagramClientProtocol()
        # defined in open_output_socket below
        self._output_socket = None

        # program state

        # ** Non-persistent internal settings go here ** #
        self.internal_settings = {
            # Of form (host, port)
            'visualizer_address' : None,
            # For providing feedback in gui:
            'calculated_instrument_order' : [],
            'missing_instruments' : [],
            'surplus_instruments' : [],
        }
        
        self.enable_log_incoming_messages = False
        self.enable_log_outgoing_messages = False

        self.aboutToQuit.connect(self.shutdown)

        # for now just use dictionaries to represent states
        # parameter -> { instrument -> value }
        self.world_state = {}
        # parameter -> { instrument -> converged_value }
        self.converged_state = {}
        # properties of an instrument:
        # instrument -> { property -> value }
        # also contains the state of the instrument:
        # instrument -> { 'state' -> { parameter -> value } }
        # instrument -> { 'address' -> (host, port) }
        self.instruments = {}
        # instrument -> { instrument -> connection_amount }
        self.connections = {}
        # State variables that are to be sent to the visualizer
        # property -> value (where value is always a list)
        self.visualizer_state = {
            'connections' : self.connections,
            'debug' : False,
        }


        self.input_processor = InputProcessor(
            self.world_state, 
            self.instruments,
            self.internal_settings,
            self.visualizer_state,
            lambda message,module='InputProcessor': self.log(message, module))

        self.connection_detector = ConnectionDetector(self.connections, 
            self.instruments)

        self.convergence_manager = ConvergenceManager(
            self.settings, 
            lambda message,module='ConvergenceManager': self.log(message, module),
            self.world_state,
            self.connections,
            self.converged_state,
            self.visualizer_state,
            self,
            )

        self.output_processor = OutputProcessor(
            self.converged_state,
            self.instruments,
            self.visualizer_state,
            self.settings,
            self.internal_settings,
            self.convergence_manager,
            self.send_osc,
            lambda message,module='OutputProcessor': self.log(message, module)
            )
        
        self.settings.reload()


    def shutdown(self):
        self.log("Shutting down")
        print("Stabilizer.shutdown()")
        self.stop_sending()
        self.stop_listening()
        self.dispatcher.stop()
        
        self.output_processor.wait()
        self.dispatcher.wait()

    # def open_output_socket(self):
    #     '''This needs to happen after reactor has been defined.
    #     '''
    #     self.osc_sender_port = reactor.listenUDP(0, self.osc_sender)
    #     self.log('OSC output socket opened on port {}'.format(self.osc_sender_port))

    def start_sending(self):
        '''Starts the output processor thread to send osc messages.'''
        # wait for any previous threads to finish
        self.output_processor.quit()
        self.output_processor.wait()
        if not self._output_socket:
            self._output_socket = reactor.listenUDP(0, self.osc_sender)
            self.log('OSC output socket opened: {}'.format(self._output_socket))
        self.output_processor.start()
        self.log('OSC output started')

    @property
    def is_sending(self):
        return self._output_socket != None

    def stop_sending(self):
        '''Stops the output processor thread stopping outgoing osc messages.'''
        self.output_processor.quit()
        self.log('OSC output stopped. Closing socket {}'.format(self._output_socket))
        if self._output_socket:
            self._output_socket.stopListening()
            self._output_socket = None

    def start_listening(self) :
        global PORT
        if self.is_listening:
            self.stop_listening()
        try:
            self._input_socket = reactor.listenUDP(PORT, async.DatagramServerProtocol(self.osc_receiver))
            self.is_listening = True 
            self.log("Listening at %d ..." % PORT)      
        except twisted.internet.error.CannotListenError as e:
            self.log("Error listening: "+e.message)
    
    def stop_listening(self):
        global PORT
        if self._input_socket:
            self._input_socket.stopListening()
            self._input_socket = None
        self.is_listening = False
        self.log("Stopped listening at %d ..." % PORT)         

    def osc_message_callback(self, message, client):
        # osc_messages.put(message)
        if self.enable_log_incoming_messages:
            self.log("%s: %s" % (client, message) )
        if message.address.startswith('/convergence/'):
            self.convergence_manager.osc_message_callback(message, client)
        else:
            self.input_processor.osc_message_callback(message, client)
        self.connection_detector.update()

    def send_osc(self, message, destination):
        if not self._output_socket:
            self.log('Error: cannot start osc message as the output socket has'
                +' not been opened.')
            return
        if self.enable_log_outgoing_messages:
            self.log('-> {}: {}'.format(message, destination))
        try:
            self.osc_sender.send(message, destination)
        except Exception as e:
            pass


    def log(self, s, module="Stabilizer"):       
        time = datetime.now()
        self.event_log.addItem("[%s] %s: %s" % (time.strftime("%H:%M:%S.%f")[:-3], module, s))

def main():
    global reactor
    app = Stabilizer()

    # Set up twisted events
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ## print all loaded modules:
    reactor.addSystemEventTrigger('before', 'shutdown', reactor.stop)
    app.start_sending()
    app.start_listening()
    # Create gui
    main_window = MainWindow(app)
    main_window.show()
    # main_window.start_or_stop_listening(True)
    # start event loop
    app.exec_()
    app.settings.save()

if __name__=='__main__':
    main()
