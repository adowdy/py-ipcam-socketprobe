# probe_for_streams.py
# full example of sending ONVIF probe out on network, and retrieving RTSP url from media profiles for camera streaming

import socket, requests
# had to pip install requests

# DEFINES
headers = {'content-type': 'text/xml'}
# headers = {'content-type': 'application/soap+xml'}

# GET ONVIF URL/URI FOR SOAP TO BEGIN
myOnvifUri="http://192.168.0.123:80/onvif/device_service"

# handy string function for grabbing substrings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# FISH OUT MEDIA PROFILE NAMES
def getMediaProfiles(onvifUri):
  # ONVIF has standard way of getting media profiles via SOAP message
  body = open('get-profiles.xml', "r").read()
  response = requests.post(onvifUri,data=body,headers=headers)
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
def getRtspUri(onvifUri, mediaProfile):
  baseUriRequest = open('get-stream-uri.xml', "r").read()
  rtspUris = []
  # now with all profile names, send request for each one to get rtsp url list
  getProfileUriReq = baseUriRequest.replace("StreamTokenName", mediaProfile)
  uriResponse = requests.post(onvifUri,data=getProfileUriReq,headers=headers)
  # with response, get rtsp URL
  rtspUri = find_between(uriResponse.content, '<tt:Uri>', '</tt:Uri>')
  #rtspUris.append(rtspUri)
  return rtspUri

### PROGRAM EXECUTION BEGINS HERE ###
myMediaProfileNameList = getMediaProfiles(myOnvifUri)
mediaProfiles = []

for mediaProfile in myMediaProfileNameList:
  rtspUri = getRtspUri(myOnvifUri,mediaProfile)
  #print mediaProfile + "\n" + rtspUri
  mediaProfile = { 'name' : mediaProfile, 'rtsp' : rtspUri }
  mediaProfiles.append(mediaProfile)
  print mediaProfile['name']
  print mediaProfile['rtsp']

# data structure holds objects with 2 elements: the media profile name, and the rtsp uri
#print mediaProfiles
