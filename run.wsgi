#!/home/shop/myenv/bin/python3

# -*- coding: UTF-8 -*-
import sys, os

# Add a custom Python path.
sys.path.insert(0, "/home/shop/projects/shop")
sys.path.insert(0, '/home/shop/myenv/lib/python3.4/site-packages')
os.chdir("/home/shop/projects/shop")

from flup.server.fcgi import WSGIServer
from app import app as application

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = ''
       return self.app(environ, start_response)

application = ScriptNameStripper(application)

if __name__ == '__main__':
    WSGIServer(application).run()