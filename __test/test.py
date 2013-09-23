#coding:utf8
# Author: aeris
# Created: 09/22/2013

import nose.tools
import urllib2
import env

def test():
    url = 'http://' +env.SERVER + ':' + str(env.PORT) + '/'
    operation = 'zip_package'
    fileurl = "filelist=http%3A%2F%2F192.168.135.64%2Fhjr%2Ffilelist"
    req = url + operation + '?' + fileurl
    fs = urllib2.urlopen(req)
    assert len(fs.read()) == int(fs.info().get('content-length'))
    
    url = 'http://' +env.SERVER + ':' + str(env.PORT) + '/'
    operation = 'zip_package'
    fileurl = "filelist=http%3A%2F%2F192.168.135.64%2Fhjr%2Ffilelist_error"
    req = url + operation + '?' + fileurl
    nose.tools.assert_raises(urllib2.HTTPError, urllib2.urlopen, req)
    
if __name__ == '__main__':  
    test()