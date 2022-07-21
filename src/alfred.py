# -*- coding: utf-8 -*-
import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

"""
You should run your script via /bin/bash with all escape options ticked.
The command line should be

python3 yourscript.py "{query}" arg2 arg3 ...
"""


UNESCAPE_CHARACTERS = u""" ;()"""

_MAX_RESULTS_DEFAULT = 9


with open('info.plist', 'rb') as file:
    preferences = plistlib.load(file)
bundleid = preferences['bundleid']


class Item(object):
    @classmethod
    def unicode(cls, value):
        try:
            items = value.items()
        except AttributeError:
            return str(value)
        else:
            return dict(map(str, item) for item in items)

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml(), encoding='utf-8')

    def xml(self):
        item = Element(u'item', self.unicode(self.attributes))
        for attribute in (u'title', u'subtitle', u'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            try:
                (value, attributes) = value
            except:
                attributes = {}
                elem = SubElement(item, attribute, self.unicode(attributes))
                elem.text = str(value)
        return item


def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])


def config():
    return _create('config')


def decode(s):
    return unicodedata.normalize('NFC', s.encode("utf-8").decode('utf-8'))


def get_uid(uid):
    return u'-'.join(map(str, (bundleid, uid)))


def unescape(query, characters=None):
    if not characters:
        characters = UNESCAPE_CHARACTERS
    for character in characters:
        query = query.replace('\\%s' % character, character)
    return query


def write(text):
    sys.stdout.buffer.write(text)


def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')


def _create(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path


def work(volatile):
    path = {
        True: '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data',
        False: '~/Library/Application Support/Alfred 2/Workflow Data'
    }[bool(volatile)]
    return _create(os.path.join(os.path.expanduser(path), bundleid))


def config_set(key, value, volatile=True):
    filepath = os.path.join(work(volatile), 'config.plist')
    with open(filepath, 'rb') as file:
        try:
            conf = plistlib.load(file)
        except IOError:
            conf = {}
    conf[key] = value
    plistlib.writePlist(conf, filepath)


def config_get(key, default=None, volatile=True):
    filepath = os.path.join(work(volatile), 'config.plist')
    with open(filepath, 'rb') as file:
        try:
            conf = plistlib.load(file)
        except IOError:
            conf = {}
    if key in conf:
        return conf[key]
    return default


class AlfredWorkflow(object):
    _reserved_words = []

    def write_text(self, text):
        print(text)

    def write_item(self, item):
        return self.write_items([item])

    def write_items(self, items):
        return write(xml(items, maxresults=self.max_results))

    def message_item(self, title, message, icon=None, uid=0):
        return Item({
            u'uid': get_uid(uid),
            u'arg': '',
            u'ignore': 'yes'
        }, title, message, icon)

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

