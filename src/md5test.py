#!/bin/python2

from __future__ import print_function
import hashlib

hash_local = int(hashlib.md5(open('201420.db', 'rb').read()).hexdigest(), 16)
hash_remote = int(open('201420.sum').read().replace('\n', ''), 16)

print(hash_local)
print(hash_remote)

if hash_local == hash_remote:
    print('\nUp to date')
else:
    print('\nUpdate your database')
