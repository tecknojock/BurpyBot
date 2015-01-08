import time
import random
import re
from willie.tools import Nick
import urllib
import urllib2
import math

from willie.module import commands, example, priority, rule, rate, event

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
    
    cur.execute('create table if not exists lck_table (nick , lck, Primary Key (nick))')
    listoftags = cur.fetchall()
    Db.close()

@rule('[1-9][0-9]*d[1-9][0-9]*')
def rollany1(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    message = trigger.partition(" ")
    roll = re.match("[0-9]+d[0-9]+", message[0]).group(0)
    rnumb = roll.partition("d")[0]
    die = roll.partition("d")[2]
    charmax = 450 - len(roll)-8-len(message[2])
    if (len(die)+2)*int(rnumb) > charmax:
        rnumb = str(int(charmax/(len(die)+2))+1)
        roll = unicode.format("%sd%s" % (rnumb, die))
    try:
        numbers = re.sub("\s",", ",urllib2.urlopen(urllib2.Request(unicode.format(u"http://www.random.org/integers/?num={0}&min=1&max={1}&col=1&base=10&format=plain&rnd=new", rnumb, die))).read().strip())
    except:
        numbers = list()
        for count in range(0, int(rnumb)):
            numbers.append(random.randint(1,int(die)))
    if int(rnumb) == 1:
        try: 
            int(numbers)
        except:
            numbers = numbers[0]
        try:
            nick = trigger.nick.lower()
            Db = willie.db.connect()
            cur = Db.cursor()
            params = (nick,)
            cur.execute('SELECT lck FROM lck_table WHERE nick=?', params)
            lck = cur.fetchall()
            if lck == []:
                lck = 0
            else:
                lck = lck[0][0]
        finally:
            Db.close()
        try:
            limit = eval(re.search(u"[0-9]+\s?[+-]?\s?[0-9]*", message[2].encode()).group(0))
            if int(numbers) > limit and int(numbers) != int(die):
                willie.say(unicode.format(u"\u00034Failure ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
            elif int(numbers) == int(die) or (int(die) == 100 and int(numbers) >= 94+math.floor(lck/2)):
                willie.say(unicode.format(u"\u000313Critical Failure ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
            elif int(numbers) == 1 or (int(die) == 100 and int(numbers) <= lck):
                willie.say(unicode.format(u"\u000310Critical Success ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
            else:
                willie.say(unicode.format(u"\u00039Sucess ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
        except:
            if  int(numbers) == int(die) or (int(die) == 100 and int(numbers) >= 94+math.floor(lck/2)):
                willie.say(unicode.format(u"\u000313Critical Failure ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
            elif int(numbers) == 1 or (int(die) == 100 and int(numbers) <= lck):
                willie.say(unicode.format(u"\u000310Critical Success ({2}) [{0}] : {1}\u0003", numbers, message[2].encode(), roll.encode()))
            else:
                willie.say(unicode.format(u"({2}) [{0}] : {1}", numbers, message[2].encode(), roll.encode()))
    else:
       willie.say(unicode.format(u"({2}) [{0}] : {1}", numbers, message[2].encode(), roll.encode()))

@commands("luck")
def luck(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    nick = trigger.nick.lower()
    luck = int(trigger.group(2))
    if 0<luck and luck <11:
        try:
            Db = willie.db.connect()
            cur = Db.cursor()
            params = (nick,)
            cur.execute('Delete from lck_table where nick=?', params)
            params = (nick, luck)
            cur.execute('Insert Into lck_table VALUES (?, ?)', params)
            Db.commit()
            willie.reply("Luck Updated")
        finally:
            Db.close()
    else:
        willie.reply("Luck must be between 1 and 10")
        return

@commands("roulette")
def roulette(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    willie.reply(random.choice(willie.memory['chan_nicks'][trigger.sender]))
