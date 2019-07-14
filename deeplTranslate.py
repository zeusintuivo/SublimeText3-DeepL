# -*- coding: utf-8 -*-
# author:zeusintuivo
# https://github.com/zeusintuivo/SublimeText3-DeepL

import sublime
import sublime_plugin

import inspect

from sublime_plugin import application_command_classes
from sublime_plugin import window_command_classes
from sublime_plugin import text_command_classes

import time
import re
import json

if sublime.version() < '3':
    from core.translate import *
    from libs.process_strings import *
else:
    from .core.translate import *
    from .libs.process_strings import *


class DeeplTranslateCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        global settings
        translate = DeeplTranslate(settings)
        process_strings = ProcessStrings(translate.callback)

        v = self.view
        window = v.window()

        # Get the current cursor position in the file
        caret = v.sel()[0].begin()

        # Get the new current line number
        cur_line = self.line_at(caret)

        # Get the count of lines in the buffer so we know when to stop
        last_line = self.line_at(v.size())

        keep_moving = True

        sublime.log_commands(False)
        sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
        sublime.active_window().run_command("reveal_in_side_bar", {"event": {"x": 505.296875, "y": 111.76171875}})
        v.run_command("show_panel", {"panel": "console", "toggle": True})
        v.run_command("reveal_in_side_bar", {"event": {"x": 505.296875, "y": 111.76171875}})

        # REF:
        # https://stackoverflow.com/questions/44578315/making-a-sublime-text-3-macro-to-evaluate-a-line-and-then-move-the-cursor-to-the
        # A regex that matches a line that's blank or contains a comment.
        # Adjust as needed
        _r_blank = re.compile("^\s*(#.*)?$")

        looping = 0
        while keep_moving:
            print('-------SublimeText3-DeepL-----:', '------------')
            for region in v.sel():

                whole_line = False
                if not region.empty():
                    selection = v.substr(region)
                    coordinates = v.sel()
                    keep_moving = False
                else:
                    selection = v.substr(v.line(v.sel()[0]))
                    coordinates = v.line(v.sel()[0])
                    whole_line = True

                if selection:
                    largo = len(selection)
                    print('line(' + str(cur_line + 1) + ') length(' + str(largo) + ') selection(' + selection + ')')

                    selection = selection.encode('utf-8')

                    if not settings.get("target_language"):
                        v.run_command("deepl_translate_to")
                        keep_moving = False
                        return
                    else:
                        try:
                            # looping = looping + 1
                            if looping > 500:
                                print('exiting 501 process here. ... last line processed(' + str(cur_line + 1) + ')')
                                v.run_command('save')
                                sublime.active_window().run_command('save')
                                keep_moving = False
                                raise DeeplTranslateException(translate.error_codes[401])

                            result = process_strings.translate(
                                selection,
                                translate.target,
                                translate.source,
                                translate.target_type,
                                False
                            )
                            time.sleep(0.15)

                        except:
                            # REF:
                            # https://github.com/Enteleform/-SCRIPTS-/blob/master/SublimeText/%5BMisc%5D/%5BProof%20Of%20Concept%5D%20Progress%20Bar/ProgressBarDemo/ProgressBarDemo.py
                            print('')
                            message = 'ERR: LINE:' + str(cur_line + 1) + ' translation service failed.'
                            print(message)
                            print('')
                            sublime.status_message(u'' + message)
                            self.view.window().show_quick_panel(
                                ["Translate", "Error", message], "", 1, 2)
                            keep_moving = False
                            return
                    # DEBUG print('edit')
                    # DEBUG pprint(edit)

                    # DEBUG print('coordinates')
                    # DEBUG pprint(coordinates)

                    # DEBUG print('result')
                    # DEBUG pprint(result)

                    if not whole_line:
                        v.replace(edit, region, result)
                    else:
                        v.replace(edit, coordinates, result)

                    window.focus_view(v)
                    if not settings.get('source_language'):
                        detected = 'auto'
                    else:
                        detected = settings.get('source_language')
                    sublime.status_message(
                        u'Done! (translate ' + detected + ' --> ' + settings.get("target_language") + ')')
                else:
                    sublime.status_message(u'Nothing to translate!')
                    print('Nothing to translate!')
                    # DEBUG print('selection(' + selection + ')' )

            if settings.get('keep_moving_down') == 'no':
                keep_moving = False

            looping = looping + 1
            if looping > 500:
                print('exiting 500 process here.... last line processed(' + str(cur_line + 1) + ')')
                v.run_command('save')
                sublime.active_window().run_command('save')
                keep_moving = False

            if keep_moving:
                # Move to the next line
                v.run_command("move", {"by": "lines", "forward": True})
                time.sleep(0.15)
                sublime.status_message(u'moved down.')
                print('moved down.')

                # Get the current cursor position in the file
                caret = v.sel()[0].begin()

                # Get the new current line number
                cur_line = self.line_at(caret)

                percent = (cur_line * 100) / last_line
                sublime.status_message('%03.2f %%' % percent)

                # Get the contents of the current line
                # content = v.substr(v.line(caret))
                # selection = v.substr(v.line(v.sel()[0]))
                # largo = len(selection.strip())

                # If the current line is the last line, or the contents of
                # the current line does not match the regex, break out now.
                if cur_line == last_line:  # or largo == 0:  # not _r_blank.match(selection):
                    print('cur_line(' + str(cur_line) + ') == last_line(' + str(last_line) + ')')
                    # print('selection.len(' + str(largo) + ')')
                    v.run_command('save')
                    sublime.active_window().run_command('save')
                    print('saving and exiting translation process here.')
                    keep_moving = False

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

    # Convert a 0 based offset into the file into a 0 based line in
    # the file.
    def line_at(self, point):
        return self.view.rowcol(point)[0]


class DeeplTranslateInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global settings

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = DeeplTranslate(settings)

        text = (json.dumps(translate.languages, ensure_ascii=False, indent=2))

        v.replace(edit, v.sel()[0], text)


class DeeplTranslateToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global settings

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = DeeplTranslate(settings)

        text = (json.dumps(translate.languages['languages'], ensure_ascii=False))
        continents = json.loads(text)
        lkey = []
        ltrasl = []

        for (slug, title) in continents.items():
            lkey.append(slug)
            ltrasl.append(title + ' [' + slug + ']')

        def on_done(index):
            if index >= 0:
                self.view.run_command("deepl_translate", {"target_language": lkey[index]})

        self.view.window().show_quick_panel(ltrasl, on_done)

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False


class DeeplTranslateShowCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.view = self.window.new_file()
        self.view.set_scratch(True)
        self.view.set_name("Command List")

        self.list_category("Application Commands", application_command_classes)
        self.list_category("Window Commands", window_command_classes)
        self.list_category("Text Commands", text_command_classes)

    def append(self, line):
        self.view.run_command("append", {"characters": line + "\n"})

    def list_category(self, title, command_list):
        self.append(title)
        self.append(len(title) * "=")

        for command in command_list:
            self.append("{cmd} {args}".format(
                cmd=self.get_name(command),
                args=str(inspect.signature(command.run))))

        self.append("")

    def get_name(self, cls):
        clsname = cls.__name__
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_command"):
            name = name[0:-8]
        return name


def plugin_loaded():
    global settings
    settings = sublime.load_settings("deeplTranslate.sublime-settings")
    sublime.log_commands(False)
    sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
    print('DeepL auth_key loaded:', settings.get('auth_key'))
    print('DeepL Translating From:', settings.get('source_language'), ' To:', settings.get('target_language'))
    print('DeepL Keep Moving Down the line?', settings.get('keep_moving_down'))
