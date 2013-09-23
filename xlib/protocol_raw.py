#coding:utf8
# Author: zJay
# Created: 10/10/2011

import httplib
import traceback

from httpgateway import httpget2dict
from httpgateway import get_cookie_param
from httpgateway import get_uri_tail_sec

class Protocol:
    def __init__(self, func, errlog):
        self._func = func
        self._errlog = errlog

    def __call__(self, ip, wsgienv):
        try:
            params_get = httpget2dict(wsgienv.get("QUERY_STRING"))
        except:
            self._errlog.log("Get param exception\n%s %s" % (ip, traceback.format_exc()))
            return "400 Bad Request", [("MSG", "GetParamException")], ()

        try:
            status, headers, content = self._func(ip, wsgienv, params_get)
            status_line = "%s %s" % (status, httplib.responses.get(status, ""))
            return status_line, headers, content
        except:
            self._errlog.log("Server exception\n%s %s" % (ip, traceback.format_exc()))
            return "500 Internal Server Error", [("MSG", "ServerException")], ()
