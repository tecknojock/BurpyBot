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


basic_lick = (u"(?i)((lick(ed|s|ing)?)|(lapp?(ed|ing|s)?)|(taste?(s|d|ing)?)|(slurp(s|ed|ing)))")
basic_drool = (u"(?i)((chew(s|ed|ing)?)|(nomf(s|ed|ing)?)|(drool(s|ed|ing)?)|(nibble?(s|ed|ing)?)|(slobber(s|ed|ing)?))/son")
basic_eat = u"(?i)((eat(s|ing)?)|ate|(swallow(s|ed|ing)?)|(nom(s|m(ed|ing))?)|(slurp|gulp|swallow)(s|ed|ing)?(up|down))"
basic_all = u"(?i)every\s?(body|one|pony|pone|poni|pont)"
basic_self = u"(?i)(((it|him|her|their|them)sel(f|ves))|Burpy\s?Hooves)"
basic_any = u"(?i)(some|any)\s?(body|one|pony|pone|poni|pont)|random"
basic_boop = u"boop(s|ing)"


@rule(
    u"(.*?\s" + basic_lick +
    u"\s$nickname.*?)"
)
def licked(willie, trigger):
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1,3))
    willie.action(random.choice([
                              u"blushes profusely.",
                              u"Meeps!",
                              u"enjoys the feel of the tongue crossing his body.",
                              unicode.format(u"wimpers and pulls away from {0}.", trigger.nick),
                              unicode.format(u"shudders as {0} licks him.", trigger.nick),
                              unicode.format(u"squirms at {0}'s advances.", trigger.nick)
                              ]))

@rule(
    u"(.*?\s" + basic_drool +
    u"\s$nickname.*?)"
)
def drool(willie, trigger):
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1,3))
    willie.action(random.choice([
                              u"squeaks and pulls away from %s." % (trigger.nick,),
                              u"whimpers and shivers.",
                              u"shoves %s off of them." % (trigger.nick),
                              unicode.format(u"squirms at {0}'s advances.", trigger.nick)
                              ]))

@rule(
    u"(.*?\s" + basic_boop +
    u"\s$nickname.*?)"
)
def boop(willie, trigger):
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1,3))
    willie.action(random.choice([
                              u'boops %s back softly and says "Boop!"' % (trigger.nick,),
                              u"scrunches his nose.",
                              u"opens his mouth and nibbles on %s's hoof." % (trigger.nick),
                              u"grabs the hoof and gulps it down hungilry, following it with the rest of %s." % (trigger.nick)
                              ]))

