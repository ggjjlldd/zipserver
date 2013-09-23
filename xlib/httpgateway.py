#coding:utf8
# Author: zJay
# Created: 05/27/2011

import traceback
import urlparse
import urllib2
from inspect import ismethod

class WSGIGateway:
    RET_API_NOTFOUND = ("400 Bad Request", [("GateWayError", "API Not Found")], "")
    RET_API_ERR = ("500 Internal Server Error", [("GateWayError", "API Processing Error")], "")
    
    def __init__(self, funcname_getter, gwlogger, protocols):
        self._protocols = protocols
        self._apiname_getter = funcname_getter
        self._gwlogger = gwlogger
        
    def _log(self, ip, logline):
        if self._gwlogger:
            self._gwlogger.log("%s %s" % (ip, logline))

    def process(self, wsgienv):
        """
        @return HTTP_STATUS(str), HEADERS([(k,v),..]), ContentGenerator
        """
        try:
            ip = wsgienv.get("HTTP_SRC_ADDR") or wsgienv.get("REMOTE_ADDR")
            assert ip
            funcname = self._apiname_getter(wsgienv)
            protocol = self._protocols.get(funcname)
            if not protocol:
                self._log(ip, "Protocol obj not found\nfuncname:%s" % funcname)
                return self.RET_API_NOTFOUND
        except:
            self._log(ip, traceback.format_exc())
            return self.RET_API_NOTFOUND
        
        try:
            httpstatus, headers, content = protocol(ip, wsgienv)
            return httpstatus, headers, content
        except:
            self._log(ip, traceback.format_exc())
            return self.RET_API_ERR

def httpget2dict(qs):
    if not qs:
        return {}
    else:
        queries = urlparse.parse_qs(qs)
        ret = {}
        for k, v in queries.items():
            if len(v) == 1:
                ret[k] = v[0]
            else:
                ret[k] = v
        return ret

def check_param(func, params):
    if ismethod(func):
        if len(params) != func.func_code.co_argcount - 1:
            return False
    else:
        if len(params) != func.func_code.co_argcount:
            return False
        
    for param_name in params:
        if param_name not in func.func_code.co_varnames:
            return False
    return True

def get_uri_tail_sec(uri):
    if uri.endswith("/"):
        i = uri.rfind("/", 0, -1)
        sec = uri[i + 1: -1].encode("ascii")
    else:
        i = uri.rfind("/")
        sec = uri[i + 1:].encode("ascii")
    return sec

def get_uri_head_sec(uri):
    if not uri:
        return ""
    i = 1 if uri[0] == "/" else 0
    
    j = uri.find("/", i)
    if j < 0:
        j = len(uri)
    return uri[i: j].encode("ascii")

def get_cookie_param(s):
    r = {}
    if not s:
        return r
    for item in s.split(";"):
        item = item.strip(" ")
        kv = item.split("=")
        if len(kv) == 2:
            r[kv[0].strip(" ")] = kv[1].strip(" ")
    return r

def read_wsgi_post(wsgienv):
    post_len = wsgienv.get("CONTENT_LENGTH")
    post_len = int(post_len) if post_len else 0
    if post_len:
        return wsgienv["wsgi.input"].read(post_len)
    else:
        return ""

def parse_multipart_raw(s):
    ret = {}
    lines = s.split("\n")
    for i in range(0, 4 * (len(lines) / 4), 4):
        infoline = lines[i + 1]
        
        infoline_lower = infoline.lower()
        if "content-disposition:" not in infoline_lower or \
           "form-data" not in infoline_lower or \
           "name=\"" not in infoline_lower:
            continue
        
        start = infoline.find("name=\"")
        end = infoline.find("\"", start + 6)
        if start < 0 or end < 0:
            continue
        name = infoline[start + 6: end]
        
        value = lines[i + 3].strip("\r\n ")
        if value:
            ret[name] = value
    return ret
