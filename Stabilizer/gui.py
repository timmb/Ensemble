'''
This module contains code to hook up the GUI (generated using the Qt UI 
designer) to the rest of the code and any hand-written GUI code.
'''


import UX.MainWindow
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import QTimer
from pprint import pformat
from lib.texttable import Texttable



def assign(var, value):
    var = value


class MainWindow(QtGui.QMainWindow):
    def __init__(self, stabilizer, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = UX.MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.stabilizer = stabilizer
        
        self.ui.actionQuit.triggered.connect(stabilizer.quit)
        self.ui.logView.setModel(stabilizer.event_log)
        self.ui.enableInputCheckbox.toggled.connect(self.start_or_stop_listening)
        self.ui.enableOutputCheckbox.toggled.connect(self.start_or_stop_sending)
        checkbox_variable_pairings = [
            (self.ui.calculateConvergenceCheckbox, self.stabilizer.enable_calculate_convergence),
            (self.ui.logIncomingMessagesCheckbox, self.stabilizer.enable_log_incoming_messages),
            (self.ui.logOutgoingMessagesCheckbox, self.stabilizer.enable_log_outgoing_messages)
            ]
        for checkbox, var in checkbox_variable_pairings:
            checkbox.setChecked(var)
            checkbox.toggled.connect(lambda x: assign(var,x))

        self.update_timer = QTimer(self)
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()

        self.show()

    def update(self):
        '''Refresh gui based on self.stabilizer'''
        self.ui.worldStateText.setPlainText(pformat(self.stabilizer.world_state))
        self.ui.convergedStateText.setPlainText(pformat(self.stabilizer.converged_state))
        self.ui.instrumentsText.setPlainText(pformat(self.stabilizer.instruments))
        self.ui.connectionsText.setPlainText(self.get_pretty_connections())

    def start_or_stop_listening(self, start_listening=None):
        if start_listening==None:
            start_listening = not self.stabilizer.is_listening

        if start_listening:
            self.stabilizer.start_listening()
        else:
            self.stabilizer.stop_listening()

    def start_or_stop_sending(self, whether_to_start_sending):
        if whether_to_start_sending:
            self.stabilizer.start_sending()
        else:
            self.stabilizer.stop_sending()

    def get_pretty_connections(self):
        names = [name for name in self.stabilizer.instruments]
        if not names:
            return 'No instruments'
        names.sort()
        c = self.stabilizer.connections
        data = [[c.setdefault(ni, {}).get(nj,'') for ni in names] for nj in names]
        for i,row in enumerate(data):
            row.insert(0, names[i])
        header_row = ['']+names
        data.insert(0, header_row)

        table = Texttable()
        table.set_cols_align(['r']*(len(names)+1))
        table.add_rows(data)
        return table.draw() + '\nRaw data:\n'+pformat(c)


