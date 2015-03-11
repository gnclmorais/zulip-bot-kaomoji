# zulip-bot-kaomoji
Zulip bot to replace commands by kaomojis.  
Simply put, replaces messages like `@kao shrug` with `¯\_(ツ)_/¯`, for example.


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


## Zulip configuration
If you want to use the bot, you’ll have to send the bot your private API key.
As explained by Zulip:
> For most bots using the API, you'll want to give each bot its own name and 
> API key using the above section. But if you want to write a bot that can access 
> your own private messages, you should use your personal API key.

So follow these steps:

1. Open up Zulip and go to __Settings__
1. Scroll until the bottom and click on the button __Show/change your API key__
1. After inserting your password, copy that 32-character string
1. Send a __private message__ to `kawaii-bot@students.hackerschool.com`  
(it’s the e-mail address of the bot – its name is Kawaii, by the way)
1. And that’s it! You should receive a message from the bot telling you your
key was saved. You can now `@kao <kaomoji>` at will! (⌒ω⌒)


## Running
`make run` ＼(＾▽＾)／


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
    sad:          (╯︵╰,),
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
To use them, just write `@kao <one-of-the-above-kaomojis-keyword>`.
Example: `@kao hi` will be replaced by `(￣▽￣)ノ`.  
You can even have several kaomojis on a phrase, any place on it: 
`I hope this @kao dance doesn’t break…` gets replaced to
`I hope this ⌒(o＾▽＾o)ノ doesn’t break…`


## Credits
Thanks to (￣▽￣)ノ[@di0spyr0s](https://github.com/di0spyr0s) for the Python
base code that allowed me to jump-start the development of this bot.  
Shout-out to [@dariajung](https://twitter.com/djj2115) for finding out a way
to [edit Zulip’s messages]
(https://github.com/dariajung/zulip-gif-bot#notes-about-zulip-api). ⌒(o＾▽＾o)ノ  
Most of kaomoijs taken from [here](http://kaomoji.ru/en/). ノ( ^ _ ^ノ)
