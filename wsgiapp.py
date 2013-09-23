#coding:utf8
# Author: aeris
# Created: 09/22/2013

from xlib.httpgateway import WSGIGateway
from xlib import protocol_raw
from xlib import protocol_json1
from xlib import retstat

import api_zip_package
import logger

apicube = {
"ping": protocol_json1.Protocol(api_zip_package.ping, retstat.ERR_SERVER_EXCEPTION, 
    retstat.ERR_BAD_PARAMS, None, None, logger.errlog),
"zip_package": protocol_raw.Protocol(api_zip_package.zip_package, logger.errlog),
}
wsgigw = WSGIGateway(protocol_json1.get_func_name, logger.errlog, apicube)

def application(environ, start_response):
    try:
        status, headders, content = wsgigw.process(environ)
        start_response(status, headders)
        return content
    except:
        start_response("500 Internal Server Error", [("GateWayError", "UnknownException")])
        return ()

if __name__ == '__main__':    
    from xlib import logger as _logger
    _logger.set_debug_verbose()
        
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8003
    print "[Debug][Single-Threaded] HTTP listening on 0.0.0.0:%s..." % port
    from wsgiref.simple_server import make_server
    
    httpd = make_server('', port, application)
    httpd.serve_forever()
