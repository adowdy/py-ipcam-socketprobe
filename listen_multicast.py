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

HOST_IP = "192.168.0.121"

# Create a UDP socket
sock_mcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Allow multiple sockets to use the same PORT number
sock_mcast.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

# Bind to the port that we know will receive multicast data
sock_mcast.bind((ANY,MCAST_PORT))

# Tell the kernel that we want to add ourselves to a multicast group
# The address for the multicast group is the third param
status = sock_mcast.setsockopt(socket.IPPROTO_IP,
socket.IP_ADD_MEMBERSHIP,
socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY))

# setblocking(0) is equiv to settimeout(0.0) which means we poll the socket.
# But this will raise an error if recv() or send() can't immediately find or send data. 
sock_mcast.setblocking(0.1)



print "begin loop!"
firsttime = False
print firsttime
while 1:
    if firsttime == True:
            print "first time, sending request"
            firsttime = False
            # TRY SENDING STUFF WE NEED
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(HOST_IP))
            # allow multiple sockets to use same port number?
            sock2.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            sock2.bind((HOST_IP, 3702))
            packetdata = open('discovery-probe.xml', "r").read()
            sock2.sendto(packetdata, (MCAST_ADDR, MCAST_PORT))
    try:
        data, addr = sock_mcast.recvfrom(4096)
    except socket.error as e:
        # show error messages?
        # print e
        pass
    else:
        print "From: ", addr
        print "Data: ", data
        # check data for IP addr, continue with getting RTSP URL
        identifierIPAddr = data.find('<wsdd:XAddrs>')
        if identifierIPAddr != -1:
            urlstring = find_between(data, 'XAddrs>', '</')
           
            if urlstring != "":
                print "\nURL:\n" + urlstring
                destIP = find_between(urlstring, '//', ':')
                print "IP: " + destIP
                destPort = find_between(urlstring, (destIP+":"), "/")
                print "PORT: " + destPort
                intDestPort = int(destPort)
                print intDestPort

                # try to reconfigure socket for listening to response to soap?
                sock_mcast.bind((socket.gethostname, 3702))

                # attempt to pass soap message for media data
                profilespacketdata = open('get-profiles.xml', "r").read()

                sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sockSend.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(HOST_IP))
                sockSend.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                #sockSend.bind(('', 80))
                sockSend.sendto(profilespacketdata, (destIP, destPort))
                print "Sending : " + profilespacketdata + "\n data sent to\n" + destIP + ":" + destPort
                
