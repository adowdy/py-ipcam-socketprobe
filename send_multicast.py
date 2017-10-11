import socket

# 224.0.0.1 is the all-hosts group. If you ping that group, all multicast capable hosts on the network should answer, 
# as every multicast capable host must join that group at start-up on all it's multicast capable interfaces.
MCAST_GRP = '224.0.0.1'
#MCAST_GRP = '239.255.255.250'
MCAST_PORT = 3702
HOST_IP = "192.168.0.121"

# TTL (time to live)
# http://www.tldp.org/HOWTO/Multicast-HOWTO-2.html
#    0 Restricted to the same host. Won't be output by any interface.
#    1 Restricted to the same subnet. Won't be forwarded by a router.
#  <32 Restricted to the same site, organization or department.
#  <64 Restricted to the same region.
# <128 Restricted to the same continent.
# <255 Unrestricted in scope. Global.

# THIS SENDS FROM DEFAULT INTERFACE (10.50.x.x)
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 33)

# SEND FROM HOST_IP ON SUBNET
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(HOST_IP))


# allow multiple sockets to use same port number?
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(("", 3702))


packetdata = open('discovery-probe.xml', "r").read()
sock.sendto(packetdata, (MCAST_GRP, MCAST_PORT))
print "SENT PACKET:\n\n" + packetdata