@commands("lick")
def licks(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if hasattr(trigger.group(2), "lower"):
        if re.match(basic_any,trigger.group(2)):
            target = random.choice(willie.memory['chan_nicks'][trigger.sender])
        else:
            target = re.sub(u"[\u0000-\u001F\u007F-\u009F]", "", trigger.group(2))
        if re.search(basic_all,target):
             willie.action(random.choice([
                                 unicode.format(u"teleports between ponies giving them a lick."),
                                 unicode.format(u"takes a taste of every pony in the room."),
                                 ]))
             return
        elif re.search( basic_self, target):
             willie.action(random.choice([
                                 unicode.format(u'licks his muzzle staring at {0} hungrily.', trigger.nick),
                                 unicode.format(u'runs his tongue through his fur, smoothing it out.'),
                                 ]))
             return
    else:
        target = trigger.nick
    willie.action(random.choice([
                                 unicode.format(u"licks over {0}'s muzzle sensually.", target),
                                 unicode.format(u"tastes {0} and murrs in delight.", target),
                                 unicode.format(u"approaches {0} with a hungry look in his eye and licks them.", target)
                                 ]))


@commands("cockvore")
def cockvore(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if hasattr(trigger.group(2), "lower"):
        if re.match(basic_any,trigger.group(2)):
            target = random.choice(willie.memory['chan_nicks'][trigger.sender])
        else:
            target = re.sub(u"[\u0000-\u001F\u007F-\u009F]", "", trigger.group(2))
        if re.search(basic_all,target):
             willie.action(random.choice([
                                          u"engulfs everyone with his cock, reveling in his squirming balls."
                                          u"shrings everypony in the room and stuffs them one by one down his dick."
                                 ]))
             return
        elif re.search( basic_self, target):
             willie.action(random.choice([
                                          u"shoves his own head into his cock, and jacks off from the inside.",
                                          unicode.format(u"raises an eyebrow at {0}. \"you can't cock vore yourself you silly goose.\"", trigger.nick)
                                 ]))
             return
    else:
        target = trigger.nick
    willie.action(random.choice([
                                 unicode.format(u"shoves {0} down his cock face first, patting the bulge.", target),
                                 unicode.format(u"pushes {0} down his shaft, turns them to cum, then shoots them out.", target),
                                 unicode.format(u"slides {0} into his cock and sloshes them around in his pendulous testicles.", target),
                                 unicode.format(u" pulls {0} down his dick and melts them into cum.", target)
                                 ]))

@rule(
    u"(.*?\s" + basic_eat +
    u"\s$nickname.*?)"
)
def eaten(willie, trigger):
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    time.sleep(random.uniform(1,3))
    willie.action(random.choice([
                              unicode.format(u"struggles to get free from {0}'s stomach with all his might.", trigger.nick),
                              unicode.format(u"relaxes in the comfort of {0}'s stomach.", trigger.nick)
                              
                              
                              
                              ])) 
                             
@commands("eat")
def eat(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if hasattr(trigger.group(2), "lower"):
        if re.match(basic_any,trigger.group(2)):
            target = random.choice(willie.memory['chan_nicks'][trigger.sender])
        else:
            target = re.sub(u"[\u0000-\u001F\u007F-\u009F]", "", trigger.group(2))
        if re.search(basic_all,target):
             willie.action(random.choice([
                                 unicode.format(u"runs around the room swallowing them one by one."),
                                 unicode.format(u"shrinks the entire room with a flash and eats everypony in a single gulp."),
                                 unicode.format(u"slurps down the planet and everypony on it.")
                                 ]))
             return
        elif re.search( basic_self, target):
             willie.action(random.choice([
                                 unicode.format(u'crosses his hooves, "Don\'t be silly {0}."', trigger.nick),
                                 unicode.format(u'gives {0} a confused look. "How am I supposed to do that?"', trigger.nick),
                                 unicode.format(u"noms on his own hoof."),
                                 unicode.format(u"chases his own tail trying to latch on.")
                                 ]))
             return
    else:
        target = trigger.nick
    willie.action(random.choice([
                                 unicode.format(u"swallows {0} in a single gulp.", target),
                                 unicode.format(u"quickly gulps down {0} and slurps up their tail.", target),
                                 unicode.format(u"eats {0} in a flash, murring as they wiggle in his belly.", target),
                                 unicode.format(u"teleports {0} directly into his gut.", target),
                                 unicode.format(u"shrinks {0} down to a small size and plays with them in his mouth before eating them.", target)
                                 ]))
'''slow chat, tummy gurgles, growls, rumbles, getting hungry, burps'''                      

@commands("inflate")
def inflate(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if hasattr(trigger.group(2), "lower"):
        if re.match(basic_any,trigger.group(2)):
            target = random.choice(willie.memory['chan_nicks'][trigger.sender])
        else:
            target = re.sub(u"[\u0000-\u001F\u007F-\u009F]", "", trigger.group(2))
        if re.search(basic_all,target):
             #willie.action(random.choice([
             #                    unicode.format(u""),
             #                    ]))
             return
        elif re.search( basic_self, target):
             willie.action(random.choice([
                                 unicode.format(u"attaches an airhose to his own plothole and turns on the switch."),
                                 unicode.format(u"shoves a bicycle pump tube down his throat and begins to pump."),
                                 unicode.format(u"steals a fire engine and feeds himself the fire hose."),
                                 unicode.format(u"opens a can of compressed air and swallows it.")
                                 ]))
             return
    else:
        target = trigger.nick
    willie.action(random.choice([
                                 unicode.format(u"attaches an airhose to {0}'s plothole and turns on the switch.", target),
                                 unicode.format(u"shoves a bicycle pump tube down {0}'s throat and begins to pump.", target),
                                 unicode.format(u"steals a fire engine and forcefeeds {0} the fire hose.", target),
                                 unicode.format(u"gives aggressive mouth to mouth to {0}", target)
                                 ]))       