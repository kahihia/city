from django.conf import settings

import urllib, urllib2, socket
import xml.etree.ElementTree as ET

baseurl = "http://services.ipaddresslabs.com/iplocation/locateip"
class IPAdressLab():
    def __init__(self, ip, apikey=settings.IPADRESSLAB_KEY):
        self.apikey = apikey
        self.info = self.get_info(ip)

    def get_info(self, ip):
        """Same as GetCity and GetCountry, but a baseurl is required.  This is for if you want to use a different server that uses the the php scripts on ipinfodb.com."""
        passdict = {
            "key":self.apikey
        }

        if ip:
            try:
                passdict["ip"] = socket.gethostbyaddr(ip)[2][0]
            except: 
                passdict["ip"] = ip

        urldata = urllib.urlencode(passdict)
        url = baseurl + "?" + urldata
        urlobj = urllib2.urlopen(url)
        data = urlobj.read()
        urlobj.close()

        tree = ET.fromstring(data)
        geolocation_data = tree.find('geolocation_data')
        if geolocation_data:
            return { element.tag: element.text for element in geolocation_data }
        else:
            return None
        

    def set_ip(self, ip):
        self.info = self.get_info(ip)

    def lon_lat(self):
        if self.info:
            return (
                float(self.info["longitude"]),
                float(self.info["latitude"])
            )
        else:
            return (
                -106.666667,
                52.133333
            )

    def lat_lon(self):
        if self.info:
            return (
                float(self.info["latitude"]),
                float(self.info["longitude"])            
            )

        else:
            return (
                52.133333,
                -106.666667
            )
