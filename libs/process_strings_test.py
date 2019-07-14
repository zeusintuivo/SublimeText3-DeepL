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
                "'",
             5: "'",
             6: "  warning_html: 'Sie haben soeben %{date} %{recurring} eine Abwesenheit eingetragen."
                "<br/> %{count_rdv}<br/> <span class=\"question\">Wie wollen Sie fortfahren?</span>",
             7: "                eingetragen.<br/> %{count_rdv}<br/> <span class=\"question\">"
                "Wie wollen Sie fortfahren?</span>",
             8: "  warning_html: 'Sie haben soeben %{date} %{recurring} eine Abwesenheit eingetragen.<br/> "
                "%{count_rdv}<br/> <span class=\"question\">Wie wollen Sie fortfahren?</span>"

             }

    process_strings = ProcessStrings()

    # def test_enters(self):
    #     self.assertEqual(self.process_strings.translate(self.tests[1], 'es', 'de', 'yml', True),
    #                      '          Cual es tu decision?\n\n "')
    #
    # def test_enters_double(self):
    #     self.assertEqual(self.process_strings.translate(self.tests[2], 'es', 'de', 'yml', True),
    #                      '          Cual es tu decision?\\n\\n "')
    #
    # def test_tag_quote(self):
    #     self.assertEqual(self.process_strings.translate(self.tests[3], 'es', 'de', 'yml', True),
    #                      ' <strong class="do-not-translate-this"> translated(Es ist ein Termin) </strong> '
    #                      'translated(w\xc3\xa4hrend dieser Abwesenheit vorgesehen.)')
    #
    # def test_key_quote_tag(self):
    #     self.assertEqual(self.process_strings.translate(self.tests[4], 'es', 'de', 'yml', True),
    #                      '              warning_html: \'translated(Sie haben soeben) %{date}   %{recurring}'
    #                      ' translated( eine Abwesenheit                eingetragen.) <br/>   %{count_rdv}  '
    #                      '<br/>   <span class="question"> translated(Wie wollen                '
    #                      'Sie fortfahren?) </span> \'')
    #
    # def test_one_single_quote(self):
    #     self.assertEqual(self.process_strings.translate(self.tests[5], 'es', 'de', 'yml', True),
    #                      "'")
    #
    # def test_one_double_quote(self):
    #     self.assertEqual(self.process_strings.translate('"', 'es', 'de', 'yml', True), '"')
    #
    def test_key_tag_var(self):
        self.assertEqual(self.process_strings.translate(self.tests[6], 'es', 'de', 'yml', True),
                         '  warning_html: \'Acabas de %{date} %{recurring} una auscencia inscrito.<br/> %{count_rdv}'
                         '<br/> <span class="question">\xc2\xbfC\xc3\xb3mo piensa proceder?</span>')

    def test_one_line_complex(self):
        self.assertEqual(self.process_strings.translate(self.tests[7], 'es', 'de', 'yml', True),
                         '                est\xc3\xa1 registrado.<br/> %{count_rdv}<br/> <span class="question">'
                         '\xc2\xbfC\xc3\xb3mo piensa proceder?</span>')

    def test_one_line_complex_2(self):
        self.assertEqual(self.process_strings.translate(self.tests[8], 'es', 'de', 'yml', True),
                         '  warning_html: \'Acabas de %{date} %{recurring} una auscencia inscrito.<br/> '
                         '%{count_rdv}<br/> <span class="question">\xc2\xbfC\xc3\xb3mo piensa proceder?</span>')


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