"""
about.py - A simple willie information module
Copyright 2013, Tim Dreyer
Modified by ThirdSpurs
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""

import random
import time

from willie.module import commands, rule


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

@commands('about')
def about(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    """Shares basic information on the bot."""
    time.sleep(random.uniform(0, 3))
    willie.say(u"Hello, my name is %s and I'm a pony! " % willie.nick)
    time.sleep(random.uniform(3, 5))
    willie.say(u"Well, that's not exactly right. I'm speaking to you " +
               u"through an implementation of the willie bot hosted by " +
               u"GyroTech.")
    time.sleep(random.uniform(3, 5))
    willie.say(u"I'm also open source! You can see my source at " +
               u"http://willie.dftba.net/ and my plugins at " +
               u"https://www.dropbox.com/sh/7jsl9693z1l46mr/AAANZFIUYg0Rr9B54rkau3Oha?dl=0")

@commands('bugs', 'bug')
def bugs(willie, trigger):
    """Shares basic bug reporting information for the bot."""
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    time.sleep(random.uniform(0, 3))
    willie.say(u'[](/derpyshock "Bugs?! I don\'t have any bugs!")')
    time.sleep(random.uniform(4, 6))
    willie.say(u"But I guess if you think you've found one, you can" +
               u" !tell my owner, GyroTech")

@commands('source')
def source(willie, trigger):
    """Gives links to the bot's source code"""
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    time.sleep(random.uniform(0, 3))
    willie.say('My what?')
    time.sleep(random.uniform(3, 5))
    willie.say(u"Well I guess it's okay, since it's you. You can see my " +
               u"source at http://willie.dftba.net/ and my modules at https://github.com/tecknojock/BurpyBot")


if __name__ == "__main__":
    print __doc__.strip()