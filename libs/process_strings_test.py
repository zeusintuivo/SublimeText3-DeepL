#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL
from process_strings import ProcessStrings
from settings import settings_list
import unittest

__version__ = "1.0.0"


class TestProcessStrings(unittest.TestCase):
    tests = {1: '          \\ Wie lautet Ihre Wahl?\n\n "',
             2: '          \\ Wie lautet Ihre Wahl?\\n\\n "',
             3: '<strong class=\"do-not-translate-this\">Es ist ein Termin</strong>während dieser '
                'Abwesenheit vorgesehen.',
             4: "              warning_html: 'Sie haben soeben %{date} %{recurring} eine Abwesenheit"
                "                eingetragen.<br/> %{count_rdv}<br/> <span class=\"question\">Wie wollen"
                "                Sie fortfahren?</span>"
                "'"}

    process_strings = ProcessStrings()

    def test_enters(self):
        self.assertEqual(self.process_strings.translate(self.tests[1], 'es', 'de', 'yml', True),
                         '          Cual es tu decision?\n\n "')

    def test_enters_double(self):
        self.assertEqual(self.process_strings.translate(self.tests[2], 'es', 'de', 'yml', True),
                         '          Cual es tu decision?\\n\\n "')

    def test_tag_quote(self):
        self.assertEqual(self.process_strings.translate(self.tests[3], 'es', 'de', 'yml', True),
                         ' <strong class="do-not-translate-this"> translated(Es ist ein Termin) </strong> '
                         'translated(w\xc3\xa4hrend dieser Abwesenheit vorgesehen.)')

    def test_key_quote_tag(self):
        self.assertEqual(self.process_strings.translate(self.tests[4], 'es', 'de', 'yml', True),
                         '              warning_html: \'translated(Sie haben soeben) %{date}   %{recurring}'
                         ' translated( eine Abwesenheit                eingetragen.) <br/>   %{count_rdv}  '
                         '<br/>   <span class="question"> translated(Wie wollen                '
                         'Sie fortfahren?) </span> \'')


if __name__ == '__main__':
    unittest.main()

# "              warning_html: 'Acabas de %{date}   %{recurring}  una ausencia
#                está registrado. <br/>   %{count_rdv}  <br/>  span class=interrogante>¿Cómo se hace?
#                ¿Continúas? </span> "
#
# How to test:
#
# nodemon --watch process_strings_test.py --exec python process_strings_test.py
#
# nodemon --watch libs/process_strings_test.py --exec python libs/process_strings_test.py
#
