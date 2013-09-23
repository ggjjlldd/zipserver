#coding:utf8
# Author: zJay
# Created: 05/27/2011

import time
import traceback
import json

from xlib.httpgateway import check_param
from xlib.httpgateway import httpget2dict

def get_func_name(wsgienv):
    path = wsgienv.get("PATH_INFO", "")
    if path.endswith("/"):
        i = path.rfind("/", 0, -1)
        func_name = path[i + 1: -1].encode("ascii")
    else:
        i = path.rfind("/")
        func_name = path[i + 1:].encode("ascii")
    return func_name

class Protocol:
    def __init__(self, func, code_err, code_badparam, gwlog, accesslog, errlog):
        self._func = func
        self._gwlog = gwlog
        self._accesslog = accesslog
        self._errlog = errlog
        self._code_err = code_err
        self._code_badparam = code_badparam

    def _make_result(self, stat, data=None, headers=None):
        if data == None:
            data = {}
        if headers == None:
            headers = []
        jsoncontent = Protocol.make_json_content(self._errlog, stat, data)
        return "200 OK", headers, (jsoncontent,)

    @staticmethod
    def make_json_content(errlog, stat, data):
        try:
            data["stat"] = stat
            ret = json.dumps(data)
            if isinstance(ret, unicode):
                ret = ret.encode("utf8")
            return ret
        except:
            errlog.log("Json dump failed\n%s" % traceback.format_exc())
            return """{"stat": "%s", "MSG": "Dump json result error"}""" % self._code_err

    def __call__(self, ip, wsgienv):
        t = time.time()
        try:
            params = httpget2dict(wsgienv.get("QUERY_STRING"))
            if not check_param(self._func, params):
                if self._gwlog:
                    self._gwlog.log("%s Param check failed" % ip)
                return self._make_result(self._code_badparam)
        except:
            if self._gwlog:
                self._gwlog.log("%s Param check failed\n%s" % (ip, traceback.format_exc()))
            return self._make_result(self._code_badparam)

        try:
            ret = self._func(**params)
            if isinstance(ret, str): # return retstats.OK
                ret = (ret, {}, [])
            elif isinstance(ret, tuple) and len(ret) == 2: # return (retstats.OK, {k:v})
                ret = (ret[0], ret[1], [])
            r = self._make_result(ret[0], ret[1], ret[2]) # return (retstats.OK, {k:v}, [(k,v)])
        except:
            self._errlog.log("Server exception\n%s" % traceback.format_exc())
            ret = (self._code_err,)
            r = self._make_result(self._code_err)
        cost = time.time() - t
        if self._accesslog:
            self._accesslog.log("%s\t%s\t%s\t%s\t%s" %
                (ip, self._func.func_code.co_name, ret[0], params, cost))
        r[1].append(("GWC", str(cost)))
        return r
