"""
info.py - willie Information Module
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""

from willie.module import commands, rule, example, priority

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

@rule(u'$nick' '(?i)(help|doc) +([A-Za-z]+)(?:\?+)?$')
@example(u'!help seen')
@commands(u'help')
@priority(u'low')
def doc(willie, trigger):
    """Shows a command's documentation, and possibly an example."""
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return

    name = trigger.group(2)
    if (not hasattr(name, 'lower')):
        willie.reply(u"For help, do '!help example' where example is the " +
                     u"name of the command you want help for. " + "For a list of commands use !commands.")
        return
    name = name.lower()

    if (name in willie.doc
            and not willie.doc[name][0].startswith(u"ADMIN")):
        willie.reply(willie.doc[name][0])
        if willie.doc[name][1]:
            willie.say(u'e.g. ' + willie.doc[name][1])


@commands(u'commands')
@priority(u'low')
def commands(willie, trigger):
    """Return a list of willie's commands"""
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if trigger.owner:
        names = u', '.join(sorted(willie.doc.iterkeys()))
    else:
        if (1 == 1):
            cmds = [i for i in sorted(willie.doc.iterkeys())
                    if not willie.doc[i][0].startswith(u"ADMIN")
                    and i not in [u'newoplist',
                                  u'listops',
                                  u'listvoices',
                                  u'blocks',
                                  u'part',
                                  u'quit'
                                  u'reload'
                                  ]  # bad hack for filtering admin cmds
                    ]
            names = u', '.join(sorted(cmds))
    willie.reply(u'Commands I recognise: ' + names + u'.')
    willie.reply((u"For help, do '!help example' where example is the " +
                  u"name of the command you want help for."))


@rule('$nick' r'(?i)help(?:[?!]+)?$')
@priority('low')
def help(willie, trigger):
    if not perm_chk(trigger.hostmask, "Ia", willie):
        return
    response = (
        u'Hi! I\'m %s and I\'m a pony. Say "!commands" to me in private ' +
        u'for a list of the things I can do. Say hi to my master, %s!'
    ) % (willie.nick, willie.config.owner)
    willie.reply(response)


if __name__ == '__main__':
    print __doc__.strip()