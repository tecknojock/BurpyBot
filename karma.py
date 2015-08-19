from willie.tools import Nick
from willie.module import commands, example, priority, rule
import re

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
    
    cur.execute('create table if not exists karma_table (karmatag , karma, Primary Key (karmatag))')
    Db.close()

@commands('karma')
def karma_chk(willie, trigger):
    if not trigger.group(2):
        willie.say("Please specify something to check the karma of.")
        return
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    karmatag = trigger.group(2).strip()
    if karmatag == "":
        return
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (karmatag,)
    cur.execute('SELECT karma FROM karma_table WHERE Upper(karmatag)=upper(?)', params)
    try:
        karma = cur.fetchone()[0]
    except:
        willie.say(u"%s has no karma." % (karmatag))
        return
    Db.close()
    willie.say(u"%s has a karma of %d" % (karmatag,karma))

@rule(".*\+\+\s*$")
def karmaup(willie, trigger):
    '''For adding new permsions. Use syntax hostmask Permission'''
    if not perm_chk(trigger.hostmask, "Bc", willie) or not "#" == trigger.sender[0]:
        return
    karmatag = re.sub('(.*?)\:?s*\+\+\s*$',('\\1'), trigger).strip()
    if karmatag == "":
        return
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (karmatag,)
    cur.execute('SELECT karma FROM karma_table WHERE Upper(karmatag)=upper(?)', params)
    try:
        karma = cur.fetchone()[0]
        karma += 1
    except:
        karma = 1
    params = (karmatag,)
    cur.execute('Delete from karma_table where Upper(karmatag)=upper(?)', params)
    params = (karmatag, karma)
    cur.execute('Insert Into karma_table VALUES (?, ?)', params)
    Db.commit()
    Db.close()
    willie.say(u"%s now has a karma of %d" % (karmatag, karma))



@rule(".*--\s*$")
def karmadown(willie, trigger):
    '''For adding new permsions. Use syntax hostmask Permission'''
    if not perm_chk(trigger.hostmask, "Bc", willie) or not "#" == trigger.sender[0]:
        return
    karmatag = re.sub('(.*?):?(\s)*--\s*$',('\\1'), trigger).strip()
    if karmatag == "":
        return
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (karmatag,)
    cur.execute(u'SELECT karma FROM karma_table WHERE Upper(karmatag)=upper(?)', params)
    try:
        karma = cur.fetchone()[0]
        karma -= 1
    except:
        karma = -1
    params = (karmatag,)
    cur.execute('Delete from karma_table where Upper(karmatag)=upper(?)', params)
    params = (karmatag, karma)
    cur.execute('Insert Into karma_table VALUES (?, ?)', params)
    Db.commit()
    Db.close()
    willie.say(u"%s now has a karma of %d" % (karmatag, karma))

