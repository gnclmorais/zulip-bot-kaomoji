# zulip-bot-kaomoji
Zulip bot to replace commands by kaomojis.
Simply put, replaces messages like `/shrug` with `¯\_(ツ)_/¯`, for example.

## Instalation
To work on this bot, follow the following instructions to setup you environment:

1. `pip install virtualenv`
1. `virtualenv venv`
1. `source venv/bin/activate`
1. `pip install -r requirements.txt`

After you’re done working for the moment, don’t forget to `$ deactivate`.

## Configuration
To run this bot, don’t forget to create a `config.sh` file with the following
structure:
```
export ZULIP_USR=<your-bot-address>
export ZULIP_API=<your-bot-apy_key>
export ZULIP_PRIVATE_USR=<your-private-address>
export ZULIP_PRIVATE_API=<your-private-api-key>
```
After having such a file, don’t forget to load these variables, something
like `source config.sh`.

## Running
`python kaomoji.py` ＼(＾▽＾)／

## Available kaomojis
```
kaomojis = {
    yay:          ＼(＾▽＾)／,
    pleased:      (⌒‿⌒),
    dance:        ⌒(o＾▽＾o)ノ,
    inlove:       (─‿‿─)♡,
    sorry:        (⌒_⌒;),
    unamused:     (￣︿￣),
    seriously:    (￢_￢;),
    thenerve:     (╬ Ò﹏Ó),
    fliptable:    (╯°□°）╯︵ ┻━┻),
    fliptable2:   (ﾉಥ益ಥ）ﾉ﻿ ┻━┻,
    fliptable3:   (ノಠ益ಠ)ノ彡┻━┻,
    fliptables:   ┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻,
    unfliptable:  ┬─┬ノ( º _ ºノ),
    coldsweat:    (;;;*_*),
    cantlook:     (/ω＼),
    shrug:        ¯\_(ツ)_/¯,
    doubt:        (￢_￢),
    what:         (⊙_⊙),
    hi:           (￣▽￣)ノ,
    sup:          (・_・)ノ,
    zzz:          (－_－) zzZ,
    sing:         (￣▽￣)/♫•*¨*•.¸¸♪
}
```
To use them, just write `/k <one-of-the-above-kaomojis-keyword>`.
Example: `/k hi` will be replaced by `(￣▽￣)ノ`.

## Credits
Thanks to (￣▽￣)ノ[@di0spyr0s](https://github.com/di0spyr0s) for the Python
base code that allowed me to jump-start the development of this bot.
Most of kaomoijs taken from [here](http://kaomoji.ru/en/).
