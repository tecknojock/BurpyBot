"""
hugs.py - A simple willie Module for interacting with 'hug' actions
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""
import random
import re
import time

from willie.module import rule, rate

try:
    import imp
    import sys
    from permissions import perm_chk
except:
    try:
        ffp, pathname, description = imp.find_module('permissions',['/home/dropbox/Dropbox/WillieBot'])
        permissions = imp.load_source('permissions', pathname, ffp)
        sys.modules['permissions'] = permissions
    finally:
        if ffp:
            ffp.close()
        from permissions import perm_chk


random.seed()


@rule(u'\001ACTION [a-zA-Z0-9 ,]*?' +
      u'((hugs? $nickname)|(gives $nickname a hug))')
@rate(90)
def hugback(willie, trigger):
    """Returns a 'hug' action directed at the bot."""
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    willie.action(random.choice([
        u'hugs %s back' % trigger.nick,
        u'returns the hug',
        u'grips %s tightly' % trigger.nick,
        u'holds on for too long, mumbling something about warmth.'
    ]))

if __name__ == "__main__":
    print __doc__.strip()