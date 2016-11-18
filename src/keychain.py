#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copied from https://raw.github.com/spjwebster/keychain.py/master/keychain.py

"""Keychain.py Simple Keychain library for MacOSX

Keychain.py  is a simple class allowing access to keychain data and
settings. Keychain.py can also setup new keychains as required. As the
keychain is only available on MaxOSX the module will raise ImportError
if import is attempted on anything other than Mac OSX

Created by Stuart Colville on 2008-02-02
Muffin Research Labs. http://muffinresearch.co.uk/

Refined by Steve Webster on 2009-01-21
Dynamic Flash. http://dynamicflash.com

Copyright (c) 2008, Stuart J Colville and Steve Webster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Muffin Research Labs nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """


import sys
import commands
import re


RXACCOUNT = re.compile(r'"acct"<blob>="(.*?)"', re.S)
RXPASS = re.compile(r'password: "(.*?)"', re.S)
RXDATA = re.compile(r'data:.*?"(.*?)"', re.S)
RXSERVICE = re.compile(r'"svce"<blob>="(.*?)"', re.S)



class KeychainException(Exception):
    """The generic keychain exception class"""

    def __init__(self, value=""):
        """Set's the message on instantiation"""
        self.message_prefix = "Keychain Error:"
        self.message = "%s %s" % (self.message_prefix, value)

    def __str__(self):
        """Returns the error message"""
        return self.message


