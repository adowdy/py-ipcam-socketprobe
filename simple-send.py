#! /usr/bin/python3

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host ="192.168.0.123"
port =80
s.connect((host,port))

# get-profiles soap doesn't seem to work, but it does respond to discovery probe directly

# responds to probe on port 80 when sent directly. different approach from mcast addr

send_data_probe = open('discovery-probe.xml', "r").read()
s.send(send_data_probe.encode()) 
recv_data = ''
recv_data = s.recv(4096).decode()
print "response: " + (recv_data)

s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

print "trying to get media profiles... "

send_data_profile_req = open('get-profiles.xml', "r").read()
s.send(send_data_profile_req.encode())
recv_data = ''
recv_data = s.recv(4096).decode()
print "response: " + (recv_data)

s.close ()