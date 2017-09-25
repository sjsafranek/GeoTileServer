#!/usr/bin/python3

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornadouvloop import TornadoUvloop
from router import router
import config

define("port", default=str(config.PORT), help="Server port")

if __name__ == "__main__":
    options.parse_command_line()
    app = router()
    app.listen(options.port)
    print("Magic happens on http://localhost:"+options.port)
    IOLoop.configure(TornadoUvloop)
    IOLoop.current().start()

