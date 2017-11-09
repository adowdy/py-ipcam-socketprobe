#!/bin/bash  
curl http://192.168.0.123/onvif/device_service -d @set-network-interface.xml
# try <tt:Mtu>1500</tt:Mtu>


# likely system reboot needed, tell it its ok to boot
#curl http://192.168.0.123/onvif/device_service -d @system-reboot.xml

# just test a response
#curl http://192.168.0.200/onvif/device_service -d @../get-profiles.xml