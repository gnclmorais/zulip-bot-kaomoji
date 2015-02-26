# -*- coding: utf-8 -*-
import zulip
import requests
import random


class KaomojiBot():
    '''
    bot takes a zulip username and api key, a word or phrase to respond to,
    a search string for giphy, an optional caption or list of captions,
    and a list of the zulip streams it should be active in.
    it then posts a caption and a randomly selected gif in response to
    zulip messages.
    '''
    def __init__(self, zulip_username, zulip_api_key, commands, kaomojis,
                 subscribed_streams=[]):
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.commands = map(lambda x: x.lower(), commands)
        self.kaomojis = kaomojis
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key)
        self.subscriptions = self.subscribe_to_streams()

    '''
    Standardizes a list of streams in the form [{'name': stream}]
    '''
    @property
    def streams(self):
        if not self.subscribed_streams:
            streams = [
                {'name': stream['name']} for stream
                in self.get_all_zulip_streams()
            ]
            return streams
        else:
            streams = [
                {'name': stream} for stream
                in self.subscribed_streams
            ]
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
        self.client.send_message({
            "type": "stream",
            "subject": msg["subject"],
            "to": msg['display_recipient'],
            "content": new_msg
        })

    '''
    Returns a caption for the gif. This is either an empty string (no caption),
    the single string provided, or a random pick from a list of provided captions
    '''
    def get_caption(self):
        if not self.caption:
            return ''
        elif isinstance(self.caption, str):
            return self.caption
        else:
            return random.choice(self.caption)

    '''
    Calls the giphy API and returns a gif url
    '''
    def get_giphy_response(self):
        response = requests.get(
            'http://api.giphy.com/v1/gifs/random',
            params=self.get_params()
        )
        if response.status_code == 200:
            return response.json()['data']['fixed_width_downsampled_url']
        else:
            raise RuntimeError(
                ':( we failed to GET giphy.\n{}'.format(response.json())
            )

    '''
    Parameters for giphy get requests
    '''
    def get_params(self):
        params = {
            'api_key': 'dc6zaTOxFJmzC',
            'tag': self.search_string
        }
        return params

    '''
    Blocking call that runs forever. Calls self.respond() on every message received.
    '''
    def main(self):
        self.client.call_on_each_message(lambda msg: self.respond(msg))


''' The Customization Part!

    Create a zulip bot under "settings" on zulip.
    Zulip will give you a username and API key
    keywords is the text in Zulip you would like the bot to respond to. This may be a
        single word or a phrase.
    search_string is what you want the bot to search giphy for.
    caption may be one of: [] OR 'a single string' OR ['or a list', 'of strings']
    subscribed_streams is a list of the streams the bot should be active on. An empty
        list defaults to ALL zulip streams
'''

zulip_username = '<your-bot-email>'
zulip_api_key = '<your-api-key>'
commands = [
    '/k',
    '/kaomoji'
]
kaomojis = {
    'shrug': '¯\_(ツ)_/¯'
}

subscribed_streams = []

new_bot = KaomojiBot(zulip_username, zulip_api_key, commands, kaomojis)
new_bot.main()
