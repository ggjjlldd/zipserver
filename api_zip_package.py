#coding:utf8
# Author: aeris
# Created: 09/22/2013

import struct
import os
import time
import json
import urllib2

from xlib import util
from xlib import retstat
from xlib import ziplib_spec

import config
import hlp


FILELISTTYPE = 1 # 1 is json format
DEFAULTZIPNAME = 'all.zip'
DEFAULTZIPENCODING = 'utf-8'

def ping():
    clen = struct.unpack("i", os.urandom(4))[0] % 512 + 64
    randstr = random_str = util.Base64_16.bin_to_b64(os.urandom(clen))
    return retstat.OK, {"randstr": randstr}

def get_content(files):
    if FILELISTTYPE == 1:
        files = json.loads(files)
    return files.get('stat'), files.get('attr'), files.get('zipfiles') 

def get_attr(attr):
    attr_set = {}
    for item in attr:
        attr_set.update(item)
    try:
        zipname = attr_set['zipname']
    except:
        zipname = DEFAULTZIPNAME
        
    try:
        zipencoding = attr_set['zipencoding']
    except:
        zipencoding = DEFAULTZIPENCODING
    
    return zipname, zipencoding

def get_file(filelist):
    urlfile = urllib2.urlopen(str(filelist))
    return urlfile.read()

def parse_item(item):
    attrs_file = {}
    for i in item:
        attrs_file.update(i)
    path, size, url = attrs_file.get('path'), attrs_file.get('size'), attrs_file.get('url')
    return path, size, url
    
def get_zipsize(zipfiles, zipencoding):
    zipfileset = []
    for item in zipfiles:
        path, size, url = parse_item(item)
        zipfileset.append((int(size), path))
    return ziplib_spec.get_zip_size(zipfileset, zipencoding)

def gen_file(urlfile, size):
    left = int(size)
    while 1:
        trunk = urlfile.read(config.ZIP_BLK_SIZE)
        left = left - len(trunk)
        yield trunk 
        if left == 0 :
            break
    
def zippack(zipfiles, zipname, zipencoding):
    
    source = []    
    for item in zipfiles:
        path, size, url = parse_item(item)
        urlfile = urllib2.urlopen(url)
        contentlen = urlfile.info().get('content-length')
        if size and contentlen != size:
            raise
        it = gen_file(urlfile, size)
        mtime = urlfile.info().get('mtime')
        if not mtime:
            mtime = int(time.time())
        source.append((it, int(size), path, mtime))
        
    return ziplib_spec.get_zip(source, zipencoding)

def zip_package(ip, wsgienv, param_get):
    try:
        filelist = param_get['filelist']
    except:
        return hlp._mk_err_ret(retstat.HTTP_BAD_PARAMS, "Invalid file list", ip, param_get)
    
    try:
        files = get_file(filelist)
    except:
        return hlp._mk_err_ret(retstat.HTTP_BAD_PARAMS, "Invalid file url", ip, param_get)
    
    stat, attr, zipfiles = get_content(files)
    
    if stat != retstat.HTTP_OK :
        return hlp._mk_err_ret(retstat.HTTP_BAD_PARAMS, "stat status not ok", ip, param_get)
    
    zipname, zipencoding = get_attr(attr)
    
    try:
        zipsize = get_zipsize(zipfiles, zipencoding) 
    except:
        zipsize = None
    try:
        it = zippack(zipfiles, zipname, zipencoding)
    except:
        return hlp._mk_err_ret(retstat.HTTP_BAD_PARAMS, "Invalid file list", ip, param_get)
    
    headers = []
    if zipsize:
        headers.append(("content-length", str(zipsize)))
    headers.append(("X-Archive-Files", "zip"))
    headers.append(("X-Archive-Charset", str(zipencoding)))
    headers.append(("Content-Disposition", str("attachment; filename=" + zipname)))
        
    return retstat.HTTP_OK, headers, it
        
        
    
    
    
    