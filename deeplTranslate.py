# -*- coding: utf-8 -*-
# author:zeusintuivo
# https://github.com/zeusintuivo/SublimeText3-DeepL

import sublime
import sublime_plugin

import inspect

from sublime_plugin import application_command_classes
from sublime_plugin import window_command_classes
from sublime_plugin import text_command_classes

import json
import re
import time
from pprint import pprint
if sublime.version() < '3':
    from core.translate import *
else:
    from .core.translate import *

settings = sublime.load_settings("deeplTranslate.sublime-settings")


class DeeplTranslateCommand(sublime_plugin.TextCommand):

    def run(self, edit,
            proxy_enable=settings.get("proxy_enable"),
            proxy_type=settings.get("proxy_type"),
            proxy_host=settings.get("proxy_host"),
            proxy_port=settings.get("proxy_port"),
            s_lang=settings.get("source_language"),
            t_lang=settings.get("target_language")):

        if not s_lang:
            s_lang = settings.get("source_language")
        if not t_lang:
            t_lang = settings.get("target_language")
        if not proxy_enable:
            proxy_enable = settings.get("proxy_enable")
        if not proxy_type:
            proxy_type = settings.get("proxy_type")
        if not proxy_host:
            proxy_host = settings.get("proxy_host")
        if not proxy_port:
            proxy_port = settings.get("proxy_port")
        target_type = settings.get("target_type")
        effectuate_keep_moving = settings.get("keep_moving_down")

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

                    # if largo > 256:
                    #    print('')
                    #    message = 'ERR:' + str(cur_line + 1) + ' line longer than 256 chars, consider split or short.'
                    #    print(message)
                    #    print('')
                    #    sublime.status_message(u'ERR:' + str(cur_line + 1) + ' line too Long (' + selection + ')')
                    #    self.view.window().show_quick_panel(
                    #        ["Translate", "Error", message + " \n line(" + str(cur_line + 1) + ') length(' + str(
                    #            largo) + ') selection(' + selection + ')'], "", 1, 2)
                    #    keep_moving = False
                    #    return

                    selection = selection.encode('utf-8')

                    translate = DeeplTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, s_lang, t_lang)

                    if not t_lang:
                        v.run_command("deepl_translate_to")
                        keep_moving = False
                        return
                    else:
                        try:
                            result = translate.translate(selection, t_lang, s_lang, target_type)
                            time.sleep(0.15)
                            looping = looping + 1
                            if looping > 201:
                                print('exiting 201 process here. ... last line processed(' + str(cur_line + 1))
                                v.run_command('save')
                                sublime.active_window().run_command('save')
                                keep_moving = False
                                raise DeeplTranslateException(translate.error_codes[401])

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
                    if not s_lang:
                        detected = 'auto'
                    else:
                        detected = s_lang
                    sublime.status_message(u'Done! (translate ' + detected + ' --> ' + t_lang + ')')
                else:
                    sublime.status_message(u'Nothing to translate!')
                    print('Nothing to translate!')
                    # DEBUG print('selection(' + selection + ')' )

            if effectuate_keep_moving == 'no':
                keep_moving = False

            looping = looping + 1
            if looping > 200:
                print('exiting 200 process here.... last line processed(' + str(cur_line + 1))
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
                    # print('cur_line(' + str(cur_line) + ') == last_line(' + str(last_line) + ')')
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
        # settings = sublime.load_settings("deeplTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        proxy_enable = settings.get("proxy_enable")
        proxy_type = settings.get("proxy_type")
        proxy_host = settings.get("proxy_host")
        proxy_port = settings.get("proxy_port")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = DeeplTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, source_language, target_language)

        text = (json.dumps(translate.languages, ensure_ascii=False, indent=2))

        v.replace(edit, v.sel()[0], text)


class DeeplTranslateToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global settings
        # settings = sublime.load_settings("deeplTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        proxy_enable = settings.get("proxy_enable")
        proxy_type = settings.get("proxy_type")
        proxy_host = settings.get("proxy_host")
        proxy_port = settings.get("proxy_port")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = DeeplTranslate(proxy_enable, proxy_type, proxy_host, proxy_port, source_language, target_language)

        text = (json.dumps(translate.languages['languages'], ensure_ascii=False))
        continents = json.loads(text)
        lkey = []
        ltrasl = []

        for (slug, title) in continents.items():
            lkey.append(slug)
            ltrasl.append(title+' ['+slug+']')

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
