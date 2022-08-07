import os
import time
import webbrowser
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from kiteconnect import KiteConnect
from kiteconnect.exceptions import TokenException
from brokers.zerodha_broker import ZerodhaBroker
from models.user import User
from utils import my_constants as mconst
import browserhistory
import urllib.parse as urlparse


def wait_for_request(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('localhost', 8081)
    httpd = server_class(server_address, handler_class)
    print(httpd)
    return httpd.handle_request()


class Authenticate(ZerodhaBroker):

    def __init__(self):
        # super().__init__(uid)
        self.kite = KiteConnect(api_key=mconst.API_KEY)

    def login(self):
        print("[*] Generate request token", self.kite.login_url())

        webbrowser.get("firefox").open(self.kite.login_url())
        handle = wait_for_request()
        # time.sleep(4)
        # os.system("killall -9 'firefox'")
        # time.sleep(4)
        # browser_list = browserhistory.get_browserhistory()
        # print(browser_list)
        # print(browser_list['firefox'][1][0])
        # request_token_url = browser_list['firefox'][1][0]
        # request_token = urlparse.parse_qs(urlparse.urlparse(request_token_url).query)['request_token'][0]
        # print(f"Your Request Token: {request_token}")
        # return request_token

    def get_access_token(self,request_token):
        try:
            data = self.kite.generate_session(request_token, api_secret=mconst.API_SECRET)
            access_token = data["access_token"]
            del data['login_time']
            self.kite.set_access_token(access_token)
            mconst.ACCESS_TOKEN = access_token
            return {"msg": "Login successful.", "status": True, "userdata": data }
        except TokenException:
            return {"msg": "Invalid token. Please login again.", "status": False}
