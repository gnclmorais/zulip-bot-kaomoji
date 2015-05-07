# -*- coding: utf-8 -*-
import json
import os
import re
import textwrap
import urlparse

import psycopg2
import requests
import zulip


class KaomojiBot():
    # Recognised command:
    command = '@kao'
    help = command + ' help'

    # Available kaomojis:
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

    # Private commands
    remove_commands = ['delete',
                       'remove',
                       'exit',
                       'stop']
    kaos = json.dumps(kaomojis, indent=4, ensure_ascii=False)
    help_api = textwrap.dedent('''
        Set me up & manage your private API key:
        * Send me your API key so I can edit your comments and include \
        awesome kaomojis! (*^ω^)
        * Send me `info` to check if I have your API key or not. (^_~)
        * Send me one of the following commands to delete your information \
        from my database: `{0}` ┐(￣ヘ￣;)┌
        * Send me the text `help` to see this message. (⌒_⌒;)

        Example usage on a stream: `{1} <keyword>`
        Available keywords & correspondent kaomojis:
        ```
        {2}
        ```''').format('`, `'.join(remove_commands), command, kaos)

    # Database-related information
    db_api_key_size = 32
    db_table_name = 'keys'

    def enum(**named_values):
        ''' Enum to define bot’s messages.
        '''
        return type('Enum', (), named_values)
    Messages = enum(
        ADD_SUCCESS='red',
        UPDATE_SUCCESS='green',
        REMOVE_SUCCESS='Your API key was successfuly removed! ＼(≧▽≦)／',
        INFO_FOUND='''I have your data! Send me one of the following commands to remote it:
            `{0}` (◕‿◕)'''.format('`, `'.join(remove_commands)),
        INFO_NOT_FOUND='I don’t have your data, so rest assure. (-‿‿-)',
        IDK='I have no idea what you mean. ¯\_(ツ)_/¯')

    def __init__(self, zulip_usr, zulip_api, private_usr, private_api,
                 database_url, subscribed_streams=[]):
        self.username = zulip_usr
        self.api_key = zulip_api
        self.private_username = private_usr
        self.private_api_key = private_api
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_usr, zulip_api)
        self.subscriptions = self.subscribe_to_streams()

        self.db_url = database_url
        self._connect(self.db_url)

    def __del__(self):
        self.cur.close()
        self.conn.close()

    @property
    def streams(self):
        "Standardizes a list of streams in the form [{'name': stream}]"
        if not self.subscribed_streams:
            streams = [{'name': stream['name']} for stream
                       in self.get_all_zulip_streams()]
            return streams
        else:
            streams = [{'name': stream} for stream
                       in self.subscribed_streams]
            return streams

    def _connect(self, database_url):
        "Connect to database"
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
            print 'I am unable to connect to the database'

    def get_all_zulip_streams(self):
        "Call Zulip API to get a list of all streams"
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

    def subscribe_to_streams(self):
        "Subscribes to zulip streams"
        self.client.add_subscriptions(self.streams)

    def respond(self, msg):
        "Respondes to messages sent to it"
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
                new_msg.append(self.kaomojis[lower])
            else:
                new_msg.append(keyword)  # Not a keyword, so put it back
        if len(new_msg):
            self.send_message(msg, ' '.join(new_msg))

    def _handle_pm(self, msg):
        mail = msg['sender_email']
        data = msg['content'].split(' ')

        # Just 2 arguments: cool
        # More than 2 args: too much info, warn the user
        # Less than 2 args: ¯\_(ツ)_/¯
        if len(data) == 1:
            data = str(data[0])
            if len(data) == self.db_api_key_size and re.match('^\w+$', data):
                if self.db_search(mail):
                    self._user_update(mail, data)
                else:
                    self._user_store(mail, data)
            elif data in self.remove_commands:
                if self.db_search(mail):
                    self._user_remove(mail)
                else:
                    msg = self.Messages.INFO_NOT_FOUND
                    self.send_private_message(mail, msg)
            elif data == 'info':
                self._user_enquiry(mail)
            elif data == 'help':
                self.send_private_message(mail, self.help_api)
            else:
                self._show_help(mail)
        else:
            self._show_help(mail)

    def _show_help(self, mail):
        self.send_private_message(mail, self.Messages.IDK)

    def _user_store(self, address, api_key):
        '''Stores a pair (key, value),

        where the `key` is the user’s e-mail and `value` is the API key
        '''
        self.db_insert(address, api_key)
        msg = 'Successfuly stored {0}'.format(api_key)
        self.send_private_message(address, msg)

    def _user_update(self, address, api_key):
        self.db_update(address, api_key)
        msg = 'API key for {0} successfuly updated.'.format(address)
        self.send_private_message(address, msg)

    def _user_enquiry(self, address):
        if self.db_search(address):
            msg = self.Messages.INFO_FOUND
        else:
            msg = self.Messages.INFO_NOT_FOUND
        self.send_private_message(address, msg)

    def _user_remove(self, address):
        self.db_remove(address)
        msg = self.Messages.REMOVE_SUCCESS
        self.send_private_message(address, msg)

    def send_help(self, msg):
        '''Sends available commands'''
        to = msg['sender_email']
        self.send_private_message(to, self.help_api)

    def send_message(self, msg, new_msg):
        '''Sends a message to zulip stream'''
        self.edit_message(msg, new_msg)

    def send_private_message(self, to, msg):
        '''Sends a private message'''
        self.client.send_message({
            "type": "private",
            "to": to,
            "content": msg
        })

    def edit_message(self, old, new):
        '''Replaces an old message with a new message.'''
        address = old['sender_email']
        credentials = self.db_search(address)

        if not credentials:
            self.send_private_message(address, self.Messages.SETUP)
            return

        (address, api_key) = credentials
        payload = {'message_id': old['id'],
                   'content': new}
        url = "https://api.zulip.com/v1/messages"
        requests.patch(url,
                       data=payload,
                       auth=requests.auth.HTTPBasicAuth(address, api_key))

    def db_search(self, mail):
        query = """SELECT email, api_key
                   FROM {0}
                   WHERE email = %s;""".format(self.db_table_name)
        self._db_execute_query(query, (mail,))
        return self.cur.fetchone()

    def db_insert(self, mail, key):
        query = """INSERT INTO {0} (email, api_key)
                   VALUES (%s, %s);""".format(self.db_table_name)
        return self._db_execute_query(query, (mail, key))

    def db_update(self, mail, key):
        query = """UPDATE {0}
                   SET api_key = %s
                   WHERE email = %s;""".format(self.db_table_name)
        return self._db_execute_query(query, (key, mail))

    def db_remove(self, mail):
        query = """DELETE FROM {0}
                   WHERE email = %s;""".format(self.db_table_name)
        return self._db_execute_query(query, (mail,))

    def _db_execute_query(self, query, values):
        result = self.cur.execute(query, values)
        self.conn.commit()
        return result

    def main(self):
        ''' Blocking call that runs forever.

        Calls self.respond() on every message received.
        '''
        self.client.call_on_each_message(lambda msg: self.respond(msg))


if __name__ == "__main__":
    zulip_usr = os.environ['ZULIP_USR']
    zulip_api = os.environ['ZULIP_API']
    private_usr = os.environ['ZULIP_PRIVATE_USR']
    private_api = os.environ['ZULIP_PRIVATE_API']
    database_url = os.environ['DATABASE_URL']

    subscribed_streams = []
    new_bot = KaomojiBot(zulip_usr, zulip_api, private_usr, private_api,
                         database_url)
    new_bot.main()
