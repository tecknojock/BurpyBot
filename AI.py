# coding=utf8
"""
ai.py - A simple willie module for misc silly ai
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""
import time
import random
import re
from willie.tools import Nick

from willie.module import rule, rate, priority

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


basic_thanks = u"ty|thanks|gracias|thank\s?you|thank\s?ya|ta"
basic_woo = u"(wo[o]+[t]?)|(y[a]+y)|(whe[e]+)"
basic_badbot = (u"bad|no|stop|dam[mnit]+?|ffs|stfu|shut (it|up)|don'?t|wtf|" +
                u"(fuck[s]?\s?(sake|off)?)")
n_text = u"[A-Za-z0-9,.'!\s]"
basic_slap = u"slap[p]?[s]?|hit[s]?|smack[s]?\b"
random.seed()

def setup(willie):
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists nini_table (user , count, timestamp, Primary Key (user))')
    Db.close()

@rule(
    u"(^$nickname[,:\s]\s(%s)($|[\s,.!]))|" % basic_thanks +
    (u"([A-Za-z0-9,.!\s]*?(%s)[^A-Za-z0-9]" +
    u"([A-Za-z0-9,.!\s]*?$nickname))") % basic_thanks
)
def ty(willie, trigger):
    '''Politely replies to thank you's.'''
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    if not set(trigger.args[1].lower().split()).intersection(set([u'not',
                                                                  u'no',
                                                                  u'at'])):
        time.sleep(random.uniform(1, 3))
        willie.reply(
            random.choice([
                u"Yep",
                u"You're welcome",
                u"Certainly",
                u"Of course",
                u"Sure thing"
            ]) +
            random.choice([".", "!"])
        )

@rule(
    u"(((^|%s+?\s)$nickname[.,-:]\s(%s+?\s)?(%s)([^A-Za-z0-9]|$))|" % (
    n_text, n_text, basic_badbot) +
    u"((^|%s+?\s)((%s)\s)(%s*?\s)?$nickname([^A-Za-z0-9]|$))|" % (
        n_text, basic_badbot, n_text) +
    u"(($nickname%s+?)(%s)([^A-Za-z0-9]|$)))" % (n_text, basic_badbot)
)
def badbot(willie, trigger):
    '''Appropriate replies to chastening'''
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1, 3))
    if trigger.owner:
        willie.say(random.choice([
            u"[](/sadderpy)",
            u"[](/raritysad)",
            u"[](/sadtwilight2)",
            u"[](/scootasad)",
            u"[](/seriouslysadaj)",
            u"[](/dashiesad)",
            u"[](/fscry)",
            u"[](/aj05)",
            u"[](/pinkiefear)"
        ]))
    elif Nick(trigger.nick) == Nick('DarkFlame'):
        willie.say(random.choice(
            u'[](/ppnowhy "Why are you so mean to me?!")',
            u'[](/ppnowhy "Why do you hate me?!")'
        ))
    elif random.uniform(0, 1) < 0.1:
        willie.reply(random.choice([
            u"[](/derpsrs)",
            u"[](/cheersrsly)",
            u"[](/fluttersrs)",
            u"[](/cewat)",
            u"[](/lyrawat)",
            u"[](/ppwatching)",
            u"[](/watchout)",
            u"[](/dashiemad)",
            u"[](/ppumad)"
        ]))

@rule(
    u"(^!(%s))|" % basic_slap +
    u"(\001ACTION [A-Za-z0-9,.'!\s]*?(%s)" % basic_slap +
    u"[A-Za-z0-9,.'!\s]+?$nickname)|" +
    u"(\001ACTION [A-Za-z0-9,.'!\s]+?$nickname" +
    u"[A-Za-z0-9,.'!\s]*?(%s)$)" % basic_slap
)
def slapped(willie, trigger):
    time.sleep(random.uniform(1, 3))
    willie.reply(random.choice([
        u'Stop that!',
        u'Hey!',
        u'Violence is not the answer!',
        u"Didn't your mother teach you not to hit?"
    ]))
    willie.reply(u"[](/pinkieslap)")


hi_prefix = ur"($nickname[:,]?\s+)"
hi_meat = ur"(hello|hi|ahoy|sup|hey|yo|((good|g)?'?\s?((afternoon)|(morn(ing)?)|(eve(ning)?))))"
hi_all = ur"(y?'?all|(every\s?(body|one|pon[tiye]))|#vore|(vore)?\s?poni?e?t?s|chattybox|" + \
    ur"folks|guys|peoples?|$nickname)"
hi_to_fineline = hi_prefix + hi_meat + u'(\W?$)'
hi_to_all = hi_meat + ur"[,]?\s+" + hi_all + u'(\W?$)'


@rule(ur"(" + hi_to_fineline + ur")|" + ur"(" + hi_to_all + ur")")
@rate(300)
def hi(willie, trigger):
    """Replies to greetings."""
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    message = random.choice([u"Hi", u"Hello", u"Yo", u"Hey", u"Ahoy"])
    if (not not re.match(u'.*?morning', trigger.bytes)) & (random.uniform(0,1) > .5):
        message = random.choice([u'Good morning', u"G'morning", u"morning"])
    if (not not re.match(u'.*?noon', trigger.bytes)) & (random.uniform(0,1) > .5):
        message = random.choice([u'Good afternoon', u"G'afternoon", u"afternoon"])
    punctuation = random.choice([u".", u"", u"!"])
    time.sleep(random.uniform(0, 3))
    if random.uniform(0, 1) > 0.5 and not re.match(u"\A\(", trigger.bytes):
        willie.reply(message + punctuation)
    elif re.match(u"\A\(", trigger.bytes):
        willie.say(unicode.format(u"({0} {1}{2})", message, trigger.nick, punctuation))
    else:
        willie.say(message + u" " + trigger.nick + punctuation)


@rule(ur'.*$nickname\:?,?\s+Are you a bot|.*$nickname (is )?a bot')
@rate(0)
def isbot(willie, trigger):
    """Replies to queries about fineline being a bot"""
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1, 2))
    willie.say(random.choice(
        [u"Nope, I'm just fast.",
         u"Nah, I just type really fast and know a lot.",
         u"What makes you think that?",
         u"lolno",
         u"Uh.....no?"]
    ))
    time.sleep(random.uniform(3, 5))
    willie.say(random.choice(
        [u"Come on, don't you see these hooves?",
         u"If I were a bot, how come I have hooves?",
         u"See? I have hooves! *wiggles hooves*",
         u"I'm kinda hurt you'd even suggest such a thing...",
         u"Are you a bot?",
         u"Besides, sentience is a hard thing to prove..."]
    ))


night_prefix = ur"($nickname\:?,?\s+)"
night_meat = ur"((good|g)?\s?'?(n'?i'?g'?h'?t|bye)|(later(s?))|nini)"
night_all = ur"(y?'?all|(every\s?(body|one|pon[yei]))|#vore|" + \
    u"folks|guys|peoples?|poni?es|$nickname)"
night_to_fineline = night_prefix + night_meat
night_to_all = ur".*?" + night_meat + ur",?\s+" + night_all
night_universal = ur".*?((time (for me)?\s?(to|for)\s?((go to)|(head))?\s?" + \
    u"(to )?(bed|sleep))|" + \
    u"(I\s?a?'?m.*?((((going to)|(gonna)) ((go)|(head))?)|(heading))" + \
    u"\s?((off)|(go))?\s?(to )?(bed|sleep|crash|(pass out)|bread)))"


@rule(
    ur"(" + night_to_fineline + ur")|" +
    ur"(" + night_to_all + ur")|" +
    ur"(" + night_universal + ur")"
)
@priority('high')
@rate(600)
def night(willie, trigger):
    """Responds to people saying good night"""
    if not perm_chk(trigger.hostmask, "Ia", willie) or re.search("(soon|a (bit|little while)|later)|([\"\'].*?((" + night_to_fineline + ur")|" + ur"(" + night_to_all + ur")|" + ur"(" + night_universal + ur")).*?[\"\'])", trigger.bytes):
        return
    if perm_chk(trigger.hostmask, "Gb", willie) and (re.match(u'.*?(night)|(nini)', trigger.bytes) or re.match(night_universal, trigger.bytes)):
        Db = willie.db.connect()
        cur = Db.cursor()
        user = trigger.hostmask.split('@', 1)[-1]
        params = (user,)
        cur.execute('SELECT timestamp FROM nini_table WHERE user=?;', params)
        timestamp = cur.fetchone()
        cur.execute('SELECT count FROM nini_table WHERE user=?;', params)
        count = cur.fetchone()
        if timestamp == None:
            params = (user, 1, time.time(),)
            cur.execute('Insert Into nini_table values (?,?,?);', params)
            count = 1
        else:
            if (timestamp[0] + (3*60*60) > time.time()) and re.match(u'.*?(night)|(nini)', trigger.bytes) or re.match(night_universal, trigger.bytes) and not re.search("soon|a (bit|little while)", trigger.bytes):
                count = count[0]+1
                params = (count, time.time(), user,)
                cur.execute('update nini_table set count=?, Timestamp=? where user=?;', params)
            elif re.match(u'.*?(night)|(nini)', trigger.bytes) or re.match(night_universal, trigger.bytes):
                count = 1
                params = (count, time.time(),user,)
                cur.execute('update nini_table set count=?, Timestamp=? where user=?;', params)
        Db.commit()    
        Db.close()
        if (random.randint(1,100) < 75/count):
            if trigger.sender in ["#vore", "#vore2", "#vore3", "#vore4", "#vore5", "#vore6", "#vore-ooc", "#vore-con", "#vore-drama"]:
                sender = "#vore"
            else:
                sender = trigger.sender
            randd = random.randint(1,2)
            if randd < 2 and count > 1 and not re.match(u"\A\(", trigger.bytes):
                willie.action(random.choice([
                                unicode.format(u"marks '{0} says they're going to bed, but doesn't actually go to bed' on their #vore bingo board.", trigger.nick),
                                unicode.format(u"predicts that {0} will be back soon.", trigger.nick),
                                unicode.format(u"rolls his eyes. \"You've said that {0} times {1}!\"", count, trigger.nick), 
                                unicode.format(u"rolls his eyes. \"You've said that {0} times {1}!\"", count, trigger.nick) 
                                ]))
            elif randd < 2 and not re.match(u"\A\(", trigger.bytes):
                willie.action(random.choice([
                                unicode.format(u"marks '{0} says they're going to bed, but doesn't actually go to bed' on their {1} bingo board.", trigger.nick, sender),
                                unicode.format(u"predicts that {0} will be back soon.", trigger.nick),
                                ]))
            elif not re.match(u"\A\(", trigger.bytes):
                willie.say(random.choice([
                                unicode.format(u"See you in 10 minutes or so {0}", trigger.nick),
                                unicode.format(u"{0}: I'll believe it when I see it.", trigger.nick),
                                unicode.format(u"Please do try to go to sleep this time {0}", trigger.nick),
                                ]))
            else:
                willie.say(random.choice([
                                unicode.format(u"(See you in 10 minutes or so {0})", trigger.nick),
                                unicode.format(u"({0}: I'll believe it when I see it.)", trigger.nick),
                                unicode.format(u"(Please do try to go to sleep this time {0})", trigger.nick),
                                ]))
            return
    if re.match(u'.*?(night)|(nini)', trigger.bytes) or re.match(night_universal, trigger.bytes):
        message = random.choice([u"Goodnight", u"'Night", u"Later", u"Bye", u"Sleep Well", u"Rest Well"])
    else:
        message = random.choice([u"Later", u"Bye"])
    punctuation = random.choice([u".", u"", u"!"])
    # Test statment to filter negetive statements
    willie.debug(u"ai_night.py:night", trigger.bytes, u"verbose")
    # Use a set intersection to filter triggering lines by keyword
    if not set(trigger.args[1].lower().split()).intersection(set([u'not',
                                                                  u'no',
                                                                  u'at'
                                                                  ])):
        time.sleep(1)
        if random.uniform(0, 1) > 0.5 and not re.match(u"\A\\(", trigger.bytes):
            willie.reply(message + punctuation)
        elif re.match(u"\A\(", trigger.bytes):
            willie.say(unicode.format(u"({0} {1}{2})", message, trigger.nick, punctuation))
        else:
            willie.say(message + u" " + trigger.nick + punctuation)
"""
def smart_action(willie, trigger):
    '''Hopefully a flexible, fun action system for admins'''
    willie.debug("ai:derp", "triggered", "verbose")
    willie.debug("ai:derp", trigger.nick, "verbose")
    willie.debug("ai:derp", trigger.args, "verbose")
    willie.debug("ai:derp", "admin: " + str(trigger.admin), "verbose")
    willie.debug("ai:derp", "owner: " + str(trigger.owner), "verbose")
    willie.debug("ai:derp", "isop: " + str(trigger.isop), "verbose")
basic_smart = "would you kindly|please|go"
smart_action.rule = ("^$nickname[:,\s]+(%s)[A-Za-z0-9,'\s]+(NICKNAME)" +
    "(a|an|the|some)(OBJECT)?")
smart_action.priority = 'medium'
"""


@rule(ur'^$nickname\s?[!\.]\s?$')
def nick(willie, trigger):
    message = trigger.nick
    if re.match(willie.nick.upper(), trigger.bytes):
        message = message.upper()
    if re.findall('!', trigger.bytes):
        willie.say(u'%s!' % message)
    else:
        willie.say(u'%s.' % message)


if __name__ == "__main__":
    print __doc__.strip()
