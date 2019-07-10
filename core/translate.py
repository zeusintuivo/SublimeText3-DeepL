#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL

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

    def translate(self, text, target_language, source_language, formato='html'):
        original = unquote(quote(text, ''))
        print('original:', original)
        if "'" in original:
            original = original.replace("'", '"')
        print('original quo:', original)
        if formato == 'plain':
            data = self._get_translation_from_deepl(original)
            data = self.filter_tags(data)
        elif formato == 'yml':
            if len(original) > 256:
                print('1')
                data = self.fix_too_long_text(original)
            else:
                print('2')
                if self.is_it_just_a_key(original):
                    if original == source_language + ':':  # change fr: to es:
                        data = target_language + ':'
                    else:
                        data = original
                else:
                    if '<' in original:
                        print('3')
                        data = self.fix_html_keep(original)
                    elif '%{' in original:
                        print('4')
                        data = self.fix_variable_keep(original)
                    else:
                        data = self._get_translation_from_deepl(original)
                    data = self.fix_yml(original, data, target_language, source_language)
        else:
            data = self._get_translation_from_deepl(text)
            data = self.fix_deepl(data)
        return data

    @staticmethod
    def is_it_just_a_key(original):
        print(10)
        original_no_spaces = original.lstrip()
        original_no_spaces_all = original_no_spaces.rstrip()
        if original_no_spaces_all in (None, '', '<br/>', '</i>', '<strong>', '</strong>',
                                      '<i>', '<br>', '</br>'):  # skip empty br's
            return True
        print(11)
        original_key_is = original_no_spaces.split(':')
        print(12)
        key_has_spaces = original_key_is[0].split(' ')
        print(13)
        second_part_exists = ""
        if len(original_key_is) > 1:
            second_part_exists = original_key_is[1].lstrip().rstrip()
        if ':' in original and ':' in original and len(original_key_is) >= 2 and len(key_has_spaces) == 1:
            print('row has a yml key:(' + original + ')')
            if second_part_exists in (None, '', '>', '|'):
                # empty second meaning, then is a like == key: or key:>  or key: |
                return True
        return False

    def fix_too_long_text(self, original):
        sentence_data = original
        if len(original) > 256:
            sentence_data = ""
            split_sentences = original.split('.')
            for sentence in split_sentences:
                if '<' in original:
                    print('23')
                    sentence_data = sentence_data + self.fix_html_keep(sentence)
                elif '%{' in original:
                    print('24')
                    sentence_data = sentence_data + self.fix_variable_keep(sentence)
                else:
                    sentence_data = sentence_data + self._get_translation_from_google(sentence)
        return sentence_data

    def fix_variable_keep(self, sentence):
        sentence_data = ""
        split_percent = sentence.split('%{')
        splitted_trans = ""
        count_split = 0
        for splitted in split_percent:
            if splitted in (None, ''):
                # case 1 "%{time_ago} Dernière connexion sur le compte : il y a %{%{time_ago}%{time_ago}.".split('%{')
                # ['', 'time_ago} Dernière connexion sur le compte : il y a ', '', 'time_ago}', 'time_ago}.']
                # splitted = split_percent[0]  -- '' = splitted_trans = '%{'
                # splitted = split_percent[1]  -- 'time_ago} Dernière connexion sur le compte : il y a '
                # splitted = split_percent[2]  -- ''
                # splitted = split_percent[3]  -- 'time_ago}'
                # splitted = split_percent[4]  -- 'time_ago}'
                # -
                # case 2 "%{details_link}"
                # ['', 'details_link}']
                splitted_trans = splitted_trans + ' %{'
            else:
                if '}' in splitted:
                    # 'time_ago} Dernière connexion sur le compte : il y a '
                    cut_other_part = splitted.split('}')
                    # ['time_ago', ' Dernière connexion sur le compte : il y a ']
                    second_part_split = cut_other_part[1]
                    #              ' Dernière connexion sur le compte : il y a '
                    if second_part_split in (None, ''):
                        splited_data = ''
                    else:
                        splited_data = self._get_translation_from_deepl(second_part_split)
                    if count_split == 0:
                        splitted_trans = splitted_trans + cut_other_part[0] + '} ' + splited_data
                    else:
                        splitted_trans = splitted_trans + ' %{' + cut_other_part[0] + '} ' + splited_data
                else:
                    splited_data = self._get_translation_from_deepl(splitted)
                    splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + ' %{' + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

    def fix_html_keep(self, sentence):
        sentence_data = ""
        split_percent = sentence.split('<')
        splitted_trans = ""
        count_split = 0
        for splitted in split_percent:
            if splitted in (None, ''):
                # case 1 "%{time_ago} Dernière connexion sur le compte : il y a %{%{time_ago}%{time_ago}.".split('%{')
                # ['', 'time_ago} Dernière connexion sur le compte : il y a ', '', 'time_ago}', 'time_ago}.']
                # splitted = split_percent[0]  -- '' = splitted_trans = '%{'
                # splitted = split_percent[1]  -- 'time_ago} Dernière connexion sur le compte : il y a '
                # splitted = split_percent[2]  -- ''
                # splitted = split_percent[3]  -- 'time_ago}'
                # splitted = split_percent[4]  -- 'time_ago}'
                # -
                # case 2 "%{details_link}"
                # ['', 'details_link}']
                splitted_trans = splitted_trans + ' <'
            else:
                if '>' in splitted:
                    # 'time_ago} Dernière connexion sur le compte : il y a '
                    cut_other_part = splitted.split('>')
                    # ['time_ago', ' Dernière connexion sur le compte : il y a ']
                    second_part_split = cut_other_part[1]
                    #              ' Dernière connexion sur le compte : il y a '
                    if second_part_split in (None, ''):
                        splited_data = ''
                    else:
                        splited_data = self.fix_variable_keep(second_part_split)
                        # splited_data = self._get_translation_from_deepl(second_part_split)
                    if count_split == 0:
                        splitted_trans = splitted_trans + cut_other_part[0] + '> ' + splited_data
                    else:
                        splitted_trans = splitted_trans + ' <' + cut_other_part[0] + '> ' + splited_data
                else:
                    splited_data = self.fix_variable_keep(splitted)
                    # splited_data = self._get_translation_from_deepl(splitted)
                    splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + ' <' + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
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
        return json

    def is_json(myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True

    @staticmethod
    def _get_translation_from_json(loaded):
        translations = loaded['translations']
        # deteced_lang = translations[0]['detected_source_language']
        translation = translations[0]['text']
        print('translation')
        pprint(translation)
        return translation

    @staticmethod
    def _unescape(text):
        return loads('"%s"' % text)

    def filter_tags(self, htmlstr):
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
        re_br = re.compile('<br\s*?/?>')
        re_h = re.compile('</?\w+[^>]*>')
        re_comment = re.compile('<!--[^>]*-->')
        s = re_cdata.sub('', htmlstr)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_br.sub('\n', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)

        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.re_exp(s)
        s = self.replace_char_entity(s)
        return s

    @staticmethod
    def re_exp(htmlstr):
        s = re.compile(r'<[^<]+?>')
        return s.sub('', htmlstr)

    @staticmethod
    def replace_char_entity(html_string):
        char_entities = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_char_entity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_char_entity.search(html_string)
        while sz:
            entity = sz.group()
            key = sz.group('name')
            try:
                html_string = re_char_entity.sub(char_entities[key], html_string, 1)
                sz = re_char_entity.search(html_string)
            except KeyError:
                html_string = re_char_entity.sub('', html_string, 1)
                sz = re_char_entity.search(html_string)
        return html_string

    @staticmethod
    def fix_yml(original, html_string, target_language, source_language):
        original_no_spaces = original.lstrip()
        original_key_is = original_no_spaces.split(':')
        key_has_spaces = original_key_is[0].split(' ')
        original_len = len(original)
        original_no_spaces_len = len(original_no_spaces)
        original_missing_spaces_len = original_len - original_no_spaces_len
        original_missing_spaces = ' ' * original_missing_spaces_len

        s = re.compile(r'<[ ]{0,1}/ (?P<name>[a-zA-Z ]{1,})>')
        sz = s.search(html_string)
        while sz:
            entity = sz.group()
            # print (entity)
            key = sz.group('name')
            try:
                html_string = s.sub(r'</' + key.lower().strip() + '>', html_string, 1)
                sz = s.search(html_string)
            except KeyError:
                sz = s.search(html_string)
        # this is a key     in yml --> last_connection_html:
        # this is not a key in yml --> Dernière connexion sur le compte :
        if ':' in original and ':' in html_string and len(original_key_is) >= 2 and len(key_has_spaces) == 1:  # fix keep keys names
            print('yml key protection:' + original + ')')
            first_source_colon = original.find(':')
            keep_source_definition = original[:first_source_colon]
            # print('length(' + str(12) + ') def(' + keep_source_definition + ')')
            first_translated_colon = html_string.find(':')
            keep_translated_text = html_string[(first_translated_colon + 1):]
            # print('length(' + str(32) + ') trans(' + keep_translated_text + ')')
            html_string = keep_source_definition + ': ' + keep_translated_text
            # new_largo = len(html_string)
        print('original(' + original + ')')
        # print('source_language(' + source_language + ')')
        # print('target_language(' + target_language + ')')
        if '{' in original and '{' in html_string and '%' in original and '%' in html_string:   # fix  % { to  %{
            html_string = html_string.replace('% {', ' %{')
        if ': >' in original and ':>' in html_string:      # fix :> to : >
            html_string = html_string.replace(':>', ': >')

        # restore white spaces
        html_string_no_spaces = html_string.lstrip()
        html_string_len = len(html_string)
        html_string_no_spaces_len = len(html_string_no_spaces)
        html_string_missing_spaces_len = html_string_len - html_string_no_spaces_len
        # html_string_missing_spaces = ' ' * html_string_missing_spaces_len
        print('original_missing_spaces_len(' + str(original_missing_spaces_len) + ')')
        print('html_string_missing_spaces_len(' + str(html_string_missing_spaces_len) + ')')
        if original_missing_spaces_len > html_string_missing_spaces_len:
            html_string = original_missing_spaces + html_string
        print('html_string(' + html_string + ')')
        return html_string

    @staticmethod
    def fix_deepl(html_string):
        s = re.compile(r'<[ ]{0,1}/ (?P<name>[a-zA-Z ]{1,})>')
        sz = s.search(html_string)
        while sz:
            entity = sz.group()
            # print (entity)
            key = sz.group('name')
            try:
                html_string = s.sub(r'</' + key.lower().strip() + '>', html_string, 1)
                sz = s.search(html_string)
            except KeyError:
                sz = s.search(html_string)

        return html_string


if __name__ == "__main__":
    import doctest

    doctest.testmod()
