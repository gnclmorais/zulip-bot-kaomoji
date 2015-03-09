# -*- coding: utf-8 -*-
import os
import re
import zulip
import json
import requests
import psycopg2
import urlparse

import pprint


class KaomojiBot():
    def __init__(self, zulip_usr, zulip_api, private_usr, private_api,
                 command, help, kaomojis, subscribed_streams=[]):
        self.api_key_size = 32
        self.table = 'keys'
        self.remove_commands = [
            'delete',
            'remove',
            'exit',
            'stop']

        self.connect('postgres://hvctpbozzdoxdy:sI6zqEvx_MEENyRfikUcquZYQg@ec2-23-21-183-70.compute-1.amazonaws.com:5432/ddn7lbp8frv36f')

        self.username = zulip_usr
        self.api_key = zulip_api
        self.private_username = private_usr
        self.private_api_key = private_api
        self.command = command.lower()
        self.help = help.lower()
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

        # Check if it’s a private message;
        # If so, it’s probably someont sending us an e-mail address and API key
        if msg['type'] == 'private':
            self._handle_pm(msg)
            return

        # Proceed only if we find an instance of the command and there is
        # a following keywork (that hopefully corresponds to a kaomoji).
        content = msg['content'].strip().encode('utf-8')

        # Check if the message is a cry for help
        if content == self.help:
            self.send_help(msg)
            return

        # Right, no help command, so check if other commands are found
        content = content.split(' ')
        index = content.index(self.command) if self.command in content else -1
        if index == -1 or len(content) <= index + 1:
            return

        # Start buidling the new message and
        # get the list of possible keywords (words after command).
        new_msg = content[0:index]
        content = content[index + 1:]

        # If a valid command is found, search for the equivalent kaomoji
        # with each keyword provided. If matches are found, send the message.
        for keyword in content:
            lower = keyword = keyword.lower()
            if lower in self.kaomojis:
                new_msg.append(kaomojis[lower])
            else:
                new_msg.append(keyword)  # Not a keyword, so put it back
        if len(new_msg):
            self.send_message(msg, " ".join(new_msg))

    def _handle_pm(self, msg):
        address = msg['sender_email']
        command = msg['content'].split(' ')

        # Just 2 arguments: cool
        # More than 2 args: too much info, warn the user
        # Less than 2 args: ¯\_(ツ)_/¯
        if len(command) == 1:
            command = str(command[0])
            # if len(cmnd) == self.api_key_size and re.match('^\w+$', cmnd):
            #     self._user_store(mail, cmnd)
            # elif cmnd in self.remove_commands:
            #     self._user_remove(mail)
            # else:
            #     self.send_private_message(mail,
            #                               'Error! Please review your command.')

            print('Printing:')
            print(self.db_search(command))
        else:
            # TODO Send message to that e-mail asking for more info
            self.send_private_message(address, 'Error! Way too many arguments…')

    '''
    Stores a pair (key, value),
    where the `key` is the user’s e-mail and `value` is the API key
    '''
    def _user_store(self, address, api_key):
        ## TODO Check if this `address` already has something saved
        self.db_insert(address, api_key)
        msg = 'Successfuly stored {0}'.format(api_key)
        self.send_private_message(address, msg)

    def _user_remove(self, address):
        ## TODO Check if this `address` already has something saved
        self.db_remove(address)

    '''
    Sends available commands
    '''
    def send_help(self, msg):
        self.edit_message(msg, "")  # Delete message

        to = msg['sender_email']
        text = """```
Example usage: """ + command + """ <keyword>

Available keywords & correspondent kaomojis:
""" + json.dumps(self.kaomojis, indent=4, ensure_ascii=False) + """
```"""

        self.send_private_message(to, text)

    '''
    Sends a message to zulip stream
    '''
    def send_message(self, msg, new_msg):
        self.edit_message(msg, new_msg)

    '''
    Sends a private message
    '''
    def send_private_message(self, to, msg):
        self.client.send_message({
            "type": "private",
            "to": to,
            "content": msg
        })

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
    Connect to database
    '''
    def connect(self, database_url):
        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(database_url)

        try:
            self.conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port)
            self.cur = self.conn.cursor()
        except:
            print "I am unable to connect to the database"

    def db_search(self, mail):
        query = """SELECT email, api_key
                   FROM {0}
                   WHERE email = \'{1}\';""".format(self.table, mail)
        return self._db_execute_query(query)

    def db_insert(self, mail, key):
        query = """INSERT INTO {0} (email, api_key)
                   VALUES (\'{1}\', \'{2}\')""".format(self.table, mail, key)
        return self._db_execute_query(query)

    def db_update(self, mail, key):
        query = """UPDATE {0}
                   SET api_key = \'{1}\'
                   WHERE email = \'{2}\'""".format(self.table, key, mail)
        return self._db_execute_query(query)

    def db_remove(self, mail):
        query = """DELETE FROM {0}
                   WHERE email = \'{1}\'""".format(self.table, mail)
        return self._db_execute_query(query)

    def _db_execute_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

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
database_url = os.environ['DATABASE_URL']
'''
Recognised command:
'''
command = '@kao'
help = command + " help"
'''
Available kaomojis:
'''
kaomojis = {
    # Happy
    'yay': '＼(＾▽＾)／',
    'pleased': '(⌒‿⌒)',
    'dance': '⌒(o＾▽＾o)ノ',
    # Love
    'inlove': '(─‿‿─)♡',
    # Embarassed
    'sorry': '(⌒_⌒;)',
    # Dissatisfaction
    'unamused': '(￣︿￣)',
    'seriously': '(￢_￢;)',
    # Angry
    'thenerve': '(╬ Ò﹏Ó)',
    'fliptable': '(╯°□°）╯︵ ┻━┻)',
    'fliptable2': '(ﾉಥ益ಥ）ﾉ﻿ ┻━┻',
    'fliptable3': '(ノಠ益ಠ)ノ彡┻━┻',
    'fliptables': '┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻',
    # Serene
    'unfliptable': '┬─┬ノ( º _ ºノ)',
    # Sad
    'sad': '(╯︵╰,)',
    # Fear
    'coldsweat': '(;;;*_*)',
    'cantlook': '(/ω＼)',
    # Indifference
    'shrug': '¯\_(ツ)_/¯',
    # Doubting
    'doubt': '(￢_￢)',
    # Surprise
    'what': '(⊙_⊙)',
    # Greetings
    'hi': '(￣▽￣)ノ',
    'sup': '(・_・)ノ',
    # Sleeping
    'zzz': '(－_－) zzZ',
    # Music
    'sing': '(￣▽￣)/♫•*¨*•.¸¸♪'
}

subscribed_streams = []
new_bot = KaomojiBot(zulip_usr, zulip_api, private_usr, private_api,
                     command, help, kaomojis)
new_bot.main()
