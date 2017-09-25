#!/usr/bin/python3

from tornado.web import Application
from handlers import *

settings = {
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
}

# router for http server
def router():
    return Application([
        (r"/", MainHandler),
        (r'/tms', ApiRoot),
        (r'/tms/1.0', ApiService),
        (r'/tms/1.0/(?P<layer>[^\/]+)', ApiTileMap),
        (r'/tms/1.0/(?P<layer>[^\/]+)/(?P<z>[^\/]+)/(?P<x>[^\/]+)/(?P<y>[^\/]+)', ApiTile),
        (r'/tms/1.0/(?P<layer>[^\/]+)/(?P<z>[^\/]+)/(?P<x>[^\/]+)/(?P<y>[^\/]+).png', ApiTile),
    ], **settings)
