#!/usr/bin/env python

import sys
import socket # only for the exception type
from txosc import osc
from txosc import sync

if __name__ == "__main__":
    try:
        udp_sender = sync.UdpSender("localhost", int(sys.argv[1]))
    except socket.error, e:
        print(str(e))
    else:
    	for i in range(int(sys.argv[2])) :
        	udp_sender.send(osc.Message("/hello", 2, "bar", 3.14159))        	
        udp_sender.close()
        print("Successfully sent the messages.")