#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# pylint: skip-file

import os

#
# GENERAL CONFIGURATION
#
current_dir = os.path.dirname(os.path.abspath(__file__))
path_to_project_root = os.path.abspath(current_dir + '/../') + '/'
dir_of_data = os.path.abspath(path_to_project_root + '/data/') + '/'
phishing_pages_dir = os.path.abspath(dir_of_data + '/phishing-pages/') + '/'
SCENARIO_HTML_DIR = "html/"
LOGOS_DIR = dir_of_data + "logos/"
MAC_PREFIX_FILE = dir_of_data + "mac-prefixes"
URL_TO_OS_FILE = dir_of_data + "os-initial-requests"
KNOWN_WLANS_FILE = dir_of_data + "known-open-wlans"
DN = open(os.devnull, 'w')

#
# DNS / DHCP Configuration
#
DNS_CONF_PATH = '/tmp/dnsmasq.conf'
DHCP_LEASE_FILE = '/var/lib/misc/dnsmasq.leases'
NETWORK_IP = "10.0.0.0"
NETWORK_MASK = "255.255.255.0"
NETWORK_GW_IP = "10.0.0.1"
DHCP_LEASE = "10.0.0.2,10.0.0.100,12h"
PUBLIC_DNS = "8.8.8.8"

#
# WEB SERVER Configuration
#
WEB_SERVER_LOG_FILE_PATH = '/tmp/wifiphisher-webserver.tmp'
VALID_POST_CONTENT_TYPE = 'application/json' #"application/x-www-form-urlencoded"
WEB_SERVER_CREDS_LOG_FILE_PATH = 'credentials.log'
PORT = 80
SSL_PORT = 443
PEM = dir_of_data + 'cert/server.pem'
LOGIN_URL = 'login'
LOGIN_PARAMETERS = ['username', 'password']
#
# Logging configurations
#
LOG_FILEPATH = '_nagaw.log'
