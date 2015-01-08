"""
choose.py - A simple willie module that chooses randomly between arguments
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""

import random

from willie.module import commands, example

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

@commands(u'choose')
@example(ur"!choose 2, The Hobbit, Ender's Game, The Golden Compass")
def choose(willie, trigger):
    """Returns a random selection of comma separated items provided to it.
    Chooses a subset if the first argument is an integer."""
    
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    willie.debug(u"choose.py", u"==============", u"verbose")
    willie.debug(u"choose.py", u"Module called.", u"verbose")
    # Parse the provided arguments into a list of strings
    willie.debug(u"choose.py trigger.args", trigger.args, u"verbose")
    __, __, list = trigger.args[1].partition(u' ')
    # Test for csv or space separated values
    if u',' in trigger.args[1]:
        willie.debug(u"choose.py list", list, u"verbose")
        args = list.split(u',')
        willie.debug(u"choose.py args", args, u"verbose")
    elif u' or ' in trigger.args[1]:
        args = list.split(u' or ')
    else:
        args = list.split()
    # Strip the strings
    for i, str in enumerate(args):
        args[i] = str.strip()
    willie.debug(u"choose.py", args, u"verbose")
    if len(args) > 1:
        # If the first argument is an int, we'll want to use it
        if args[0].isdigit():
            willie.debug(u"choose.py", u"First arg is a number.", u"verbose")
            # Cast the string to an int so it's usable
            choices = int(float(args.pop(0)))
            # Test for sanity
            if choices < len(args) and choices > 0:
                willie.debug(u"choose.py",
                             u"Choice number is sane.",
                             u"verbose"
                             )
                # run through choices and add the selections to a list
                choice_list = []
                for i in range(choices):
                    last_choice = random.choice(args)
                    args.remove(last_choice)
                    willie.debug(u"choose.py",
                                 u"Adding Choice " + last_choice,
                                 u"verbose")
                    choice_list.append(last_choice)
                willie.reply(u', '.join(choice_list))
            else:
                # The number is too small or too large to be useful
                willie.debug(u"choose.py",
                             u"Choice number is not sane.",
                             u"verbose")
                willie.reply(u"Hmm, how about everything?")
        else:
            # Just choose one item since no number was specified
            willie.debug(u"choose.py",
                         u"First arg is not a number.",
                         u"verbose"
                         )
            choice = random.choice(args)
            willie.reply(choice)
    else:
        # <=1 items is not enough to choose from!
        willie.debug(u"choose.py", u"Not enough args.", u"verbose")
        willie.reply(u"You didn't give me enough to choose from!")


if __name__ == "__main__":
    print __doc__.strip()