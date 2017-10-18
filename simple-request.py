import requests

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# assume URL given in probe for now
url="http://192.168.0.123:80/onvif/device_service"

#headers = {'content-type': 'application/soap+xml'}
headers = {'content-type': 'text/xml'}

body = open('get-profiles.xml', "r").read()

response = requests.post(url,data=body,headers=headers)
#print "response: " + response.content

# FISH OUT MEDIA PROFILE NAMES
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
  tokenIndex = profStr.find('token="', index, len(profStr))
  if tokenIndex != -1:
    tokenIndex += 7
    finishTokenIndex = profStr.find('"', tokenIndex, len(profStr))
    profileName = profStr[tokenIndex:finishTokenIndex]
    print "profile: " + profileName
    mediaProfileList.append(profileName)
  else:
      print "didn't find token for this profile! SKIP"

  # move index forward when done
  index += len(mediaProfileKey)

# URI REQUEST FOR EACH MEDIA PROFILE NAMED
baseUriRequest = open('get-stream-uri.xml', "r").read()

# now with all profile names, send request for each one to get rtsp url list
for mProfileName in mediaProfileList:
  getProfileUriReq = baseUriRequest.replace("StreamTokenName", mProfileName)
  uriResponse = requests.post(url,data=getProfileUriReq,headers=headers)
  # with response, get rtsp URL
  rtspUrl = find_between(uriResponse.content, '<tt:Uri>', '</tt:Uri>')
  #print uriResponse.content
  print rtspUrl
