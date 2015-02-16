import time
import random
import re
from willie.tools import Nick
import urllib
import urllib2
from willie.module import commands, example, priority, rule, rate, event
from subprocess import call
import string
import heapq


def hacky_import(mod):
    ffp = None
    try:
        ffp, pathname, description = imp.find_module(mod, [os.path.expanduser("~/.willie/modules/")])
        loaded = imp.load_source(mod, pathname, ffp)
        sys.modules[mod] = loaded
    finally:
        if ffp:
            ffp.close()
    
    return __import__(mod)

perm_chk = hacky_import(permissions).perm_chk
nicks = hacky_import(nicks)

try:
    import nicks
except:
    try:
        ffp, pathname, description = imp.find_module('nicks',['/home/dropbox/Dropbox/WillieBot'])
        nicks = imp.load_source('nicks', pathname, ffp)
        sys.modules['nicks'] = permissions
    finally:
        if ffp:
            ffp.close()
        import nicks


'''@commands("test1")
def test1(willie, trigger):
    stuff = list(willie.doc)
    for item in stuff:
        willie.say(str(item))'''
 
#@commands("poke")
#def poke(willie, trigger):
#    willie.action('pokes ' + trigger.group(2))

'''@rule(".*")
def echo(willie,trigger):
	willie.debug("#gorgerbot",trigger,"warning")'''

'''@commands("renameTable")
def renameTable(willie, trigger):
    DB = willie.db.connect()
    cur = DB.cursor()
    cur.execute('Alter Table tag_table ADD ')
    DB.close()'''

'''@commands("columnadd")
def columnadd(willie, trigger):
    willie.db.tag_table.addcolumns('Placeholder')'''

'''@commands("VHostSet")
def VHostSet(willie, trigger):
    willie.msg("HostServ", "take $account.Is.Not.A.Clever.Poni")'''

'''Catch Randomusr's real ip'''
'''@event('JOIN')
@rule('.*')
def echoevent(willie, trigger):
    if trigger.nick == "Pony_1":
        willie.say(event)

@event('RPL_WHOISUSER')
@rule('.*')
def whoisevent(willie, trigger):
    willie.debug("#gorgerbot",trigger,"Warning")'''

#@commands('tagtest')
#def host(willie, trigger):
#    tagTargeted= trigger.group(2).split("|");
#    for content in tagTargeted:
#        willie.say(content);

@commands('join')
def Joinhost(willie, trigger):
    if perm_chk(trigger.hostmask, "Ad", willie):
        channel = trigger.group(2);
        willie.say(unicode.format(u"Joining {0}", channel))
        willie.join(channel);

@commands('part')
def parthost(willie, trigger):
    if perm_chk(trigger.hostmask, "Ad", willie):
        channel = trigger.group(2);
        willie.part(channel);
#@commands('testremove')
#def tagremovetest(willie, trigger):
#    if (len(trigger.group(2).split(None, 2)) == 1):
#        content = trigger.group(2).split("|")
#        tagTargeted = trigger.nick.lower()
#    else:
#        tagTargeted, content = trigger.group(2).split(None, 1)
#        tagTargeted = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagTargeted)
#        tagTargeted = tagTargeted.lower()
#        content = content.split("|")
#    Db = willie.db.connect()
#    cur = Db.cursor()
#    for tagcontent in content:
#        try:
#            tagcontent = tagcontent.strip()
#            tagcontent = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagcontent)
#            if tagcontent != "":
#                params = (tagTargeted, tagcontent.upper())
#                willie.say(str(params))
#                cur.execute('Delete from tag_table where tagTarget="test" and UPPER(tag)="VORE" ')
#                Db.commit()
#        except:
#            if len(content) == 1:
#                raise
#    willie.reply('I have removed the tag(s) for you.')
#    Db.close()

@commands('hostmask')
def hostmask(willie, trigger):
    willie.say(trigger.hostmask.split('@', 1)[-1])

@commands("banme")
def testsomethings(willie, trigger):
    if re.search("ACTION", trigger.bytes):
        willie.say("true")
    #willie.say(unicode.format(u"TBAN {0} {1} {2}", trigger.sender,trigger.group(2), trigger.
    willie.write(("TBAN",trigger.sender,trigger.group(2), "m:"+trigger.nick))

@rule(".*teststhis")
def repearacrion(willie, trigger):
    willie.reply(trigger.bytes)

@commands("run")
def runcommand(willie, trigger):
    if perm_chk(trigger.hostmask, "Ow", willie):
        say = willie.say
        exec trigger.group(2)

@commands("ReID")
def reidentify(willie, trigger):
    if perm_chk(trigger.hostmask, "Ow", willie):
        willie.msg('nickserv', "identify Burpyhooves " + willie.config.core.nickserv_password)
        willie.write(('NICK',trigger.group(2),))


@commands("bsay")
def bsay(willie, trigger):
    if perm_chk(trigger.hostmask, "Op", willie) and trigger.group(2):
        if not "#" == trigger.group(2)[0]:
            channel = trigger.sender
            message = trigger.group(2)
        else:
            channel, message = trigger.group(2).split(None,1)
        willie.msg(channel, message)

@commands("bdo")
def bdo(willie, trigger):
    if perm_chk(trigger.hostmask, "Op", willie) and trigger.group(2):
        if not "#" == trigger.group(2)[0]:
            channel = trigger.sender
            message = trigger.group(2)
        else:
            channel, message = trigger.group(2).split(None,1)
        willie.write(("PRIVMSG", channel), "\x01ACTION "+message+"\x01")

@commands("restart")
def restartthis(willie, trigger):
    if perm_chk(trigger.hostmask, "Ow", willie):
        if trigger.group(2) and willie.memory['restartpass']:
            if willie.memory['restartpass'] == trigger.group(2):
                call(["/etc/init.d/burpybot restart"], shell = True)
        else:
            willie.memory['restartpass'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            willie.reply('Please retype !restart %s' % willie.memory['restartpass'])