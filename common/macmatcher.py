class MACMatcher(object):
    """This class handles Organizationally Unique Identifiers (OUIs).
    The original data comes from http://standards.ieee.org/regauth/oui/oui.txt
    See also:: http://standards.ieee.org/faqs/OUI.html"""

    def __init__(self, mac_vendor_file):
        """Setup the class with all the given arguments"""
        self._mac_to_vendor = {}
        self._vendor_file = mac_vendor_file
        self._get_vendor_information()

    def _get_vendor_information(self):
        """Read and process all the data in the vendor file"""
        # open the file with all the MAC addresses and vendor information
        with open(self._vendor_file, 'r') as _file:
            # check every line in the file
            for line in _file:
                # skip comment lines
                if not line.startswith("#"):
                    # separate vendor and MAC addresses and add it to the dictionary
                    separated_line = line.rstrip('\n').split('|')
                    mac_identifier = separated_line[0]
                    vendor = separated_line[1]
                    logo = separated_line[2]
                    self._mac_to_vendor[mac_identifier] = vendor

    def get_vendor_name(self, mac_address):
        """Return the matched vendor name for the given MAC address
        or Unknown if no match is found"""
        # Don't bother if there's no MAC
        if mac_address is None:
            return None

        # convert mac address to same format as file
        # ex. 12:34:56:78:90:AB --> 123456
        mac_identifier = mac_address.replace(':', '').upper()[0:6]

        # try to find the vendor and if not found return unknown
        try:
            vendor = self._mac_to_vendor[mac_identifier]
            return vendor
        except KeyError:
            return "Unknown"

    def unbind(self):
        """Unloads mac to vendor mapping from memory and therefore you can
        not use MACMatcher instance once this method is called"""
        del self._mac_to_vendor
