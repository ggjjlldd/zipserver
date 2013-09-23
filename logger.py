#coding:utf8
# Author: zJay
# Created: 10/10/2011

from xlib.logger import LoggerBase
import config

critlog = LoggerBase(config.PATH_CRIT_LOG, False, 0)

errlog = LoggerBase(config.PATH_ERR_LOG, True, 0)

warninglog = LoggerBase(config.PATH_WARNING_LOG, True, 0)

infolog = LoggerBase(config.PATH_INFO_LOG, True, 0)

successlog = LoggerBase(config.PATH_SUCCESS_LOG, True, 0)

failedlog = LoggerBase(config.PATH_FAILED_LOG, True, 0)
