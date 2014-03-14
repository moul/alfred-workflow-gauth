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


_MAX_RESULTS = 20
_CONFIG_FILE = os.path.expanduser("~") + '/.gauth'


def get_hotp_token(key, intervals_no):
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(key):
    return get_hotp_token(key, intervals_no=int(time.time()) // 30)


def get_section_token(config, section):
    try:
        secret = config.get(section, 'secret')
    except:
        secret = None

    try:
        key = config.get(section, 'key')
    except:
        key = None

    try:
        hexkey = config.get(section, 'hexkey')
    except:
        hexkey = None

    if hexkey:
        key = hexkey.decode('hex')

    if secret:
        secret = secret.replace(' ', '')
        secret = secret.ljust(int(math.ceil(len(secret) / 16.0) * 16), '=')
        key = base64.b32decode(secret, casefold=True)

    return str(get_totp_token(key)).zfill(6)


def get_time_remaining():
    return int(30 - (time.time() % 30))


def list_accounts(config, query):
    i = 0
    for section in config.sections():
        if len(query.strip()) and not query.lower() in str(section).lower():
            continue

        try:
            token = get_section_token(config, section)
            yield alfred.Item({u'uid': alfred.uid(i), u'arg': token,
                               u'autocomplete': section},
                              section,
                              'Post {} at cursor'.format(token),
                              'icon.png')
            i += 1
        except:
            pass

    if i > 0:
        # The uid for the remaining time will be the current time,
        # so it will appears always at the last position in the list
        yield alfred.Item({u'uid': time.time(), u'arg': '', u'ignore': 'yes'},
                          'Time Remaining: {}s'.format(get_time_remaining()),
                          None, 'time.png')
    else:
        yield alfred.Item({u'uid': alfred.uid(0), u'arg': '', u'ignore': 'yes'},
                          "Account not found",
                          "There is no account named '" + query +
                          "' on your configuration file (~/.gauth)",
                          'warning.png')


def config_file_not_found():
    yield alfred.Item({u'uid': alfred.uid(0), u'arg': '', u'ignore': 'yes'},
                      'Google Authenticator is not yet configured',
                      "You must create a '~/.gauth' file with your secrets " +
                      "(see documentation)",
                      'error.png')


def get_config():
    config = ConfigParser.RawConfigParser()
    config.read(os.path.expanduser(_CONFIG_FILE))
    return config


def main(action, query):
    try:
        config = get_config()
    except Exception as e:
        alfred.write(alfred.xml([alfred.Item({u'uid': alfred.uid(0), u'arg': '',
                                              u'ignore': 'yes'},
                                             "~/.gauth: Invalid syntax",
                                             str(e).replace('\n', ' '),
                                             "error.png")]))
        sys.exit(1)
    if action == 'list':
        if os.path.isfile(_CONFIG_FILE):
            alfred.write(alfred.xml(list_accounts(config, query),
                                    maxresults=_MAX_RESULTS))
        else:
            alfred.write(alfred.xml(config_file_not_found()))


if __name__ == "__main__":
    main(action=alfred.args()[0], query=alfred.args()[1])
