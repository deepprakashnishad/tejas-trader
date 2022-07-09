import os
import time
import webbrowser
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from kiteconnect import KiteConnect
from brokers.zerodha_broker import ZerodhaBroker
from model import User
from utils import my_constants as mconst
import browserhistory
import urllib.parse as urlparse


def wait_for_request(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('localhost', 8081)
    httpd = server_class(server_address, handler_class)
    print(httpd)
    return httpd.handle_request()


def save_user(data):
    user = User.query.filter(User.user_id == data['user_id']).first()
    if user is not None:
        user.remove()

    if data['avatar_url'] is None:
        avatar_url = ""
    else:
        avatar_url = data['avatar_url']
    User(
        user_id=data['user_id'],
        user_name=data['user_name'],
        user_shortname=data['user_shortname'],
        broker=data['broker'],
        email=data['email'],
        user_type=data['user_type'],
        exchanges=data['exchanges'],
        products=data['products'],
        access_token=data['access_token'],
        public_token=data['public_token'],
        login_time=data['login_time'],
        avatar_url=avatar_url,
        access_token_expiry=data['login_time'] + timedelta(hours=12)
    ).save()


class Authenticate(ZerodhaBroker):

    def __init__(self, uid):
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
        # print(browser_list['firefox'][1][0])
        # request_token_url = browser_list['firefox'][1][0]
        # request_token = urlparse.parse_qs(urlparse.urlparse(request_token_url).query)['request_token'][0]
        # return request_token

    def get_access_token(self):
        request_token = self.login()
        request_token = input("[*] Enter your request token: ")
        data = self.kite.generate_session(request_token, api_secret=mconst.API_SECRET)
        save_user(data)
        access_token = data["access_token"]
        self.kite.set_access_token(access_token)
        mconst.ACCESS_TOKEN = access_token
        print(f"Your Access Token: {access_token}")
        return access_token
