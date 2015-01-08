"""
uptime.py - A simple willie module
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""
import time
from datetime import timedelta

from willie.module import commands

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



def setup(willie):
    if "uptime" not in willie.memory:
        willie.debug(u"uptime:startup",
                     u"Found no time, adding.",
                     u"verbose"
                     )
        willie.memory["uptime"] = int(time.time())
    else:
        willie.debug(u"uptime:startup",
                     u"Found time.",
                     u"verbose"
                     )


@commands('uptime')
def uptime(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    now = int(time.time())
    then = willie.memory["uptime"]
    diff = str(timedelta(seconds=now - then))
    willie.debug(u"uptime", diff, u"verbose")
    willie.debug(u"uptime", len(diff), u"verbose")
    if len(diff) < 9:
        h, m, s = diff.split(":")
        d = '0 days'
    else:
        d, m, s = diff.split(":")
        d, h = d.split(", ")
    willie.say((u"I have had %s, %s hours, %s minutes and %s " +
                u"seconds of uptime.") % (d, h, m, s)
               )


if __name__ == "__main__":
    print __doc__.strip()