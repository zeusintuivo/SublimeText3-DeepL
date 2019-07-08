Sublime Text Deepl Translate Plugin
===============================

For SublimeText 3, support proxy `PROXY_TYPE_SOCKS5` `PROXY_TYPE_SOCKS4` `PROXY_TYPE_HTTP`

**Version:** 1.0.0

------------------

Install:
=======

**[Recommend] Package Control:** [Usage](https://sublime.wbond.net/docs/usage),
 `Package Control: Install Package` then search `SublimeText3-DeepL`

**Without Git:** Download the latest source from 
[GitHub](https://github.com/zeusintuivo/SublimeText3-DeepL) and copy the 
SublimeText3-DeepL folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory:

    git clone https://github.com/zeusintuivo/SublimeText3-DeepL 'SublimeText3-DeepL'

Folder name must be **SublimeText3-DeepL** !!

The "Packages" directory is located at:

* OS X:

        ST3: ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/

* Linux:

        ST3: ~/.config/sublime-text-3/Packages/

* Windows:

        ST3: %APPDATA%/Sublime\ Text\ 3/Packages/

Configure:
=========

Set Target Language AND Source Language [default is auto detect] in user settings:


    {
        "source_language": "", // eg. en, default is 'auto detect'
        "target_language": "", // default is en
        "keep_moving_down": "yes",  // or yes or no Will keep translating down the line
        "target_type": "html",  // or plain or html or yml
        "proxy_enable": "yes",  // enable or disable proxy
        "proxy_type": "socks5", // socks4 or socks5 or http
        "proxy_host": "127.0.0.1",  // eg. 127.0.0.1
        "proxy_port": "9050"    // eg. 9050
    }


Usage:
=====

Select text:

* press `ctrl+alt+g` or select `Deepl Translate selected text` in context menu

Tips:
====

Overview your language code:

* press `Deepl Translate Print the available translate variants` in context menu
* press `ctrl + ~` to see output errors in console


Credits:
=======

* [PySocks](https://github.com/Anorov/PySocks)
* [MTimer](https://github.com/MTimer/)
* [MTimerCMS](https://github.com/MtimerCMS/)


License:
=======

MIT



------------------

