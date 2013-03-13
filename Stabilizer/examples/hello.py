#!/usr/bin/python
 
# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *

from txosc import osc
from txosc import dispatch
from txosc import async

class Example(QWidget):
    def __init__(self, reactor, parent=None):
        super(Example, self).__init__(parent)
        self.label = None
        self.initUI()
        self.port = 1187
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        print("Listening on osc.udp://localhost:%s" % (self.port))        
        # fallback:
        self.receiver.fallback = self.fallback
        
    def fallback(self, message, address):
    	self.label.append("%s"%message)        
        
    def initUI(self):
        title = QLabel('Messages')

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')

        self.label = QTextEdit('', self)

        grid = QGridLayout()

        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(self.label, 2, 0)

        self.setLayout(grid)

        self.show()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	import qt4reactor
	qt4reactor.install()
	from twisted.internet import reactor


	mainwindow = Example(reactor)
	mainwindow.show()

	reactor.run()
	
	reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
	app.connect(app, SIGNAL("lastWindowClosed()"), reactor.stop)	
	
	sys.exit(app.exec_())