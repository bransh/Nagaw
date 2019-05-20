import os
import ConfigParser
import logging
from shutil import copyfile

class InvalidTemplate(Exception):
    """ Exception class to raise in case of a invalid template """

    def __init__(self):
        Exception.__init__(self, "The given template is either invalid or not available locally!")

class FormTemplate():
    """ This class represents phishing templates """

    def __init__(self, name, template_dir_path, html_dir, static_dir, config_file):
        # Read the template's configuration file
        config = ConfigParser.ConfigParser()
        config_file_path = os.path.join(template_dir_path, config_file)
        config.read(config_file_path)

        self.name = name
        self.display_name = config.get('info', 'name')
        self.description = config.get('info', 'description')
        self.html_dir_path = os.path.join(template_dir_path, html_dir, '')
        self.static_dir_path = os.path.join(template_dir_path, html_dir, static_dir, '')

    def __str__(self):
        """Return a string representation of the template."""
        return self.display_name + "\n\t" + self.description + "\n"


class TemplateManager():
    """This class handles all the template management operations"""

    def __init__(self, template_root):
        self.html_dir = 'html'
        self.static_dir = 'static'
        self.config_file = 'config.ini'
        self.template_root = template_root
        template_list = os.listdir(self.template_root)

        # Load templates
        self.templates = {}
        for template_name in template_list:
            template_dir_path = os.path.join(self.template_root, template_name)
            if os.path.isdir(template_dir_path) and self.is_valid_template(template_name):
                try:
                    self.templates[template_name] = FormTemplate(template_name,
                                                                 template_dir_path, 
                                                                 self.html_dir,
                                                                 self.static_dir,
                                                                 self.config_file)
                except:
                    logging.debug('[D] Template "%s" is not valid and cannot be created.' % template_name)


    def is_valid_template(self, name):
        """Validate the template"""

        html = False
        template_dir_path = os.path.join(self.template_root, name)
        
        # 1) check config file...
        if not self.config_file in os.listdir(template_dir_path):
            return False, "Configuration file not found."
        
        # 2) check html dir
        try:
            html_path = os.listdir(os.path.join(template_dir_path, self.html_dir))
        except OSError:
            return False, "No " + self.html_dir + " directory found."
        
        # 3) Check HTML files...
        for tfile in html_path:
            if tfile.endswith(".html"):
                html = True
                break
        if not html:
            return False, "No HTML files found."

        return True
