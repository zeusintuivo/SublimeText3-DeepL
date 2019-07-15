#!/usr/bin/python
# coding:utf-8
# https://github.com/zeusintuivo/SublimeText3-DeepL
from process_strings import ProcessStrings
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
                "%{count_rdv}<br/> <span class=\"question\">Wie wollen Sie fortfahren?</span>",

             9: '                    on_same_day: Sie haben soeben am %{date} von %{start_time} bis',
             10: 'Sie haben soeben am',
             11: '        title: Centroderentas “responds to a specific need of society, it is practical and',
             12: '        title: Centroderentas “responds to a specific need of society, it is practical and '
                 'user-friendly, has an enormous amount of growth potential"',
             13: '          müssen Sie alle kommenden Termine in Ihrem Konto stornieren.\n"',
             14: 'Vous vous exposez, ce faisant, à une forte dégradation de l’expérience utilisateur',
             15: "   key_something_here: ''",
             16: '   key_something_here: ""',
             17: "      # html: '<abbr title=\"required\">*</abbr>'"
             }

    process_strings = ProcessStrings()

    def test_enters(self):
        self.assertEqual(self.process_strings.translate(self.tests[1], 'es', 'de', 'yml', True),
                         '          Cual es tu decision?\n\n"')

    def test_enters_double(self):
        self.assertEqual(self.process_strings.translate(self.tests[2], 'es', 'de', 'yml', True),
                         '          Cual es tu decision?\\n\\n"')

    def test_tag_quote(self):
        self.assertEqual(self.process_strings.translate(self.tests[3], 'es', 'de', 'yml', True),
                         '<strong class="do-not-translate-this">Es una cita</strong>durante esta ausencia.')

    def test_key_quote_tag(self):
        self.assertEqual(self.process_strings.translate(self.tests[4], 'es', 'de', 'yml', True),
                         '              warning_html: \'Usted acaba de ver %{date} %{recurring} ha registrado una '
                         'ausencia.<br/> %{count_rdv}<br/> <span class="question">¿Cómo piensa proceder?</span>\'')

    def test_one_single_quote(self):
        self.assertEqual(self.process_strings.translate(self.tests[5], 'es', 'de', 'yml', True),
                         "'")

    def test_one_double_quote(self):
        self.assertEqual(self.process_strings.translate('"', 'es', 'de', 'yml', True), '"')

    def test_key_tag_var(self):
        self.assertEqual(self.process_strings.translate(self.tests[6], 'es', 'de', 'yml', True),
                         '  warning_html: \'Usted acaba de ver %{date} %{recurring} una auscencia inscrito.<br/> %{count_rdv}'
                         '<br/> <span class="question">¿Cómo piensa proceder?</span>')

    def test_one_line_complex(self):
        self.assertEqual(self.process_strings.translate(self.tests[7], 'es', 'de', 'yml', True),
                         '                está registrado.<br/> %{count_rdv}<br/> <span class="question">'
                         '¿Cómo piensa proceder?</span>')

    def test_one_line_complex_2(self):
        self.assertEqual(self.process_strings.translate(self.tests[8], 'es', 'de', 'yml', True),
                         '  warning_html: \'Usted acaba de ver %{date} %{recurring} una auscencia inscrito.<br/> '
                         '%{count_rdv}<br/> <span class="question">¿Cómo piensa proceder?</span>')

    def test_one_line_now_what(self):
        self.assertEqual(self.process_strings.translate(self.tests[9], 'es', 'de', 'yml', True),
                         '                    on_same_day: Acabas de llegar al %{date} antes de %{start_time} '
                         'para cuando')

    def test_sqlite_response(self):
        self.assertEqual(self.process_strings.translate(self.tests[10], 'es', 'de', 'yml', True),
                         'Acabas de llegar al')

    def test_sqlite_stranger_char(self):
        self.assertEqual(self.process_strings.translate(self.tests[11], 'es', 'de', 'yml', True),
                         '        title: translated(Centroderentas \xe2\x80\x9cresponds to a specific need of '
                         'society), translated(it is practical and)')

    def test_sqlite_stranger_char(self):
        self.assertEqual(self.process_strings.translate(self.tests[12], 'es', 'de', 'yml', True),
                         '        title: Centroderentas "responde a una necesidad específica de la sociedad, '
                         'es práctico y fácil de usar, tiene un enorme potencial de crecimiento"')

    def test_cuote_at_the_end(self):
        self.assertEqual(self.process_strings.translate(self.tests[13], 'es', 'de', 'yml', True),
                         '          usted debe cancelar todas las próximas citas en su cuenta.\n"')

    def test_comma_separation(self):
        self.assertEqual(self.process_strings.translate(self.tests[14], 'es', 'fr', 'yml', True),
                         'Usted se está exponiendo a, de este modo, un deterioro significativo de la '
                         'experiencia del usuario')

    def test_alone_single_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[15], 'es', 'fr', 'yml', True),
                         self.tests[15])

    def test_alone_single_double_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[16], 'es', 'fr', 'yml', True),
                         self.tests[16])

    def test_alone_single_double_quotes(self):
        self.assertEqual(self.process_strings.translate(self.tests[17], 'es', 'fr', 'yml', True),
                         self.tests[17])

    def test_trail_single_quotes(self):
        self.assertEqual(self.process_strings.translate("# html: '", 'es', 'fr', 'yml', True),
                         "# html: '")

    def test_trail_double_quotes(self):
        self.assertEqual(self.process_strings.translate('# html: "', 'es', 'fr', 'yml', True),
                         '# html: "')


if __name__ == '__main__':
    unittest.main()

#
# How to test:
#
# nodemon --watch process_strings_test.py --exec python process_strings_test.py
#
# nodemon --watch libs/process_strings_test.py --exec python libs/process_strings_test.py
#
