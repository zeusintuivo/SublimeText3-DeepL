#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL

__version__ = "1.0.0"

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


class ProcessStrings(object):

    error_codes = {
        401: "ERR_TARGET_LANGUAGE_NOT_SPECIFIED",
        501: "ERR_SERVICE_NOT_AVAILABLE_TRY_AGAIN_OR_USE_PROXY",
        503: "ERR_VALUE_ERROR",
        504: "ERR_PROXY_NOT_SPECIFIED",
        505: "TOO_MANY_LINES",
    }

    def __init__(self, callback=None):
        self.callback = callback

    def translate(self, text, target_language, source_language, formato='html', fake=True):
        original = unquote(quote(text, ''))
        print('original:', original)
        # if "'" in original:
        #    original = original.replace("'", '"')
        print('orig quo:', original)
        if formato == 'plain':
            data = self._get_translation_from_deepl(original, fake)
            data = self.filter_tags(data)
        elif formato == 'yml':
            if len(original) > 256:
                print('1')
                data = self.fix_too_long_text(original, fake)
            else:
                print('2')
                if self.is_it_just_a_key(original):
                    if original == source_language + ':':  # change fr: to es:
                        data = target_language + ':'
                    else:
                        data = original
                else:
                    if self.starts_with_key(original):
                        saved_key = self.obtain_key(original)
                        translate_this = self.obtain_second_part(original)
                        if "\\n" in translate_this:
                            print('a3c')
                            data = saved_key + ': ' + self.fix_enters_keep(translate_this, fake, "\\n")
                        elif "\n" in translate_this:
                            print('a3c')
                            data = saved_key + ': ' + self.fix_enters_keep(translate_this, fake, "\n")
                        elif "'" in translate_this:
                            print('a3a')
                            data = saved_key + ': ' + self.fix_singlequote_keep(translate_this, fake)
                        elif '"' in translate_this:
                            print('a3b')
                            data = saved_key + ': ' + self.fix_doublequote_keep(translate_this, fake)
                        elif '<' in translate_this:
                            print('a3d')
                            data = saved_key + ': ' + self.fix_html_keep(translate_this, fake)
                        elif '%{' in original:
                            print('a4')
                            data = saved_key + ': ' + self.fix_variable_keep(translate_this, fake)
                        else:
                            print('a5')
                            data = saved_key + ': ' + self._get_translation_from_deepl(translate_this, fake)
                    else:
                        data = self.original_work_distribute(original, fake)
                    data = self.fix_yml(original, data, target_language, source_language)
        else:
            data = self._get_translation_from_deepl(text, fake)
            data = self.fix_deepl(data)
        return data

    def original_work_distribute(self, original, fake):
        if "\\n" in original:
            print('c3c', original)
            return self.fix_enters_keep(original, fake, "\\n")
        elif "\n" in original:
            print('c3c', original)
            return self.fix_enters_keep(original, fake, "\n")
        elif "'" in original:
            print('c3a')
            if '<' in original:
                print('c3axd')
                return self.fix_html_keep(original, fake)
            else:
                return self.fix_singlequote_keep(original, fake)
        elif '"' in original:
            print('c3b')
            if '<' in original:
                print('c3bxd')
                return self.fix_html_keep(original, fake)
            else:
                return self.fix_doublequote_keep(original, fake)
        elif '<' in original:
            print('c3d')
            return self.fix_html_keep(original, fake)
        elif '%{' in original:
            print('c4')
            return self.fix_variable_keep(original, fake)
        else:
            print('c5 _get_translation_from_deepl', original)
            return self._get_translation_from_deepl(original, fake)

    @staticmethod
    def starts_with_key(original):
        print(20)
        original_no_spaces = original.lstrip()
        original_no_spaces_all = original_no_spaces.rstrip()
        print(21)
        original_key_is = original_no_spaces.split(':')
        print(22)
        key_has_spaces = original_key_is[0].split(' ')
        print(23)
        second_part_exists = ""
        if len(original_key_is) > 1:
            second_part_exists = original_key_is[1].lstrip().rstrip()
        if ':' in original and ':' in original and len(original_key_is) >= 2 and len(key_has_spaces) == 1:
            if len(second_part_exists) > 0:
                print('has hey and second part has content:(' + second_part_exists + ')')
                # empty second meaning, then is a like == key: or key:>  or key: |
                return True
        return False

    @staticmethod
    def obtain_key(original):
        print(30)
        first_source_colon = original.find(':')
        keep_source_definition = original[:first_source_colon]
        print('has hey called:(' + keep_source_definition + ')')
        # empty second meaning, then is a like == key: or key:>  or key: |
        return keep_source_definition

    @staticmethod
    def obtain_second_part(original):
        print(40)
        first_source_colon = original.find(':')
        second_part = original[(first_source_colon + 1):]
        print('has second part:(' + second_part + ')')
        # empty second meaning, then is a like == key: or key:>  or key: |
        return second_part.lstrip().rstrip()

    @staticmethod
    def is_it_just_a_key(original):
        print(10)
        original_no_spaces = original.lstrip()
        original_no_spaces_all = original_no_spaces.rstrip()
        if original_no_spaces_all in (None, '', '<br/>', '</i>', '<strong>', '</strong>', '<i>', '<br>', '</br>'):
            # skip empty br's
            return True
        print(11)
        original_key_is = original_no_spaces.split(':')
        print(12)
        key_has_spaces = original_key_is[0].split(' ')
        print(13)
        second_part_exists = ""
        if len(original_key_is) > 1:
            second_part_exists = original_key_is[1].lstrip().rstrip()
        if ':' in original and len(original_key_is) >= 2 and len(key_has_spaces) == 1:
            if second_part_exists in (None, '', '>', '|', '|-'):
                print('row has a yml key:(' + original + ')')
                # empty second meaning, then is a like == key: or key:>  or key: |
                return True
        return False

    def fix_too_long_text(self, original, fake):
        sentence_data = original
        if len(original) > 256:
            sentence_data = ""
            split_sentences = original.split('.')
            for sentence in split_sentences:
                if '<' in original:
                    print('23')
                    sentence_data = sentence_data + self.fix_html_keep(sentence, fake)
                elif '%{' in original:
                    print('24')
                    sentence_data = sentence_data + self.fix_variable_keep(sentence, fake)
                else:
                    sentence_data = sentence_data + self._get_translation_from_deepl(sentence, fake)
        return sentence_data

    def fix_variable_keep(self, sentence, fake):
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
                        splited_data = self._get_translation_from_deepl(second_part_split, fake)
                    if count_split == 0:
                        splitted_trans = splitted_trans + cut_other_part[0] + '} ' + splited_data
                    else:
                        splitted_trans = splitted_trans + ' %{' + cut_other_part[0] + '} ' + splited_data
                else:
                    splited_data = self._get_translation_from_deepl(splitted, fake)
                    splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + ' %{' + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

    def fix_singlequote_keep(self, sentence, fake):
        sentence_data = ""
        split_percent = sentence.split("'")
        splitted_trans = ""
        count_split = 0
        for splitted in split_percent:
            if splitted in (None, ''):
                splitted_trans = splitted_trans + "'"
            else:
                splited_data = self.original_work_distribute(splitted, fake)
                splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + "'" + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

    def fix_doublequote_keep(self, sentence, fake):
        sentence_data = ""
        split_percent = sentence.split('"')
        splitted_trans = ""
        count_split = 0
        for splitted in split_percent:
            if splitted in (None, ''):
                splitted_trans = splitted_trans + '"'
            else:
                splited_data = self.original_work_distribute(splitted, fake)
                splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + '"' + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

    def fix_enters_keep(self, sentence, fake, tipo="\n"):
        print("fix_" + tipo + "_enters_keep", sentence)
        sentence_data = ""
        split_percent = sentence.split(tipo)
        pprint(split_percent)
        splitted_trans = ""
        count_split = 0
        for splitted in split_percent:
            count_split = count_split + 1
            print("simple splited_data", splitted)
            if splitted in (None, ''):
                print("adding enter")
                splitted_trans = splitted_trans + tipo
            else:
                print("work distribute", splitted)
                splited_data = self.original_work_distribute(splitted, fake)
                print("work translated", splited_data)

                print("count_split", count_split)
                if count_split < len(split_percent):
                    splited_data = splited_data + tipo
                    print("adding enter")
                    print("work translated", splited_data)
                splitted_trans = splitted_trans + splited_data

        print("split_percent", split_percent)
        if count_split == 0:
            sentence_data = sentence_data + tipo + splitted_trans
        else:
            sentence_data = splitted_trans
        print("sentence_data", sentence_data)
        return sentence_data

    def fix_html_keep(self, sentence, fake):
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
                        splited_data = self.fix_variable_keep(second_part_split, fake)
                        # splited_data = self._get_translation_from_deepl(second_part_split)
                    if count_split == 0:
                        splitted_trans = splitted_trans + cut_other_part[0] + '> ' + splited_data
                    else:
                        splitted_trans = splitted_trans + ' <' + cut_other_part[0] + '> ' + splited_data
                else:
                    splited_data = self.fix_variable_keep(splitted, fake)
                    # splited_data = self._get_translation_from_deepl(splitted)
                    splitted_trans = splitted_trans + splited_data
                count_split = count_split + 1
        if count_split == 0:
            sentence_data = sentence_data + ' <' + splitted_trans
        else:
            sentence_data = splitted_trans
        return sentence_data

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
        if ':' in original and ':' in html_string and len(original_key_is) >= 2 and len(
                key_has_spaces) == 1:  # fix keep keys names
            print('yml key protection:' + original + ')')
            first_source_colon = original.find(':')
            keep_source_definition = original[:first_source_colon]
            # print('length(' + str(12) + ') def(' + keep_source_definition + ')')
            first_translated_colon = html_string.find(':')
            keep_translated_text = html_string[(first_translated_colon + 1):]
            # print('length(' + str(32) + ') trans(' + keep_translated_text + ')')
            html_string = keep_source_definition + ': ' + keep_translated_text.lstrip()
            # new_largo = len(html_string)
        print('original(' + original + ')')
        # print('source_language(' + source_language + ')')
        # print('target_language(' + target_language + ')')
        if '{' in original and '{' in html_string and '%' in original and '%' in html_string:  # fix  % { to  %{
            html_string = html_string.replace('% {', ' %{')
        if '},' in original and '} ,' in html_string:  # fix  } , to  },
            html_string = html_string.replace('} ,', '},')
        if ': >' in original and ':>' in html_string:  # fix :> to : >
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
    def _get_translation_from_fake_deepl(text):
        if text == '<strong class="count-suspendable-citas">Es ist ein Termin</strong>während dieser ' \
                   'Abwesenheit vorgesehen.':
            return ' <clase fuerte=conteo-suspendible-citas> Es una cita </strong>durante esta ausencia.'
        if text == '          \\ Wie lautet Ihre Wahl?':
            return 'Cual es tu decision?'
        else:
            return 'translated(' + text + ')'

    def _get_translation_from_deepl(self, text, fake):
        if text.lstrip().rstrip() in (None, '', '>', '|', '|-', '"', "'", '.', ',', ';', ':'):
            return text
        if fake:
            return self._get_translation_from_fake_deepl(text.rstrip())
        loaded = self.callback(text.rstrip())
        translation = self._get_translation_from_json(loaded)
        return translation

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

