'''
This module contains code to hook up the GUI (generated using the Qt UI 
designer) to the rest of the code and any hand-written GUI code.
'''

from UX import mainWindows
from PySide import QtCore, QtGui
from PySide.QtGui import *

class MainWindow(QtGui.QMainWindow):
    def __init__(self, stabilizer, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = mainWindows.Ui_MainWindow()
        self.ui.setupUi(self)
        self.stabilizer = stabilizer
        
        self.ui.listView.setModel(stabilizer.event_log)
        self.ui.pushButton.clicked.connect(self.start_or_stop_listening)
        self.show()

    def start_or_stop_listening(self):
        if self.stabilizer.is_listening:
            self.stabilizer.stop_listening()
            self.ui.pushButton.setText("Start Listening")
        else:
            self.stabilizer.start_listening()
            self.ui.pushButton.setText("Stop Listening")