class Keychain:
    """Simple class for creating and accessing the MacOSX keychain"""

    def __init__(self):
        if sys.platform == 'darwin':
            self.list_keychains()
        else:
            raise KeychainException('Keychain is only available on Mac OSX')


    @staticmethod
    def list_keychains():
        """Returns a dictionary of all of the keychains found on the system"""

        result = commands.getoutput("security list-keychains")
        keychain_rx = re.compile(r'".*?/([0-9a-z_\-]*)\.keychain"', re.I | re.M)
        keychains = {}
        for match in keychain_rx.finditer(result):
            keychains[match.group(1)]=match.group().strip('"')
        return keychains


    @staticmethod
    def normalise_keychain_name(keychain_name):
        """Ensures keychain name doesn't end with .keychain"""

        return keychain_name.endswith('.keychain') \
            and keychain_name.replace('.keychain', "") or keychain_name


    def check_keychain_exists(self, keychain):
        """Checks that a specific keychain exists

        Rationalises keychain strings as to whether they end with .keychain
        and looks the keychain them up in the dictionary of keychains created
        at instantiation. Returns a tuple containing True if successful and
        False + error message if keychain is not found

        """
        keychain_name = self.normalise_keychain_name(keychain)
        keychain_list = self.list_keychains()

        if keychain_name in keychain_list:
            return True
        else:
            raise KeychainException(
                "%s.keychain  doesn't exist" % keychain
            )


    def get_generic_password(self, keychain, account, servicename=None):
        """Returns account information from specified keychain item """

        if self.check_keychain_exists(keychain):
            account = account and '-a %s' % (account,) or ''
            servicename = servicename and '-s %s' % (servicename,) or ''
            result = commands.getstatusoutput(
                "security find-generic-password -g %s %s %s.keychain" % \
                    (account, servicename, keychain)
            )
            if result[0]:
                return False, 'The specified item could not be found'
            else:
                account = RXACCOUNT.search(result[1])
                password = RXPASS.search(result[1])
                service = RXSERVICE.search(result[1])
                
                if account and password:
                    data = {
                        "account":account.group(1),
                        "password":password.group(1),
                    }
                    if service:
                        data.update({"service": service.group(1)})
                    return data
                else:
                    return False, 'The specified item could not be found'


    def set_generic_password(self, keychain, account, password, \
        servicename=None):
        """Create and store a generic account and password in a keychain"""

        if self.check_keychain_exists(keychain):
            account = account and '-a %s' % (account,) or ''
            password = password and '-p %s' % (password,) or ''
            servicename = servicename and '-s %s' % (servicename,) or ''
            result = commands.getstatusoutput(
                "security add-generic-password %s %s %s %s.keychain" % (
                    account, password, servicename, keychain
                )
            )
            if result[0]:
                return False, 'The specified password could not be added to '\
                    '%s' % keychain
            elif result[0] is 0:
                return True, 'Password added to %s successfully' % keychain


    def lock_keychain(self, keychain):
        """Locks an un-locked Keychain"""

        if self.check_keychain_exists(keychain):
            result = commands.getstatusoutput(
                "security lock-keychain %s.keychain" % (keychain,)
            )
            if result[0]:
                return False, 'Keychain: %s could not be locked' % keychain
            elif result[0] is 0:
                return True, 'Keychain: %s locked successfully' % keychain


    def unlock_keychain(self, keychain, password=None):
        """Unlocks a locked Keychain"""

        if self.check_keychain_exists(keychain):
            if not password:
                from getpass import getpass
                password = getpass('Password:')
            result = commands.getstatusoutput("security unlock-keychain -p %s "\
                "%s.keychain" % (password, keychain,))

            if result[0]:
                return False, 'Keychain could not be unlocked'
            elif result[0] is 0:
                return True, 'Keychain unlocked successfully'


    def create_keychain(self, keychain, password=None):
        """Creates a Keychain

        returns True on success and False if it fails

        """

        if not password:
            from getpass import getpass
            password = getpass('Password:')

        keychain = self.normalise_keychain_name(keychain)
        result = commands.getstatusoutput(
            "security create-keychain -p %s %s.keychain" % (password, keychain,)
        )
        if result[0] == 12288:
            return False, 'A Keychain already exists with this name'
        elif result[0]:
            return False, 'Keychain creation failed'
        elif result[0] is 0:
            return True, 'Keychain created successfully'


    def delete_keychain(self, keychain):
        """Deletes a Keychain

        Returns True on success and False if it fails

        """

        if self.check_keychain_exists(keychain):
            result = commands.getstatusoutput(
                "security delete-keychain %s.keychain" % keychain
            )

            if result[0]:
                return False, 'Keychain deletion failed'
            elif result[0] is 0:
                return True, 'Keychain deleted successfully'


    def set_keychain_settings(self, keychain, lock=True, timeout=0):
        """Allows setting the keychain configuration.

        If lock is True the keychain will be locked on sleep. If the timeout is
        set to anything other than 0 the keychain will be set to lock after
        timeout seconds of inactivity

        """

        if self.check_keychain_exists(keychain):
            lock = lock and "-l " or ""
            timeout = timeout and '-u -t %s' % (timeout,) or ''
            result = commands.getstatusoutput(
                "security set-keychain-settings %s %s %s.keychain" % \
                    (lock, timeout, keychain,)
            )

            if result[0]:
                return False, 'Keychain settings failed'
            elif result[0] is 0:
                return True, 'Keychain updated successfully'


    def show_keychain_info(self, keychain):
        """Returns a dictionary containing the keychain settings"""

        if self.check_keychain_exists(keychain):

            result = commands.getstatusoutput(
                "security show-keychain-info %s.keychain" % (keychain,)
            )

            if result[0]:
                return False, 'Keychain could not be found'
            elif result[0] is 0:
                info = {}
                info['keychain'] = keychain

                if result[1].find('lock-on-sleep') > -1:
                    info['lock-on-sleep'] = True

                if result[1].find('no-timeout') > -1:
                    info['timeout'] = 0
                else:
                    timeout_rx = re.compile(r'timeout=(\d+)s', re.S)
                    match = timeout_rx.search(result[1])
                    info['timeout'] = match.group(1)
                return info


    def list_keychain_accounts(self, keychain):
        """ Returns account + password list from specified keychain """

        if self.check_keychain_exists(keychain):
            result = commands.getstatusoutput(
                "security dump-keychain -d %s.keychain" % (keychain)
            )
            data = []
            for kc in result[1].split("keychain:"):
                account = RXACCOUNT.search(kc)
                password = RXDATA.search(kc)
                service = RXSERVICE.search(kc)
                if account and password:
                    data.append({
                        "account":account.group(1),
                        "password":password.group(1)
                    })
                if service:
                    data[-1].update({"service": service.group(1)})

            return data


    def remove_generic_password(self, keychain, keychainpassword, account):
        """ Drop a generic password.

        This is carried out by recreating the old keychain minus the
        specified account.

        """

        if self.check_keychain_exists(keychain):

            if not keychainpassword:
                raise KeychainException("Password must be supplied")

            old_keychain = self.show_keychain_info(keychain)
            old_accounts = self.list_keychain_accounts(keychain)

            if self.delete_keychain(keychain)[0] is False:
                return False, 'Keychain could not be modified'

            self.create_keychain(keychain, keychainpassword)
            self.set_keychain_settings(
                keychain,
                old_keychain["lock-on-sleep"],
                old_keychain["timeout"]
            )

            for old_account in old_accounts:
                if old_account.get("account", None) and \
                    old_account["account"] != account:

                    servicename = old_account.get('service', None)
                    self.set_generic_password(
                        keychain,
                        old_account["account"],
                        old_account["password"],
                        servicename=servicename,
                    )

            return (True, "Generic Password removed Successfully")


    def change_generic_password(self, keychain, keychain_password, \
        account, new_account_password):
        """ Change a generic password."""

        if self.check_keychain_exists(keychain):
            old_account = self.get_generic_password(keychain, account)
            self.remove_generic_password(keychain, keychain_password, account)
            self.set_generic_password(
                keychain, 
                account, 
                new_account_password,
                servicename=old_account.get("service", None),
            )
            return (True, "Generic Password updated Successfully")
        
        
