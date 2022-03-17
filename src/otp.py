# -*- coding: utf-8 -*-

import hmac
import base64
import struct
import hashlib
import time


def get_hotp_token(key, intervals_no):
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(key):
    token = get_hotp_token(key, intervals_no=int(time.time()) // 30)
    return str(token).zfill(6)


def get_totp_time_remaining():
    return int(30 - (time.time() % 30))


def pad_base32_str(str, padding_char):
    str_len = len(str)
    missing_padding = str_len % 8
    if missing_padding != 0:
        # str += '=' * (8 - missing_padding)
        str = str.ljust(str_len + 8 - missing_padding, padding_char)
    return str


def is_otp_secret_valid(secret):
    try:
        secret = secret.replace(' ', '')
        if not len(secret):
            return False
        secret = pad_base32_str(secret, '=')
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
        secret = pad_base32_str(secret, '=')
        key = base64.b32decode(secret, casefold=True)
    return key
