#!/usr/bin/python3
import os
import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options

try:
    from tornadouvloop import TornadoUvloop
except ImportError:
    pass

if not os.path.exists('config.py'):
    contents = """#!/usr/bin/python3
import multiprocessing

PORT = 8080
CACHE_DIR = 'cache'
MAX_WORKERS = multiprocessing.cpu_count()
LAYER_DIR = 'examples'
# LAYER_DIR = 'data'
STYLESHEET = 'stylesheet.xml'"""
    with open('config.py', 'w') as fileHandler:
        fileHandler.write(contents)

import config
from router import router

define("port", default=str(config.PORT), help="Server port")

if __name__ == "__main__":
    options.parse_command_line()
    app = router()
    app.listen(options.port)
    print("Magic happens on http://localhost:"+options.port)
    try:
        IOLoop.configure(TornadoUvloop)
    except NameError:
        pass
    IOLoop.current().start()
