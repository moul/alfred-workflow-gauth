# -*- coding: utf-8 -*-

import sys
import os
import hmac
import base64
import struct
import hashlib
import time
import ConfigParser
import os.path
import math

import alfred


def get_hotp_token(key, intervals_no):
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(key):
    token = get_hotp_token(key, intervals_no=int(time.time()) // 30)
    return str(token).zfill(6)


def get_totp_time_remaining():
    return int(30 - (time.time() % 30))


def is_secret_valid(secret):
    try:
        secret = secret.replace(' ', '')
        secret = secret.ljust(int(math.ceil(len(secret) / 16.0) * 16), '=')
        key = base64.b32decode(secret, casefold=True)
        get_totp_token(key)
    except:
        return False

    return True


def get_hotp_key(key=None, secret=None, hexkey=None):
    if hexkey:
        key = hexkey.decode('hex')
    if secret:
        secret = secret.replace(' ', '')
        secret = secret.ljust(int(math.ceil(len(secret) / 16.0) * 16), '=')
        key = base64.b32decode(secret, casefold=True)
    return key


class AlfredWorkflow(object):
    _reserved_words = []

    def write_text(self, text):
        return alfred.write(text)

    def write_item(self, item):
        return self.write_items([item])

    def write_items(self, items):
        return alfred.write(alfred.xml(items, maxresults=self.max_results))

    def message_item(self, title, message, icon=None, uid=0):
        return alfred.Item({u'uid': alfred.uid(uid), u'arg': '',
                            u'ignore': 'yes'}, title, message, icon)

    def warning_item(self, title, message, uid=0):
        return self.message_item(title=title, message=message, uid=uid,
                                 icon='warning.png')

    def error_item(self, title, message, uid=0):
        return self.message_item(title=title, message=message, uid=uid,
                                 icon='error.png')

    def exception_item(self, title, exception, uid=0):
        message = str(exception).replace('\n', ' ')
        return self.error_item(title=title, message=message, uid=uid)

    def route_action(self, action, query=None):
        method_name = 'do_{}'.format(action)
        if not hasattr(self, method_name):
            raise RuntimeError('Unknown action {}'.format(action))

        method = getattr(self, method_name)
        return method(query)

    def is_command(self, query):
        try:
            command, rest = query.split(' ', 1)
        except ValueError:
            command = query
            command = command.strip()
        return command in self._reserved_words or \
            hasattr(self, 'do_{}'.format(command))


class AlfredGAuth(AlfredWorkflow):
    _config_file_initial_content = """
#Examples of valid configurations:
#[google - bob@gmail.com]
#secret=xxxxxxxxxxxxxxxxxx
#
#[evernote - robert]
#secret=yyyyyyyyyyyyyyyyyy
"""

    _reserved_words = ['add', 'update', 'remove']

    def __init__(self, config_file='~/.gauth', max_results=20):
        self._config_file = config_file
        self.config_file = os.path.expanduser(self._config_file)
        self.max_results = max_results
        self._config = None

        # If the configuration file doesn't exist, create an empty one
        if not os.path.isfile(self.config_file):
            self.create_config()

        try:
            if not self.config.sections() and action != 'add':
                # If the configuration file is empty,
                # tell the user to add secrets to it
                self.write_item(self.config_file_is_empty_item())
                return
        except Exception as e:
            item = self.exception_item(title='{}: Invalid syntax'
                                       .format(self._config_file),
                                       exception=e)
            self.write_item(item)

    @property
    def config(self):
        if not self._config:
            self._config = ConfigParser.RawConfigParser()
            self._config.read(os.path.expanduser(self.config_file))
        return self._config

    def create_config(self):
        with open(os.path.expanduser(self.config_file), 'w') as f:
            f.write(self._config_file_initial_content)
            f.close()

    def config_get_account_token(self, account):
        try:
            secret = self.config.get(account, 'secret')
        except:
            secret = None

        try:
            key = self.config.get(account, 'key')
        except:
            key = None

        try:
            hexkey = self.config.get(account, 'hexkey')
        except:
            hexkey = None

        key = get_hotp_key(secret=secret, key=key, hexkey=hexkey)
        return get_totp_token(key)

    def config_list_accounts(self):
        return self.config.sections()

    def filter_by_account(self, account, query):
        return len(query.strip()) and not query.lower() in str(account).lower()

    def account_item(self, account, token, uid=None):
        return alfred.Item({u'uid': alfred.uid(uid), u'arg': token,
                            u'autocomplete': account}, account,
                           'Post {} at cursor'.format(token), 'icon.png')

    def time_remaining_item(self):
        # The uid for the remaining time will be the current time,
        # so it will appears always at the last position in the list
        time_remaining = get_totp_time_remaining()
        return alfred.Item({u'uid': time.time(), u'arg': '', u'ignore': 'yes'},
                           'Time Remaining: {}s'.format(time_remaining),
                           None, 'time.png')

    def config_file_is_empty_item(self):
        return self.warning_item(title='GAuth is not yet configured',
                                 message='You must add your secrets to '
                                 'the {} file (see documentation)'
                                 .format(self.config_file))

    def search_by_account_iter(self, query):
        if self.is_command(query):
            return
        i = 0
        for account in self.config_list_accounts():
            if self.filter_by_account(account, query):
                continue
            token = self.config_get_account_token(account)
            entry = self.account_item(uid=i, account=account, token=token)
            if entry:
                yield entry
                i += 1
        if i > 0:
            yield self.time_remaining_item()
        else:
            yield self.warning_item('Account not found',
                                    'There is no account matching "{}" '
                                    'on your configuration file '
                                    '({})'.format(query,
                                                  self.config_file))

    def add_account(self, account, secret):

        if not is_secret_valid(secret):
            return "Invalid secret:\n[{0}]".format(secret)

        config_file = open(self.config_file, 'r+')
        try:
            self.config.add_section(account)
            self.config.set(account, "secret", secret)
            self.config.write(config_file)
        except ConfigParser.DuplicateSectionError:
            return "Account already exists:\n[{0}]".format(account)
        finally:
            config_file.close()

        return "A new account was added:\n[{0}]".format(account)

    def do_search_by_account(self, query):
        self.write_items(self.search_by_account_iter(query))

    def do_add_account(self, query):
        try:
            account, secret = query.split(",", 1)
            account = account.strip()
            secret = secret.strip()
        except ValueError:
            return self.write_text('Invalid arguments!\n'
                                   'Please enter: account, secret.')
        self.write_text(self.add_account(account, secret))


def main(action, query):
    alfred_gauth = AlfredGAuth()
    alfred_gauth.route_action(action, query)

if __name__ == "__main__":
    main(action=alfred.args()[0], query=alfred.args()[1])
