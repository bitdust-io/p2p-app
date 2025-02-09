#!/usr/bin/python
# rsa_key.py
#
# Copyright (C) 2008 Veselin Penev, https://bitdust.io
#
# This file (rsa_key.py) is part of BitDust Software.
#
# BitDust is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BitDust Software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with BitDust Software.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact us if you have any questions at bitdust.io@gmail.com
#
#
#
"""
.. module:: rsa_key.


"""

#------------------------------------------------------------------------------

from __future__ import absolute_import

#------------------------------------------------------------------------------

_Debug = False
_CryptoLog = None

#------------------------------------------------------------------------------

import struct
import binascii
import rsa

#------------------------------------------------------------------------------

from lib import strng
from lib import system
from lib import number
from lib import pkcs1_v2

#------------------------------------------------------------------------------

class RSAKey(object):

    def __init__(self):
        self.keyObject = None
        self.privateKeyObject = None
        self.label = ''
        self.bits = None
        self.signed = None
        self.active = True
        self.meta = {}

    def __str__(self) -> str:
        return 'RSAKey(%s|%s)' % (self.label, 'active' if self.active else 'inactive')

    def isReady(self):
        return self.keyObject is not None

    def forget(self):
        self.keyObject = None
        self.privateKeyObject = None
        self.bits = None
        self.label = ''
        self.signed = None
        self.active = False
        self.meta = {}
        # gc.collect()
        return True

    def size(self):
        return self.bits

    def generate(self, bits):
        if self.keyObject:
            raise ValueError('key object already exist')
        self.bits = bits
        self.keyObject, self.privateKeyObject = rsa.newkeys(self.bits)
        return True

    def isPublic(self):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        if self.privateKeyObject:
            return False
        return True

    def isPrivate(self):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        if not self.privateKeyObject:
            return False
        return True

    def public(self):
        if self.isPublic():
            return self
        return self.keyObject

    def fromDict(self, key_dict):
        if self.keyObject:
            raise ValueError('key object already exist')
        key_src = key_dict['body']
        result = self.fromString(key_src)
        if result:
            self.label = key_dict.get('label', '')
            self.active = key_dict.get('active', True)
            self.meta = key_dict.get('meta', {})
            if 'signature' in key_dict and 'signature_pubkey' in key_dict:
                self.signed = (
                    key_dict['signature'],
                    key_dict['signature_pubkey'],
                )
        del key_src
        # gc.collect()
        return result

    def fromString(self, key_src):
        if self.keyObject:
            raise ValueError('key object already exist')
        if strng.is_text(key_src):
            key_src = strng.to_bin(key_src)
        try:
            if key_src.count(b'BEGIN RSA PUBLIC KEY'):
                self.keyObject = rsa.PublicKey.load_pkcs1(key_src)
                self.privateKeyObject = None
            elif key_src.count(b'BEGIN RSA PRIVATE KEY'):
                self.privateKeyObject = rsa.PrivateKey.load_pkcs1(key_src)
                self.keyObject = rsa.PublicKey(self.privateKeyObject.n, self.privateKeyObject.e)
            elif key_src.count(b'ssh-rsa '):
                keystring = binascii.a2b_base64(key_src.split(b' ')[1])
                keyparts = []
                while len(keystring) > 4:
                    length = struct.unpack(">I", keystring[:4])[0]
                    keyparts.append(keystring[4:4 + length])
                    keystring = keystring[4 + length:]
                e = number.bytes_to_long(keyparts[1])
                n = number.bytes_to_long(keyparts[2])
                self.keyObject = rsa.PublicKey(n, e)
                self.privateKeyObject = None
            else:
                self.privateKeyObject = rsa.PrivateKey.load_pkcs1(key_src)
                self.keyObject = rsa.PublicKey(self.privateKeyObject.n, self.privateKeyObject.e)
        except Exception as exc:
            if _Debug:
                print(exc, 'key_src=%r' % key_src)
            raise ValueError('failed to read key body')
        del key_src
        # gc.collect()
        return True

    def fromFile(self, keyfilename):
        if self.keyObject:
            raise ValueError('key object already exist')
        key_src = system.ReadTextFile(keyfilename)
        key_src = strng.to_bin(key_src)
        try:
            if key_src.count(b'BEGIN RSA PUBLIC KEY'):
                self.keyObject = rsa.PublicKey.load_pkcs1(key_src)
                self.privateKeyObject = None
            elif key_src.count(b'BEGIN RSA PRIVATE KEY'):
                self.privateKeyObject = rsa.PrivateKey.load_pkcs1(key_src)
                self.keyObject = rsa.PublicKey(self.privateKeyObject.n, self.privateKeyObject.e)
            elif key_src.count(b'ssh-rsa '):
                keystring = binascii.a2b_base64(key_src.split(b' ')[1])
                keyparts = []
                while len(keystring) > 4:
                    length = struct.unpack(">I", keystring[:4])[0]
                    keyparts.append(keystring[4:4 + length])
                    keystring = keystring[4 + length:]
                e = number.bytes_to_long(keyparts[1])
                n = number.bytes_to_long(keyparts[2])
                self.keyObject = rsa.PublicKey(n, e)
                self.privateKeyObject = None
            else:
                self.privateKeyObject = rsa.PrivateKey.load_pkcs1(key_src)
                self.keyObject = rsa.PublicKey(self.privateKeyObject.n, self.privateKeyObject.e)
        except Exception as exc:
            if _Debug:
                print(exc, 'key_src=%r' % key_src)
            raise ValueError('failed to read key body')
        del key_src
        # gc.collect()
        return True

    def toPrivateString(self, output_format='PEM'):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        if not self.isPrivate():
            raise ValueError('this key contains only public component')
        return strng.to_text(self.privateKeyObject.save_pkcs1(output_format)).strip()

    def toPublicString(self):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        e_bytes = number.long_to_bytes(self.keyObject.e)
        n_bytes = number.long_to_bytes(self.keyObject.n)
        if (e_bytes[0]) & 0x80:
            e_bytes = b'\x00' + e_bytes
        if (n_bytes[0]) & 0x80:
            n_bytes = b'\x00' + n_bytes
        keyparts = [b'ssh-rsa', e_bytes, n_bytes]
        keystring = b''.join([struct.pack(">I", len(kp)) + kp for kp in keyparts])
        return strng.to_text(b'ssh-rsa ' + binascii.b2a_base64(keystring)[:-1])

    def toDict(self, include_private=False):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        if include_private and not self.isPrivate():
            raise ValueError('this key contains only public component')
        if include_private:
            key_body = strng.to_text(self.toPrivateString())
        else:
            key_body = strng.to_text(self.toPublicString())
        key_dict = {
            'body': key_body,
            'label': self.label,
            'active': self.active,
        }
        if self.isSigned():
            key_dict.update({
                'signature': self.signed[0],
                'signature_pubkey': self.signed[1],
            })
        if self.meta:
            key_dict['meta'] = self.meta
        return key_dict

    def sign(self, message, as_digits=True):
        global _CryptoLog
        # if _CryptoLog is None:
        #     _CryptoLog = os.environ.get('CRYPTO_LOG') == '1'
        if not self.keyObject:
            raise ValueError('key object is not exist')
        if not strng.is_bin(message):
            raise ValueError('message must be byte string')
        signature_raw = rsa.sign(message, self.privateKeyObject, 'SHA-1')
        if not as_digits:
            if _Debug:
                if _CryptoLog:
                    print('sign signature_raw:', signature_raw)
            return signature_raw
        signature_long = number.bytes_to_long(signature_raw)
        signature_bytes = strng.to_bin(signature_long)
        if _Debug:
            if _CryptoLog:
                print('sign signature_bytes:', signature_bytes)
        return signature_bytes


    def verify(self, signature, message, signature_as_digits=True):
        global _CryptoLog
        # if _CryptoLog is None:
        #     _CryptoLog = os.environ.get('CRYPTO_LOG') == '1'
        signature_bytes = signature
        if signature_as_digits:
            signature_bytes = number.long_to_bytes(signature, blocksize=4)
        if not strng.is_bin(signature_bytes):
            raise ValueError('signature must be byte string')
        if not strng.is_bin(message):
            raise ValueError('message must be byte string')
        result = False
        try:
            ret = rsa.verify(message, signature_bytes, self.keyObject)
            if ret != 'SHA-1':
                raise ValueError('signature is not valid')
            result = True
        except (
            ValueError,
            TypeError
        ) as exc:
            # do not raise any exception... just return False
            if _Debug:
                print(exc, 'signature=%r message=%r' % (signature, message))
        if _Debug:
            if _CryptoLog:
                print('verify', result, signature)
        return result

    def encrypt(self, private_message):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        ciphertext = pkcs1_v2.encrypt_OAEP(private_message, self.keyObject)
        return ciphertext

    def decrypt(self, encrypted_payload):
        if not self.keyObject:
            raise ValueError('key object is not exist')
        private_message = pkcs1_v2.decrypt_OAEP(encrypted_payload, self.privateKeyObject)
        return private_message

    def isSigned(self):
        return self.signed is not None
