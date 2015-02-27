# -*- coding: utf-8 -*-
import os
import zulip
import requests


class KaomojiBot():
    def __init__(self, zulip_usr, zulip_api, private_usr, private_api,
                 commands, kaomojis, subscribed_streams=[]):
        self.username = zulip_usr
        self.api_key = zulip_api
        self.private_username = private_usr
        self.private_api_key = private_api
        self.commands = map(lambda x: x.lower(), commands)
        self.kaomojis = kaomojis
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_usr, zulip_api)
        self.subscriptions = self.subscribe_to_streams()

    '''
    Standardizes a list of streams in the form [{'name': stream}]
    '''
    @property
    def streams(self):
        if not self.subscribed_streams:
            streams = [{'name': stream['name']} for stream
                       in self.get_all_zulip_streams()]
            return streams
        else:
            streams = [{'name': stream} for stream
                       in self.subscribed_streams]
            return streams

    '''
    Call Zulip API to get a list of all streams
    '''
    def get_all_zulip_streams(self):
        response = requests.get(
            'https://api.zulip.com/v1/streams',
            auth=(self.username, self.api_key)
        )
        if response.status_code == 200:
            return response.json()['streams']
        elif response.status_code == 401:
            raise RuntimeError('check yo auth')
        else:
            raise RuntimeError(':( we failed to GET streams.\n(%s)' % response)

    '''
    Subscribes to zulip streams
    '''
    def subscribe_to_streams(self):
        self.client.add_subscriptions(self.streams)

    '''
    Checks msg against keywords. If keywords is in msg, gets a gif url,
    picks a caption, and calls send_message()
    '''
    def respond(self, msg):
        # Proceed only if we have 1 command and at least 1 kaomoji keyword.
        content = msg['content'].lower().strip().split(' ')
        if len(content) < 2:
            return

        # Remove the head (command) and leave the kaomojis on the list
        command = content.pop(0)

        # If a valid command is found, search for the equivalent kaomoji
        # with each keyword provided. If matches are found, send the message.
        if any(command in c for c in self.commands):
            new_msg = []
            for keyword in content:
                if keyword in self.kaomojis:
                    new_msg.append(kaomojis[keyword])
            if len(new_msg):
                self.send_message(msg, " ".join(new_msg))

    '''
    Sends a message to zulip stream
    '''
    def send_message(self, msg, new_msg):
        self.edit_message(msg, new_msg)

    '''
    Replaces an old message with a new message.
    '''
    def edit_message(self, old, new):
        payload = {'message_id': old['id'],
                   'content': new}
        url = "https://api.zulip.com/v1/messages"
        requests.patch(url, data=payload,
                       auth=requests.auth.HTTPBasicAuth(self.private_username,
                                                        self.private_api_key))

    '''
    Blocking call that runs forever.
    Calls self.respond() on every message received.
    '''
    def main(self):
        self.client.call_on_each_message(lambda msg: self.respond(msg))


'''
Zulip credentials:
'''
zulip_usr = os.environ['ZULIP_USR']
zulip_api = os.environ['ZULIP_API']
private_usr = os.environ['ZULIP_PRIVATE_USR']
private_api = os.environ['ZULIP_PRIVATE_API']
'''
Recognised commands:
'''
commands = [
    '/k',
    '/kaomoji'
]
'''
Available kaomojis:
'''
kaomojis = {
    # Happy status:
    'yay': '＼(＾▽＾)／',
    'pleased': '(⌒‿⌒)',
    'dance': '⌒(o＾▽＾o)ノ',
    # Love status:
    'inlove': '(─‿‿─)♡',
    # Embarassed status:
    'sorry': '(⌒_⌒;)',
    # Dissatisfaction stauts:
    'unamused': '(￣︿￣)',
    'seriously': '(￢_￢;)',
    # Angry status:
    'thenerve': '(╬ Ò﹏Ó)',
    'fliptable': '(╯°□°）╯︵ ┻━┻)',
    'fliptable2': '(ﾉಥ益ಥ）ﾉ﻿ ┻━┻',
    'fliptable3': '(ノಠ益ಠ)ノ彡┻━┻',
    'fliptables': '┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻',
    # Serene status
    'unfliptable': '┬─┬ノ( º _ ºノ)',
    # Fear status:
    'coldsweat': '(;;;*_*)',
    'cantlook': '(/ω＼)',
    # Indifference status:
    'shrug': '¯\_(ツ)_/¯',
    # Doubting status:
    'doubt': '(￢_￢)',
    # Surprise status:
    'what': '(⊙_⊙)',
    # Greetings:
    'hi': '(￣▽￣)ノ',
    'sup': '(・_・)ノ',
    # Sleeping
    'zzz': '(－_－) zzZ',
    # Music
    'sing': '(￣▽￣)/♫•*¨*•.¸¸♪'
}

subscribed_streams = []
new_bot = KaomojiBot(zulip_usr, zulip_api, private_usr, private_api,
                     commands, kaomojis)
new_bot.main()
