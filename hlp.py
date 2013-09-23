#coding:utf8
# Author: aeris
# Created: 09/22/2013

import config
import logger

def _mk_err_ret(status, reason, ip, loginfo=""):
    logger.failedlog.log("%s\t%s\t%s\t%s" % (ip, status, reason, str(loginfo)))
    return status, [], ()