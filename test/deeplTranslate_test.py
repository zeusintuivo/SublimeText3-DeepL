#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL

__version__ = "1.0.0"

import platform
import os
import sys

# REF "how to absolute import from root" https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
python_version = platform.python_version()
path_cwd = os.getcwd()
print('Python version:', python_version)
print('Path version:', path_cwd)

# expectation  '3.7.3' < '3' or '2.7.11' < '3'
if python_version < '3':
    # Python 2 assumption
    from core.translate import *
    from libs.process_strings import *
    from libs.settings import *
    import unittest
else:
    # Python 3 assumption
    import unittest
    from core.translate import *
    from libs.process_strings import *
    from libs.settings import *


class TestDeeplTranslate(unittest.TestCase):
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
                "%{count_rdv}<br/> <span class=\"question\">Wie wollen Sie fortfahren?</span>",

             9: '                    on_same_day: Sie haben soeben am %{date} von %{start_time} bis',
             10: 'Sie haben soeben am',
             11: '        title: Centroderentas “responds to a specific need of society, it is practical and',
             12: '        title: Centroderentas “responds to a specific need of society, it is practical and '
                 'user-friendly, has an enormous amount of growth potential"',
             13: 'Centroderentas bietet einen einfach zu benutzenden Kalender, der von mobilen Geräten aus zugänglich '
                 'und den Bedürfnissen der 25 Ärzte der Renticenter angepasst ist.',
             14: 'Les Cookies dits « Techniques » (listés ci-après) ayant pour',
             15: "      # html: '<abbr title=\"required\">*</abbr>'",
             16: '      # html: "<abbr title=\'required\'>*</abbr>"',
             17: "      # html: '",
             18: '      # html: "'
             }
    settings = Settings()
    print('settings:', settings.settings)
    translate = DeeplTranslate(settings.settings)
    process_strings = ProcessStrings(translate.callback)

    def test_enters(self):
        self.assertEqual(self.process_strings.translate(self.tests[1], 'es', 'de', 'yml', True),
                         '          Cual es tu decision?\n\n"')

    def test_enters_double(self):
        self.assertEqual(self.process_strings.translate(self.tests[2], 'es', 'de', 'yml', False),
                         '          Cual es tu decision?\\n\\n"')

    def test_tag_quote(self):
        self.assertEqual(self.process_strings.translate(self.tests[3], 'es', 'de', 'yml', False),
                         '<strong class="do-not-translate-this">Es una cita</strong>durante esta ausencia.')

    def test_key_quote_tag(self):
        self.maxDiff = 1000
        self.assertEqual(self.process_strings.translate(self.tests[4], 'es', 'de', 'yml', False),
                         "              warning_html: 'Usted acaba de ver %{date} %{recurring} ha registrado "
                         "una ausencia.<br/> %{count_rdv}<br/> <span class=\"question\">¿Cómo piensa proceder?</span>'")

    def test_one_single_quote(self):
        self.assertEqual(self.process_strings.translate(self.tests[5], 'es', 'de', 'yml', False),
                         "'")

    def test_one_double_quote(self):
        self.assertEqual(self.process_strings.translate('"', 'es', 'de', 'yml', False), '"')

    def test_key_tag_var(self):
        self.assertEqual(self.process_strings.translate(self.tests[6], 'es', 'de', 'yml', False),
                         '  warning_html: \'Usted acaba de ver %{date} %{recurring} una auscencia inscrito.<br/> '
                         '%{count_rdv}<br/> <span class="question">¿Cómo piensa proceder?</span>')

    def test_one_line_complex(self):
        self.assertEqual(self.process_strings.translate(self.tests[7], 'es', 'de', 'yml', False),
                         '                está registrado.<br/> %{count_rdv}<br/> <span class="question">'
                         '¿Cómo piensa proceder?</span>')

    def test_one_line_complex_2(self):
        self.assertEqual(self.process_strings.translate(self.tests[8], 'es', 'de', 'yml', False),
                         "  warning_html: 'Usted acaba de ver %{date} %{recurring} una auscencia inscrito.<br/> "
                         "%{count_rdv}<br/> <span class=\"question\">¿Cómo piensa proceder?</span>")

    def test_one_line_now_what(self):
        self.assertEqual(self.process_strings.translate(self.tests[9], 'es', 'de', 'yml', False),
                         '                    on_same_day: Acabas de llegar al %{date} antes de %{start_time} '
                         'para cuando')

    def test_sqlite_response(self):
        self.assertEqual(self.process_strings.translate(self.tests[10], 'es', 'de', 'yml', False),
                         'Acabas de llegar al')

    def test_sqlite_response(self):
        self.assertEqual(self.process_strings.translate('Gesundheitseinrichtungen', 'es', 'de', 'yml', False),
                         'Centros de salud')

    def test_encoding_solve(self):
        self.assertEqual(self.process_strings.translate(self.tests[11], 'es', 'de', 'yml', False),
                         '        titulo: Centroderentas \\xe2\\x80\\x9cresponde a una necesidad '
                         'espec\xc3\xadfica de la sociedad, es pr\xc3\xa1ctico y')

    def test_encoding_solve(self):
        self.assertEqual(self.process_strings.translate(self.tests[13], 'es', 'de', 'yml', False),
                         'Centroderentas ofrece un calendario fácil de usar, accesible desde dispositivos móviles y '
                         'adaptado a las necesidades de los 25 médicos del Renticenter.')

    def test_sqlite_stranger_char(self):
        self.assertEqual(self.process_strings.translate(self.tests[12], 'es', 'de', 'yml', False),
                         '        title: Centroderentas "responde a una necesidad específica de la sociedad, es '
                         'práctico y fácil de usar, tiene un enorme potencial de crecimiento"')

    def test_little_brackets(self):
        self.assertEqual(self.process_strings.translate(self.tests[14], 'es', 'fr', 'yml', False),
                         'Las denominadas Cookies « Técnicas » (que se enumeran a continuación) cuya finalidad es')

    def test_mix_match_single_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[15], 'es', 'fr', 'yml', False),
                         self.tests[15])

    def test_mix_match_double_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[16], 'es', 'fr', 'yml', False),
                         self.tests[16])

    def test_trail_single_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[17], 'es', 'fr', 'yml', False),
                         self.tests[17])

    def test_trail_double_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[18], 'es', 'fr', 'yml', False),
                         self.tests[18])


if __name__ == '__main__':
    unittest.main()

'''

How to test:

nodemon --watch deeplTranslate_test.py --watch libs/process_strings.py --watch core/translate.py
--exec python deeplTranslate_test.py

'''

