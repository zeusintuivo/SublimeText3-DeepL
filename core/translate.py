#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL

__version__ = "1.0.0"

try:
    # Sublime environment assumption
    import sublime
except ImportError:
    # Python 2 assumption
    class Sublime(object):
        @staticmethod
        def version():
            return '2'
        pass
    sublime = Sublime()


try:
    # Python 3 assumption
    import urllib
    from urllib.request import urlopen, build_opener, Request
    from urllib.parse import urlencode, quote, unquote
except ImportError:
    # Python 2 assumption
    from urllib import urlopen, urlencode, quote, unquote

from json import loads
from pprint import pprint
import re
import json
import random
from pprint import pprint

if sublime.version() < '3':
    from urllib2 import urlopen, build_opener, Request
    from handler_st2 import *
    from socks_st2 import *
else:
    from .handler_st3 import *
    from .socks_st3 import *


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
        505: "TOO_MANY_LINES",
    }

    def __init__(self, settings):
        print('auth_key:', settings.get('auth_key'))
        self.settings = settings
        self.source = settings.get('source_language', 'auto')
        self.target = settings.get('target_language', 'en')
        self.target_type = settings.get('target_type', 'plain')
        self.proxy_ok = settings.get('proxy_enable')
        self.proxy_tp = settings.get('proxy_type')
        self.proxy_ho = settings.get('proxy_host')
        self.proxy_po = settings.get('proxy_port')
        self.auth = settings.get('auth_key')
        if self.proxy_ok == 'yes':
            if not self.proxy_tp or not self.proxy_ho or not self.proxy_po:
                raise DeeplTranslateException(self.error_codes[504])
        self.settings_list = [self.source,
                              self.target,
                              settings.get('keep_moving_down'),
                              self.target_type,
                              settings.get('auth_key'),
                              self.proxy_ok,
                              self.proxy_tp,
                              self.proxy_ho,
                              self.proxy_po]
        self.cache = {
            'languages': None,
        }
        self.api_urls = {
            'translate': 'https://api.deepl.com/v2/translate?auth_key=' + self.auth
        }

    @property
    def callback(self):
        return self._get_translation_from_deepl

    @property
    def languages(self, cache=True):
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
            raise DeeplTranslateException(self.error_codes[501])
        except ValueError:
            raise DeeplTranslateException(self.error_codes[503])
        return self.cache['languages']

    def _get_translation_from_deepl(self, text):
        try:
            loaded = self._get_json5_from_deepl(text)
            translation = self._get_translation_from_json(loaded)
        except IOError:
            raise DeeplTranslateException(self.error_codes[501])
        except ValueError:
            raise DeeplTranslateException(self.error_codes[503])
        print('_get_translation_from_deepl:', translation)
        return translation

    def build_url(self, text):
        e = quote(text, '')
        s = self.api_urls['translate'] + "&preserve_formatting=1"
        if self.source == 'auto':
            return s + "&target_lang=%s&text=%s" % (self.target, e)
        else:
            return s + "&source_lang=%s&target_lang=%s&text=%s" % (self.source, self.target, e)

    def select_proxy_opener(self):
        if self.proxy_tp == 'socks5':
            opener = build_opener(SocksiPyHandler(PROXY_TYPE_SOCKS5, self.proxy_ho, int(self.proxy_po)))
        else:
            if self.proxy_tp == 'socks4':
                opener = build_opener(SocksiPyHandler(PROXY_TYPE_SOCKS4, self.proxy_ho, int(self.proxy_po)))
            else:
                opener = build_opener(SocksiPyHandler(PROXY_TYPE_HTTP, self.proxy_ho, int(self.proxy_po)))
        return opener

    def _get_json5_from_deepl(self, text):
        headerses = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
                     'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/67.0',
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/75.0.3770.100 Safari/537.36']
        headers = {'User-Agent': headerses[random.randrange(len(headerses))]}
        request_url = self.build_url(text)
        if self.proxy_ok == 'yes':
            opener = self.select_proxy_opener()
            # print('request_url 1:' + request_url)
            req = Request(request_url, headers=headers)
            result = opener.open(req, timeout=2).read()
            loaded = loads(result.decode('utf-8'))
            return loaded
        else:
            # print('request_url 2:' + request_url)
            try:
                web_url = urllib.request.urlopen(request_url)
                data = web_url.read()
                encoding = web_url.info().get_content_charset('utf-8')
                loaded = loads(data.decode(encoding))
            except IOError:
                raise DeeplTranslateException(self.error_codes[501])
            except ValueError:
                raise DeeplTranslateException(loaded['message'])
            return loaded

    @staticmethod
    def _get_translation_from_json(loaded):
        translations = loaded['translations']
        # detected_lang = translations[0]['detected_source_language']
        translation = translations[0]['text']
        print('translation 1 ')
        pprint(translation)
        return translation


if __name__ == "__main__":
    import doctest

    doctest.testmod()
