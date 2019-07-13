#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL
from libs.fix_enters_keep import ProcessStrings

__version__ = "1.0.0"

import sublime

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
if sublime.version() < '3':
    from urllib2 import urlopen, build_opener, Request
    from handler_st2 import *
    from socks_st2 import *
else:
    from .handler_st3 import *
    from .socks_st3 import *


from ..libs.process_strings import ProcessStrings

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

    def __init__(self, proxy_enable, proxy_type, proxy_host, proxy_port, source_lang, target_lang):
        settings = sublime.load_settings("deeplTranslate.sublime-settings")
        auth_key = settings.get("auth_key")
        self.cache = {
            'languages': None,
        }
        self.api_urls = {
            'translate': 'https://api.deepl.com/v2/translate?auth_key=' + auth_key
        }
        # https://api.deepl.com/v2/translate?auth_key=___&text=___&source_lang=EN&target_lang=DE&preserve_formatting=1&tag_handling=xml
        if not source_lang:
            source_lang = 'auto'
        if not target_lang:
            target_lang = 'en'
            raise DeeplTranslateException(self.error_codes[401])
        if proxy_enable == 'yes':
            if not proxy_type or not proxy_host or not proxy_port:
                raise DeeplTranslateException(self.error_codes[504])
        self.source = source_lang
        self.target = target_lang
        self.proxyok = proxy_enable
        self.proxytp = proxy_type
        self.proxyho = proxy_host
        self.proxypo = proxy_port

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
        return translation

    def build_url(self, text):
        e = quote(text, '')
        # try:         #   other params  deepL   &source_lang=EN&target_lang=DE&preserve_formatting=1&tag_handling=xml
        s = self.api_urls['translate'] + "&preserve_formatting=1"
        if self.source == 'auto':
            return s + "&target_lang=%s&text=%s" % (self.target, e)
        else:
            return s + "&source_lang=%s&target_lang=%s&text=%s" % (self.source, self.target, e)

    def select_proxy_opener(self):
        if self.proxytp == 'socks5':
            opener = build_opener(SocksiPyHandler(PROXY_TYPE_SOCKS5, self.proxyho, int(self.proxypo)))
        else:
            if self.proxytp == 'socks4':
                opener = build_opener(SocksiPyHandler(PROXY_TYPE_SOCKS4, self.proxyho, int(self.proxypo)))
            else:
                opener = build_opener(SocksiPyHandler(PROXY_TYPE_HTTP, self.proxyho, int(self.proxypo)))
        return opener

    def _get_json5_from_deepl(self, text):
        headerses = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
                     'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/67.0',
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/75.0.3770.100 Safari/537.36']
        headers = {'User-Agent': headerses[random.randrange(len(headerses))]}
        request_url = self.build_url(text)
        if self.proxyok == 'yes':
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
        # deteced_lang = translations[0]['detected_source_language']
        translation = translations[0]['text']
        print('translation')
        pprint(translation)
        return translation


if __name__ == "__main__":
    import doctest
    doctest.testmod()
