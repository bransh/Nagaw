import logging
from common.constants import (NETWORK_GW_IP, SSL_PORT, PORT, DN)
from subprocess import (PIPE, Popen)

class Fw():
    """Handles all iptables operations."""

    @staticmethod
    def execute_commands(commands):
        # type: (List[str]) -> None
        """Execute each command and log any errors."""
        for command in commands:
            _, error = Popen(command.split(), stderr=PIPE, stdout=DN).communicate()
            if error:
                logger.error(
                    "{command} has failed with the following error:\n{error}".
                    format(command=command, error=error))

    @staticmethod
    def nat(in_iface, ext_iface):
        cmd1 = 'iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format(ext_iface)
        cmd2 = 'iptables -A FORWARD -i {} -o {} -j ACCEPT'.format(in_iface, ext_iface)
        logging.debug('[D] Executing the following commands: ')
        logging.debug('    %s' % cmd1)
        logging.debug('    %s' % cmd2)
        Fw.execute_commands(
            [cmd1, cmd2]
        )

    @staticmethod
    def clear_rules():
        cmd1 = 'iptables -F'
        cmd2 = 'iptables -X'
        cmd3 = 'iptables -t nat -F'
        cmd4 = 'iptables -t nat -X'

        logging.debug('[D] Executing the following commands: ')
        logging.debug('    %s' % cmd1)
        logging.debug('    %s' % cmd2)
        logging.debug('    %s' % cmd3)
        logging.debug('    %s' % cmd4)

        Fw.execute_commands(
            [cmd1, cmd2, cmd3, cmd4]
        )

    @staticmethod
    def redirect_http_to_localhost():
        """Redirect HTTP, HTTPS & DNS requests to localhost.
        Redirect the following requests to localhost:
            * HTTP (Port 80)
            * HTTPS (Port 443)
            * DNS (Port 53)
        """
        cmd1 = 'iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination {}:{}'.format(NETWORK_GW_IP, PORT)
        cmd2 = 'iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination {}:{}'.format(NETWORK_GW_IP, SSL_PORT)
        cmd3 = 'iptables -t nat -A PREROUTING -p tcp --dport 53 -j DNAT --to-destination {}:{}'.format(NETWORK_GW_IP, 53)
        cmd4 = 'iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT --to-destination {}:{}'.format(NETWORK_GW_IP, 53)

        logging.debug('[D] Executing the following commands: ')
        logging.debug('    %s' % cmd1)
        logging.debug('    %s' % cmd2)
        logging.debug('    %s' % cmd3)
        logging.debug('    %s' % cmd4)

        Fw.execute_commands(
            [cmd1, cmd2, cmd3, cmd4]
        )
    
    @staticmethod
    def do_not_redirect_host(ip):
        # iptables -t nat -I PREROUTING 1 -p tcp -s CLIENT -j ACCEPT
        # iptables -t nat -A PREROUTING 1 -p tcp -s CLIENT -j ACCEPT > allows a client to reach Inet
        cmd = 'iptables -t nat -I PREROUTING 1 -p tcp -s {} -j ACCEPT'.format(ip)
        logging.debug('[D] Executing the following command: ')
        logging.debug('    %s' % cmd)

        Fw.execute_commands(
            [cmd]
        )

    @staticmethod
    def set_ip_fwd():
        cmd = 'sysctl -w net.ipv4.ip_forward=1'
        logging.debug('[D] Executing the following command: ')
        logging.debug('    %s' % cmd)

        Fw.execute_commands(
            [cmd]
        )

    @staticmethod
    def set_route_localnet():
        cmd = 'sysctl -w net.ipv4.conf.all.route_localnet=1'
        logging.debug('[D] Executing the following command: ')
        logging.debug('    %s' % cmd)

        Fw.execute_commands(
            [cmd]
        )

    @staticmethod
    def on_exit():
        Fw.clear_rules()
