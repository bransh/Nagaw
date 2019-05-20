import ConfigParser
import os

class ConfigurationManager():
    # Instance will be stored here.
    __instance = None

    @staticmethod
    def get_instance():
        """Return the instance of the class or create new if none exists."""
        if ConfigurationManager.__instance is None:
            ConfigurationManager()
        return ConfigurationManager.__instance

    def __init__(self):
        """Initialize the class."""
        if ConfigurationManager.__instance:
            raise Exception("Error: ConfigurationManager class is a singleton!")
        else:
            ConfigurationManager.__instance = self
            self.config_file = None

    def load_config(self, config_file):
        # Reading config.ini file
        self.config_file = config_file
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(current_dir + '/../') + '/'
        self.dev_null = open(os.devnull, 'w')
        self.target_iface = None
        self.internet_iface = None
        self.target_template_name = None

        # GENERAL = self.config['GENERAL']
        self.template_dir = os.path.abspath(self.project_root + '/' + self.config.get('GENERAL', 'HTML_TEMPLATE_PAGES_REL_PATH'))
        self.mac_prefix_file = os.path.abspath(self.project_root + '/' + self.config.get('GENERAL', 'MAC_PREFIX_REL_PATH'))
        self.url_to_os_file = os.path.abspath(self.project_root + '/' + self.config.get('GENERAL', 'URL_TO_OS_REL_PATH'))
        self.log_file = self.config.get('GENERAL', 'LOG_REL_PATH')

        # DNS_DHCP = self.config['DNS_DHCP']
        self.dnsmasq_config_file = os.path.abspath(self.project_root + '/' + self.config.get('DNS_DHCP', 'CONFIG_REL_PATH'))
        self.dnsmasq_log_file = os.path.abspath(self.project_root + '/' + self.config.get('DNS_DHCP', 'LOG_REL_PATH'))
        self.dhcp_lease_file = os.path.abspath(self.project_root + '/' + self.config.get('DNS_DHCP', 'DHCP_LEASE_REL_PATH'))
        self.network_ip = self.config.get('DNS_DHCP', 'NETWORK_IP')
        self.network_mask = self.config.get('DNS_DHCP', 'NETWORK_MASK')
        self.network_gw_ip = self.config.get('DNS_DHCP', 'NETWORK_GW_IP')
        self.dhcp_lease = self.config.get('DNS_DHCP', 'DHCP_LEASE')
        self.public_dns = self.config.get('DNS_DHCP', 'PUBLIC_DNS')

        # WEB_SERVER = self.config['WEB_SERVER']
        self.webserver_log_file = os.path.abspath(self.project_root + '/' + self.config.get('WEB_SERVER', 'LOG_REL_PATH'))
        self.credentials_log_file = os.path.abspath(self.project_root + '/' + self.config.get('WEB_SERVER', 'CREDS_REL_PATH'))
        self.certificates_file = os.path.abspath(self.project_root + '/' + self.config.get('WEB_SERVER', 'PEM_REL_PATH'))
        self.content_type = self.config.get('WEB_SERVER', 'VALID_POST_CONTENT_TYPE')
        self.http_port = self.config.get('WEB_SERVER', 'HTTP_PORT')
        self.https_port = self.config.get('WEB_SERVER', 'HTTPS_PORT')
        self.login_url = self.config.get('WEB_SERVER', 'LOGIN_URL')
        self.login_parameters = [param.strip() for param in self.config.get('WEB_SERVER', 'LOGIN_PARAMETERS').split(',')]
