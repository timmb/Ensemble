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

from gui import *
from input_processor import *
# from state import *
from plugins.plugin import *
from output_processor import *
from visualization import *
from connection_detector import *
from convergence_manager import *

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







def temp_convergence_method(world_state, connections, converged_state, default_values):
    '''Very basic convergence function. This will be replaced with
    a proper plugins-based structure in the future.

    Assumes `connections` is a complete mapping with respect to the instruments 
    described by `world_state`
    '''
    converge_using_mean = [
        'activity',
        'tempo',
        'loudness',
        'immediate_pitch',
        'root',
        'detune',
        'note_density',
        'note_frequency',
        'attack',
        'brightness',
        'roughness',
    ]
    converge_using_mean = [p for p in converge_using_mean if p in world_state]

    for param in converge_using_mean:
        insts = world_state[param]
        for inst0 in insts:
            total_weight = 0
            total = 0.
            for inst1 in insts:
                weight = connections[inst0][inst1]
                total_weight += weight
                total += world_state[param][inst1][0] * weight
            if total_weight==0:
                mean = world_state[param][inst0][0]
            else:
                mean = total/total_weight
            if type(world_state[param][inst0][0])==int:
                mean = int(mean)
            if inst0 in converged_state.setdefault(param,{}):
                converged_state[param][inst0][0] += 0.001*(mean-converged_state[param][inst0][0])
            else:
                converged_state[param][inst0] = [mean]

    # if a parameter hasn't been set then use the default value
    for param in default_values:
        for inst in connections:
            if param not in converged_state:
                converged_state[param] = {}
            if inst not in converged_state[param]:
                converged_state[param][inst] = default_values[param][:]



class Stabilizer(QApplication):

    def __init__(self):
        QApplication.__init__(self, sys.argv, True)

        self.settings = {
            'convergence_speed': 1.,
            'narrative_speed': 1.,
            'narrative_decay': 0.99
        }

        self.event_log = ListModel([])
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

        #settings
        
        self.enable_log_incoming_messages = False
        self.enable_log_outgoing_messages = False
        self.enable_calculate_convergence = True
        


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


        self.input_processor = InputProcessor(self.world_state, 
            self.instruments, self.log)
        self.connection_detector = ConnectionDetector(self.connections, 
            self.instruments)
        self.output_processor = OutputProcessor(
            self.converged_state,
            self.instruments,
            self.send_osc,
            lambda message,module='OutputProcessor': self.log(message, module)
            )
        self.convergence_manager = ConvergenceManager(self.settings)




        self.convergence_timer = QTimer(self)

        self.convergence_timer.timeout.connect(
            lambda: self.enable_calculate_convergence 
                and self.convergence_manager.universal_convergence_method(
                self.world_state,
                self.connections,
                self.converged_state,
                ))
        self.convergence_timer.setInterval(100)
        self.convergence_timer.start()


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
        osc_messages.put(message)
        if self.enable_log_incoming_messages:
            self.log("%s: %s" % (client, message) )
        self.input_processor.osc_message_callback(message, client)
        self.connection_detector.update()

    def send_osc(self, message, destination):
        if not self._output_socket:
            self.log('Error: cannot start osc message as the output socket has'
                +' not been opened.')
            return
        if self.enable_log_outgoing_messages:
            self.log('-> {}: {}'.format(message, destination))
        self.osc_sender.send(message, destination)


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
    app.start_sending()
    # Create gui
    main_window = MainWindow(app)
    main_window.show()
    main_window.start_or_stop_listening(True)
    # start event loop
    app.exec_()

