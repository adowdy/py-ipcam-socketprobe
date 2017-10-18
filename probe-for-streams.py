#!/usr/bin/python3

# probe_for_streams.py
# full example of sending ONVIF probe out on network, 
# and retrieving RTSP url from media profiles for camera streaming

import socket, requests, sys, fcntl, struct
# had to pip install requests
# todo -- figure out how to build my own soap header so we don't need requests??

# DEFINES

ANY_ADDR = "0.0.0.0" 

# group specific to onvif?
MCAST_ADDR = "239.255.255.250"

# all hosts group
# MCAST_ADDR = '224.0.0.1'

MCAST_PORT = 3702

HEADERS = {'content-type': 'text/xml'}
# headers = {'content-type': 'application/soap+xml'}


### FUNCTIONS ###

# get IP from network interface without special packages
def get_ip_address(ifname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

# handy string function for grabbing substrings
def find_between( s, first, last ):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

# FISH OUT MEDIA PROFILE NAMES
def getMediaProfiles(onvifUri):
    # ONVIF has standard way of getting media profiles via SOAP message
    body = open('get-profiles.xml', "r").read()
    response = requests.post(onvifUri, data=body, headers=HEADERS)
    profStr = response.content
    # at each instance of <trt:Profiles ... search for next 'token='
    mediaProfileList = []
    mediaProfileKey = '<trt:Profiles'
    index = 0
    while index < len(profStr):
        index = profStr.find(mediaProfileKey, index, len(profStr))
        if index == -1:
          break
        # get media profile name based on index, put in list
        tokenKey = 'token="'
        tokenIndex = profStr.find(tokenKey, index, len(profStr))
        if tokenIndex != -1:
          tokenIndex += len(tokenKey)
          finishTokenIndex = profStr.find('"', tokenIndex, len(profStr))
          profileName = profStr[tokenIndex:finishTokenIndex]
          mediaProfileList.append(profileName)
        else:
            print "didn't find token for this profile! SKIP"

        # move index forward when done
        index += len(mediaProfileKey)
    return mediaProfileList


  # URI REQUEST FOR EACH MEDIA PROFILE NAMED
def getRtspUri(onvifUri, profileName):
    baseUriRequest = open('get-stream-uri.xml', "r").read()
    rtspUris = []
    # now with all profile names, send request for each one to get rtsp url list
    getProfileUriReq = baseUriRequest.replace("StreamTokenName", profileName)
    uriResponse = requests.post(onvifUri,data=getProfileUriReq,headers=HEADERS)
    # with response, get rtsp URL
    rtspUri = find_between(uriResponse.content, '<tt:Uri>', '</tt:Uri>')
    #rtspUris.append(rtspUri)
    return rtspUri

def createMulticastListenerSocket():
    # Create a UDP socket for multicast listen
    sockMcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Allow multiple sockets to use the same PORT number
    sockMcast.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # Bind to the port that we know will receive multicast data
    sockMcast.bind((ANY_ADDR,MCAST_PORT))

    # Tell the kernel that we want to add ourselves to a multicast group
    # The address for the multicast group is the third param
    status = sockMcast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY_ADDR))

    # setblocking(0) is equiv to settimeout(0.0) which means we poll the socket.
    # But this will raise an error if recv() or send() can't immediately find or send data. 
    sockMcast.setblocking(0.1)

    return sockMcast

def sendProbe():
    print "Sending probe to MCAST " + MCAST_ADDR + " " + str(MCAST_PORT)
    # TRY SENDING STUFF WE NEED
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    send_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(hostIP))
    # allow multiple sockets to use same port number?
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    send_sock.bind((ANY_ADDR, 3702))
    packetdata = open('discovery-probe.xml', "r").read()
    send_sock.sendto(packetdata, (MCAST_ADDR, MCAST_PORT))
    send_sock.close()
    print "Sent Probe Packet"







### *** MAIN PROGRAM EXECUTION BEGINS HERE *** ###

# get arg so we know which net interface to send on
arg_list = sys.argv

if len(sys.argv) < 2:
    print "give network interface name as argument!";
    print  "EXAMPLE: python scriptname.py eth0"; exit()

hostInterface = arg_list[1]
hostIP = get_ip_address(hostInterface)
print "Probe data will be sent from my IP at: " + hostIP

socketMultiListener = createMulticastListenerSocket()

running = 1

# send probe out on network
sendProbe()

while running:
    try:
        data, addr = socketMultiListener.recvfrom(4096)

    except socket.error as e:
        # show error messages?
        # print e
        pass

    else:
        # print "From: ", addr
        # print "Data: ", data
        # check data for IP addr, continue with getting RTSP URL
        print "Got multicast response!"
        identifierIPAddr = data.find('<wsdd:XAddrs>')
        if identifierIPAddr != -1:
            onvifUri = find_between(data, 'XAddrs>', '</')
           
            if onvifUri != "":
                print "ONVIF URI:\n" + onvifUri
                # if i need to do URI parsing later, use import urlparse ?
                #destIP = find_between(onvifUri, '//', ':')

                # get the names of all media profiles
                myMediaProfileNameList = getMediaProfiles(onvifUri)
                mediaProfiles = []

                # query each media profile to get its stream URI
                for mediaProfile in myMediaProfileNameList:
                    rtspUri = getRtspUri(onvifUri,mediaProfile)
                    #print mediaProfile + "\n" + rtspUri
                    mediaProfile = { 'name' : mediaProfile, 'rtsp' : rtspUri }
                    mediaProfiles.append(mediaProfile)
                    print mediaProfile['name']
                    print mediaProfile['rtsp']

                    # FROM HERE, if wanted to do anything with the URIs, there is handy urlparse package
                    # for instance, get individual url pieces and reorder them, like username,pass which can feed to other stuff
                    socketMultiListener.close()
                    running = 0 # stop, we're done!

                # data structure holds objects with 2 elements: the media profile name, and the rtsp uri
                #print mediaProfiles