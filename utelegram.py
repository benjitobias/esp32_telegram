
import time
import gc
import os


machine = os.uname().machine
if 'ESP32' in machine:
    import ujson
    import urequests
else:
    import json as ujson
    import requests as urequests

URL = 'https://api.telegram.org/bot'

ERROR = 1
WARNING = 2
INFO = 3
VERBOSE = 4
DEBUG = 5

PRINT_LEVELS = {
    ERROR: 'Error',
    WARNING: 'Warning',
    INFO: 'Info',
    DEBUG: 'Debug',
    VERBOSE: 'Verbose'
}


class Message(object):
    def __init__(self, message):
        self.raw_message = message
        self.message_text = None
        self.cmd = None
        self.args = []

        self.parse_message_text()        
        

    def parse_message_text(self):
        try:
            message_text = self.raw_message['message']['text']
            self.message_text = message_text

            if message_text.startswith('/'):
                parts = message_text.split(" ")
                self.cmd = parts[0]
                if len(parts) > 1:
                    self.args = parts[1:]
        except TypeError:            
            pass
        except:
            self.print("Invalid message", ERROR)


class ubot(object):
    def __init__(self, token, print_level=WARNING):
        self.url = URL + token
        self.default_handler = {}
        self.sleep_btw_updates = 3
        self.last_message_id = -1
        self.commands = {}
        self.default_handler = None
        self.print_level = print_level
        
        self.print('Started')    

    def get_latest_message(self):
        latest_message = self.get_updates(offset=-1)
        try:
            latest_message = latest_message[-1]
            self.mark_as_read(latest_message)
            return Message(latest_message)
        except(IndexError):
            self.print('No messages found', DEBUG)
            return Message(None)
        
    def get_updates(self, offset=0, limit=1, timeout=0, allowed_updates='message'):
        query_options = {
            'offset': offset,
            'limit': limit,
            'timeout': timeout,
            'allowed_updates': allowed_updates
        }        
        getUpdatesURL = '%s/getUpdates' % self.url
        try:            
            updates = urequests.post(getUpdatesURL, json=query_options)
            return updates.json()['result']
        except (ValueError):
            self.print('No updates available', DEBUG)
            return None
        except (OSError):
            self.print('OSError: request timed out', ERROR)
            return None

            messages = urequests.post

    def mark_as_read(self, message):
        offset = message['update_id'] + 1        
        self.get_updates(offset=offset)

    def send(self, chat_id, text):
        data = {
            'chat_id': chat_id,
            'text': text
        }
        headers =  {
            'Content-type': 'application/json', 
            'Accept': 'text/plain'
        }        
        sendMessageURL = '%s/sendMessage' % self.url
        try:
            response = urequests.post(sendMessageURL, json=data, headers=headers)
        except Exception as e:
            self.print('Error sending message: %s' % e, ERROR)

    def message_handler(self, message):                        
        if message.cmd in self.commands:
            return self.commands[message.cmd](message)
        else:
            if self.default_handler:
                return self.default_handler(message)
            else:
                return None


    def set_default_handler(self, handler):
        self.default_handler = handler

    def register_handler(self, command, handler):
        self.commands[command] = handler

    def check_commands(self):
        msg = self.get_latest_message()
        return self.message_handler(msg)

    def print(self, message, level=INFO):
        if level <= self.print_level:
            print('[telegram] %s: %s' % (level, message))
