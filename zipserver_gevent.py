#coding:utf8
# Author: zJay
# Created: 10/19/2011

# ------------------
# Gevent Patch
from gevent import monkey
monkey.patch_all()

import config
import logger


# ------------------

import sys
import traceback

from gevent import pywsgi
from xlib import util

import wsgiapp

def application(environ, start_response):
    return wsgiapp.application(environ, start_response)

def run_server(listen_addr, spawn):
    server = pywsgi.WSGIServer(listen_addr, application, log=None, spawn=spawn)
    server.serve_forever()

if __name__ == '__main__':
    try:
        addr, port, spawn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    except:
        traceback.print_exc()
        exit(-1)

    run_server((addr, port), spawn)
