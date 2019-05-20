"""This module was made for DNSMASQ (DNS + DHCP services)."""

import os
import time
import subprocess
from subprocess import check_output
import logging

class Dnsmasq(object):
    """This singleton class handles dnsmasq for DNS & DHCP services"""

    # Instance will be stored here.
    __instance = None

    @staticmethod
    def get_instance():
        """Return the instance of the class or create new if none exists."""
        if Dnsmasq.__instance is None:
            Dnsmasq()
        return Dnsmasq.__instance

    def __init__(self):
        """Initialize the class."""
        if Dnsmasq.__instance:
            raise Exception("Error: DNSMASQ class is a singleton!")
        else:
            Dnsmasq.__instance = self
            self.dns_conf_path = None
            self.dhcp_lease = None
            self.dns_server = None
            self.gw_ip = None
            self.net_mask = None
            self.interface = None
            self.dhcp_lease_file = None
            self.log_file = None
            self.stdout = None
            self.stderr = None
            self.client_dic = {}

    def check_installed(self):
        # catch the exception if dnsmasq is not installed
        try:
            dev_null = open(os.devnull, 'w')
            subprocess.check_call(
                ['dnsmasq', '-v'], 
                stdout=dev_null, 
                stderr=dev_null
            )
        except OSError:
            logging.info('[-] dnsmasq is not installed!')
            return False

        return True

    def start_service(self):
        """Start the dhcp/dns services."""
        config = 'no-resolv\n'
        config += 'interface=' + self.interface + '\n'
        config += 'dhcp-range=' + self.dhcp_lease + '\n'
        config += 'dhcp-leasefile=' + self.dhcp_lease_file + '\n'
        config += 'server=' + self.dns_server + '\n'
        config += 'log-facility=' + self.log_file + '\n'

        #config += 'address=/#/' + self.gw_ip + '\n'
        #/var/lib/misc/dnsmasq.leases

        with open(self.dns_conf_path, 'w') as dhcpconf:
            dhcpconf.write(config)
        
        # first kill Dnsmasq
        try:
            subprocess.Popen(
                ['killall', 'dnsmasq'],
                stdout=self.stdout,
                stderr=self.stderr
            )
            time.sleep(1)
        except Exception as e:
            log.debug('[D] Exception on killing dnsmasq ...')
            log.debug(e)
        
        # catch the exception if dnsmasq is not installed
        try:
            subprocess.Popen(
                ['dnsmasq', '-C', self.dns_conf_path], 
                stdout=subprocess.PIPE, 
                stderr=self.stderr
            )
        except OSError:
            logging.info('[-] dnsmasq is not installed!')
            raise Exception

        # Set interface's MTU parameter
        #subprocess.Popen(
        #    ['ifconfig', str(self.interface), 'mtu', '1400'],
        #    stdout=self.stdout,
        #    stderr=self.stderr
        #)

        # Set interface's IP and Network mask parameters
        subprocess.Popen(
            ['ifconfig', str(self.interface), 'up', self.gw_ip, 'netmask', self.net_mask],
            stdout=self.stdout,
            stderr=self.stderr
        )

        # Give it some time to avoid "SIOCADDRT: Network is unreachable"
        time.sleep(1)

        # Make sure that we have set the network properly.
        proc = subprocess.check_output(
            ['ifconfig', str(self.interface)]
        )

        if self.gw_ip not in proc:
            return False

    def stop_service(self):
        """Clean up the resoures when exits."""
        subprocess.call(
            'pkill dnsmasq', shell=True
        )
        
        if os.path.isfile(self.dhcp_lease_file):
            os.remove(self.dhcp_lease_file)

        if os.path.isfile(self.dns_conf_path):
            os.remove(self.dns_conf_path)
    
        # sleep 2 seconds to wait the process is killed
        time.sleep(2)

    def get_new_clients(self):
        """Returns a list of NEW tuples of (mac, ip) values retrieved from dnsmasq.leases file."""
        if (not os.path.isfile(self.dhcp_lease_file)):
            return []

        mew_clients = []
        with open(self.dhcp_lease_file, "r") as dnsmasq_leases:
            for line in dnsmasq_leases:
                line = line.split()
                if not line:
                    break
                mac = line[1].strip()
                ip = line[2].strip()
                if self.client_dic.get(mac) == None:
                    self.client_dic[mac] = ip
                    mew_clients.append((mac, ip))

        return mew_clients
