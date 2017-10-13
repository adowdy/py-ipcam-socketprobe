# Multicast client
# Adapted from: http://chaos.weblogs.us/archives/164

import socket
from xml.etree.ElementTree import Element

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

ANY = "0.0.0.0" 
# all hosts group
MCAST_ADDR = '224.0.0.1' 
#MCAST_ADDR = "239.255.255.250"
MCAST_PORT = 3702

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Allow multiple sockets to use the same PORT number
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

# Bind to the port that we know will receive multicast data
sock.bind((ANY,MCAST_PORT))

# Tell the kernel that we want to add ourselves to a multicast group
# The address for the multicast group is the third param
status = sock.setsockopt(socket.IPPROTO_IP,
socket.IP_ADD_MEMBERSHIP,
socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY))

# setblocking(0) is equiv to settimeout(0.0) which means we poll the socket.
# But this will raise an error if recv() or send() can't immediately find or send data. 
sock.setblocking(0.1)

print "begin loop!"

while 1:
    try:
        data, addr = sock.recvfrom(4096)
    except socket.error as e:
        pass
    else:
        print "From: ", addr
        print "Data: ", data
        # check data for IP addr, continue with getting RTSP URL
        identifierIPAddr = data.find('<wsdd:XAddrs>')
        if identifierIPAddr != -1:
            print identifierIPAddr
            urlstring = find_between(data, 'XAddrs>', '</')
            print "\nIP:\n" + urlstring

        
       
            
print "end"