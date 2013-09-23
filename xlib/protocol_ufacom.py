#coding:utf8
# Author: zJay
# Created: 05/27/2011

import time
import traceback
import json

from xlib.httpgateway import check_param
from xlib.httpgateway import httpget2dict
from xlib.httpgateway import read_wsgi_post

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
        self._name = self._func.func_code.co_name

    def _make_result(self, stat, data=None, headers=None):
        if data == None:
            data = {}
        if headers == None:
            headers = []
        jsoncontent = Protocol.make_json_content(self._errlog, stat, data)
        headers.append(("Content-Length", str(len(jsoncontent))))
        return "200 OK", headers, (jsoncontent,)

    @staticmethod
    def make_json_content(errlog, stat, data):
        try:
            data["code"] = stat
            ret = json.dumps(data)
            if isinstance(ret, unicode):
                ret = ret.encode("utf8")
            return ret
        except:
            errlog.log("Json dump failed\n%s" % traceback.format_exc())
            return """{"code": "%s", "MSG": "Dump json result error"}""" % self._code_err

    def __call__(self, ip, wsgienv):
        t = time.time()
        try:
            params = httpget2dict(wsgienv.get("QUERY_STRING"))
            if wsgienv.get("REQUEST_METHOD") == "POST":
                post_data = read_wsgi_post(wsgienv)
                if post_data:
                    post_params = json.loads(post_data)
                    for k, v in post_params.iteritems():
                        params[str(k)] = post_params[k]
            
            if not check_param(self._func, params):
                if self._gwlog:
                    self._gwlog.log("%s Param check failed" % ip)
                return self._make_result(self._code_badparam)
        except:
            if self._gwlog:
                self._gwlog.log("%s Param check failed\n%s" % (ip, traceback.format_exc()))
            return self._make_result(self._code_badparam)

        try:
            code = self._code_err
            data = {}
            headers = []
            stat = {}
            stat_str = ""
            ret = self._func(**params)
            if isinstance(ret, str): # return retstats.OK
                code = ret
            elif isinstance(ret, tuple): 
                if len(ret) == 2: # return (retstats.OK, {k:v})
                    code, data = ret
                elif len(ret) == 3: # return (retstats.OK, {k:v}, {k:v})
                    code, data, stat = ret
                elif len(ret) == 4: # return (retstats.OK, {k:v}, {k:v}, [(k,v),])
                    code, data, stat, headers = ret
            r = self._make_result(code, data, headers) # return (retstats.OK, {k:v}, [(k,v)])
            stat_str = ",".join("%s=%s" % (k, v) for k, v in stat.iteritems())
        except:
            self._errlog.log("Server exception\n%s" % traceback.format_exc())
            ret = (self._code_err,)
            r = self._make_result(self._code_err)
        cost = time.time() - t
        if self._accesslog:
            self._accesslog.log("%s\t%s\t%s\t%s\t%s\t%s" %
                (ip, self._name, code, cost, stat_str, params))
        r[1].append(("GWC", str(cost)))
        return r