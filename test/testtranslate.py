# -*- coding: utf-8 -*-
# Sublime Text 3 test
__version__ = "1.0.0"

try:
    # Python 3 assumption
    from urllib.request import urlopen, HTTPHandler, HTTPSHandler, build_opener, Request
    from urllib.parse import urlencode, quote
except ImportError:
    # Python 2 assumption
    from urllib import urlopen, urlencode, quote
    from urllib2 import HTTPHandler, HTTPSHandler, build_opener, Request

from json import loads

import re

try:
    # Python 3 assumption
    from http.client import HTTPConnection, HTTPSConnection
except ImportError:
    # Python 2 assumption
    from httplib import HTTPConnection, HTTPSConnection

import socks
import ssl


class DeeplTranslateException(Exception):
    """
    Default DeeplTranslate exception
    >>> DeeplTranslateException("DoctestError")
    DeeplTranslateException('DoctestError',)
    """
    pass


class DeeplTranslate(object):
    string_pattern = r"\"(([^\"\\]|\\.)*)\""
    match_string = re.compile(
        r"\,?\["
        + string_pattern + r"\,"
        + string_pattern
        + r"\]")

    error_codes = {
        401: "ERR_TARGET_LANGUAGE_NOT_SPECIFIED",
        501: "ERR_SERVICE_NOT_AVAILABLE_TRY_AGAIN_OR_USE_PROXY",
        503: "ERR_VALUE_ERROR",
        504: "ERR_PROXY_NOT_SPECIFIED",
    }

    def __init__(self, source_lang='en', target_lang='zh-CN'):
        self.cache = {
            'languages': None,
        }
        self.api_urls = {
            'translate': 'https://translate.deepl.com/translate_a/single?client=t&ie=UTF-8&oe=UTF-8&dt=t',
        }
        if not target_lang:
            raise DeeplTranslateException(self.error_codes[401])
        self.source = source_lang
        self.target = target_lang

    @property
    def langs(self, cache=True):
        try:
            if not self.cache['languages'] and cache:
                self.cache['languages'] = loads('{"languages":{'
                                                '"en":"English",'
                                                '"es":"Spanish",'
                                                '"de":"German",'
                                                '"fr":"French",'
                                                '"it":"Italian",'
                                                '"pt":"Portuguese",'
                                                '"pl":"Polish",'
                                                '"nl":"Dutch",'
                                                '"ru":"Russian",'
                                                '}}')
        except IOError:
            raise DeeplTranslateException(self.error_codes[503])
        except ValueError:
            raise DeeplTranslateException(self.error_codes[501])
        return self.cache['languages']

    def translate(self, text, format='html'):
        data = self._get_translation_from_deepl(text)
        #if (format == 'plain')
            #data =
        return data

    def _get_translation_from_deepl(self, text):
        try:
            json5 = self._get_json5_from_deepl(text).decode('utf-8')
        except IOError:
            raise DeeplTranslateException(self.error_codes[503])
        except ValueError:
            raise DeeplTranslateException(self.error_codes[501])
        return self._unescape(self._get_translation_from_json5(json5.encode('utf-8')))

    def _get_json5_from_deepl(self, text):
        escaped_source = quote(text, '')
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        enable_proxy = True
        if enable_proxy:
            opener = build_opener(SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050))
            req = Request(self.api_urls['translate']+"&sl=%s&tl=%s&text=%s" % (self.source, self.target, escaped_source), headers = headers)
            result = opener.open(req, timeout = 5).read()
            json = result

        else:
            try:
                result = urlopen(self.api_urls['translate']
                         +"&sl=%s&tl=%s&text=%s" % (self.source, self.target, escaped_source), timeout = 5, headers = headers).read()
                json = loads(result.decode('utf-8'))
            except IOError:
                raise DeeplTranslateException(self.error_codes[503])
            except ValueError:
                raise DeeplTranslateException(result)
        return json

    def _get_translation_from_json5(self, content):
        result = ""
        pos = 2
        while True:
            m = self.match_string.match(content.decode('utf-8'), pos)
            if not m:
                break
            result += m.group(1)
            pos = m.end()
        return result

    def _unescape(self, text):
        return loads('"%s"' % text)

class SocksiPyConnection(http.client.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport=None, rdns=True, username=None, password=None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        http.client.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = socks.socksocket()
        self.sock.setproxy(*self.proxyargs)
        if type(self.timeout) in (int, float):
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

class SocksiPyConnectionS(http.client.HTTPSConnection):
    def __init__(self, proxytype, proxyaddr, proxyport=None, rdns=True, username=None, password=None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        http.client.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socks.socksocket()
        sock.setproxy(*self.proxyargs)
        if type(self.timeout) in (int, float):
            sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file)

class SocksiPyHandler(HTTPHandler, HTTPSHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs
        HTTPHandler.__init__(self)

    def http_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnection(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)

    def https_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnectionS(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)

if __name__ == "__main__":
    translate = DeeplTranslate('en', 'zh-CN')
    result = translate.translate('Hello, Beijing', 'html')
