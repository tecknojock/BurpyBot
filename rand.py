import time
import random
import re
from willie.tools import Nick
import urllib
import urllib2
import math
import heapq

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
    cur.execute('create table if not exists system_table (nick , direction, Primary Key (nick))')
    listoftags = cur.fetchall()
    Db.close()

@rule('[1-9][0-9]*d[1-9][0-9]*')
def rollany1(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    message = trigger.partition(" ")
    roll = re.match("[0-9]+d[0-9]+([hl][0-9]+)?([+*-][0-9])*", message[0]).group(0)
    advantagetype = re.findall(r"[hl]",roll)
    rollwithmath = re.split(r"([+*-])",roll,1)
    rolled = re.split(r"[dhl]", rollwithmath[0])
    rnumb = rolled[0]
    die = rolled[1]
    advantage = 0
    try:
        mathstuff = rollwithmath[1]+rollwithmath[2]
    except:
        mathstuff = "*1"
    try:
        if advantagetype[0] == "h":
            advantage = int(rolled[2])
        elif advantagetype[0] == "l":
            advantage = -int(rolled[2])
    except:
        pass

    charmax = 450 - len(roll)-8-len(message[2])
    if (len(die)+2)*int(rnumb) > charmax:
        rnumb = str(int(charmax/(len(die)+2))+1)
        roll = unicode.format("%sd%s" % (rnumb, die))
    try:
        numbers = re.findall("[0-9]+",urllib2.urlopen(urllib2.Request(unicode.format(u"http://www.random.org/integers/?num={0}&min=1&max={1}&col=1&base=10&format=plain&rnd=new", rnumb, die))).read().strip())
    except:
        numbers = list()
        for count in range(0, int(rnumb)):
            numbers.append(random.randint(1,int(die)))
    if advantage != 0:
        if advantage >0:
            numbers = heapq.nlargest(advantage, numbers)
        else:
            numbers = heapq.nsmallest(abs(advantage), numbers)
    if int(rnumb) == 1 or abs(advantage) == 1:
        try: 
            int(numbers)
        except:
            numbers = numbers[0]
        adjnumbers = eval(str(numbers)+mathstuff)
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
            if int(adjnumbers) > limit and int(adjnumbers) != int(die):
                willie.say(unicode.format(u"\u00039Sucess ({2}) [{0} ({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
            elif int(adjnumbers) == int(die) or (int(die) == 100 and int(adjnumbers) >= 94+math.floor(lck/2)):
                willie.say(unicode.format(u"\u000310Critical Success ({2}) [{0} ({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
            elif int(adjnumbers) == 1 or (int(die) == 100 and int(adjnumbers) <= lck):
                willie.say(unicode.format(u"\u000313Critical Failure ({2}) [{0} ({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
            else:
                willie.say(unicode.format(u"\u00034Failure ({2}) [{0}({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
        except:
            if  int(adjnumbers) == int(die) or (int(die) == 100 and int(adjnumbers) >= 94+math.floor(lck/2)):
                willie.say(unicode.format(u"\u000310Critical Success ({2}) [{0} ({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
            elif int(adjnumbers) == 1 or (int(die) == 100 and int(adjnumbers) <= lck):
                willie.say(unicode.format(u"\u000313Critical Failure ({2}) [{0} ({3})] : {1}\u0003", numbers, message[2].encode(), roll.encode(), adjnumbers))
            else:
                willie.say(unicode.format(u"({2}) [{0}({3})] : {1}", numbers, message[2].encode(), roll.encode(), adjnumbers))
    else:
        willie.say(unicode.format(u"({2}) {0} : {1}", ", ".join(str(x) for x in numbers), message[2].encode(), roll.encode()))

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
