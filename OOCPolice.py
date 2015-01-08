"""
vore.py - A simple willie module for silly vore ai
Copyright 2013, GyroTech
Licensed under the Eiffel Forum License 2.

"""
import time
import random
import re
import string
from willie.tools import Nick

from willie.module import commands, example, priority, rule, rate

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
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists OOC_table (user , count, timestamp, nonrp, Primary Key (user))')
    Db.close()

@priority(u'low')
@rule(u'.*')
def action_Police(willie, trigger):
    if not trigger.args[0].startswith(u'#vore-ooc'):
        return  # ignore RP Channels
    action = False
    if re.search("(ACTION)|(^\*.*?\*\s*$)", trigger.bytes):
        action = True
    Db = willie.db.connect()
    cur = Db.cursor()
    user = trigger.hostmask.split('@', 1)[-1]
    params = (user,)
    cur.execute('SELECT timestamp FROM OOC_table WHERE user=?;', params)
    timestamp = cur.fetchone()
    cur.execute('SELECT count FROM OOC_table WHERE user=?;', params)
    count = cur.fetchone()
    cur.execute('Select nonrp FROM OOC_table where user=?;', params)
    nonrp = cur.fetchone()
    if timestamp == None:
        params = (user, 0, time.time(), 0)
        cur.execute('Insert Into OOC_table values (?,?,?,?);', params)
    elif not action:
        if nonrp == 0:
            cur.execute('update OOC_table set nonrp=1 where user=?', params)
        else:
            params = (0, user,)
            cur.execute('update OOC_table set count=? where user=?;', params)
    else:
        if (timestamp[0] + (60*15) > time.time()):
            if len(trigger.group(0)) > 25:
                trigger.group(0)[20]
                count = count[0]+1
                if count == 3:
                    willie.reply("This is not an RP room. Please take your RP to one of the main channels.")
                elif count == 5:
                    willie.write(("TBAN", trigger.sender, "5m", "m:" + trigger.nick + "!*@*"))
                    willie.write(("MODE", trigger.sender, "-hov", trigger.nick,trigger.nick,trigger.nick))
                    willie.reply("You have been muted in this channel for 5 minutes. Please dont RP in here.")
                    count = 0
                params = (count, time.time(), 0, user,)
                cur.execute('update OOC_table set count=?, Timestamp=?, nonrp=? where user=?;', params)
        else:
            count = 1
            params = (count, time.time(), 0, user,)
            cur.execute('update OOC_table set count=?, Timestamp=?, nonrp=? where user=?;', params)
    Db.commit()    
    Db.close()