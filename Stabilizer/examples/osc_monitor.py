#!/usr/bin/env python
"""
OSC monitor example using txosc
"""
import sys
from twisted.internet import reactor
from txosc import osc
from txosc import dispatch
from txosc import async

def foo_handler(message, address):
    """
    Function handler for /foo
    """
    print("foo_handler")
    print("  Got %s from %s" % (message, address))

class UDPReceiverApplication(object):
    """
    Example that receives UDP OSC messages.
    """
    def __init__(self, port):
        self.port = port
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        print("Listening on osc.udp://localhost:%s" % (self.port))        
        # fallback:
        self.receiver.fallback = self.fallback
        
    def fallback(self, message, address):
        print("%s: %s" % (address, message))

if __name__ == "__main__":
    app = UDPReceiverApplication(sys.argv[1])
    reactor.run()