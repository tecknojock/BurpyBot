"""
tags.py - A willie module to tag words
Copyright 2013, TecknoJock
Licensed under the Eiffel Forum License 2.

"""

from willie.tools import Nick
from willie.module import commands, example, priority, rule, event, thread, unblockable
import os.path
import re
import threading
import time
import traceback
import random
import string
from copy import deepcopy


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

sunset = 60*60*24*30 #sunsets hostmasks/nicks after 30 days
re_hostname = re.compile(r':\S+\s311\s\S+\s(\S+)\s\S+\s(\S+)\s\*')

class UserID(Nick):
    
    def __new__(cls, ident, nick=None):
        s = Nick.__new__(cls, ident)
        s.nicks = [nick]
        return s
        
    def __eq__(self, other):
        if isinstance(other, NickPlus) and \
                (self.hostname is not None) and (other.hostname is not None):
            return self._lowered == other._lowered or self.hostname == other.hostname
        return self._lowered == Nick._lower(other)
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__str__())

class NickPlus(Nick):
    _hostname = None

    def __new__(cls, nick, host=None, ident=None):
        s = Nick.__new__(cls, nick)
        s.ident = ident
        s.hostname = host
        return s

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        assert isinstance(value, basestring) or value is None
        self._hostname = value

    def __eq__(self, other):
        if isinstance(other, NickPlus) and \
                (self.hostname is not None) and (other.hostname is not None):
            return self._lowered == other._lowered or self.hostname == other.hostname
        return self._lowered == Nick._lower(other)

    def __hash__(self):
        return 0  # Fuck the police

    def __repr__(self):
        return '%s(%s - %s)' % (self.__class__.__name__, self.__str__(), self._hostname)


def setup(willie):
    willie.memory['chan_nicks'] = {}
    willie.memory['chan_ids'] = {}
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists hostmasktrack_table (hostmask , userid, timestamp, Primary Key (hostmask))')
    cur.execute('create table if not exists nickstrack_table (nick, userid, timestamp, Primary Key (nick))')
    Db.close()
    if 'nick_lock' not in willie.memory:
        willie.memory['nick_lock'] = threading.Lock()
    willie.memory['whois_time'] = {}
    refresh_nicks(willie)

def refresh_nicks(willie):
    # The documentation disagrees, but coretasks.py seems to be keeping
    # willie.channels up to date with joins, parts, kicks, etc.
    for chan in willie.channels:
        with willie.memory['nick_lock']:
            chan = chan.lower
            willie.memory['chan_nicks'][chan] = {}
            willie.write(['NAMES', chan])
        time.sleep(0.5)


@rule('.*')
@event('311')
@unblockable
@priority('high')
@thread(False)  # Don't remove this or you'll break the willie.raw call
def whois_catcher(willie, trigger):
    '''Parses whois responses'''
    n, h = re_hostname.search(willie.raw).groups()
    n = n.lstrip('+%@&~')
    ident = getident(n, h,willie)
    who = NickPlus(n, h, ident)
    user = UserID(ident, who)
    #willie.debug(__file__, log.format(u'WHOIS %s: %s' % (who, h)), u'verbose')
    with willie.memory['nick_lock']:
        for chan in willie.memory['chan_nicks']:
            chan = chan.lower()
            # Replace all matching nicks with the updated nick from the whois
            # query, but only if the existing doesn't have a hostname. This is
            # to prevent the possibility of someone NICKing before the whois
            # gets processed and getting the new nick overwritten with the old.
            willie.memory['chan_nicks'][chan] = \
                [who if i.lower() == who.lower() and i.hostname is None else i for i in willie.memory['chan_nicks'][chan]]
            if who in willie.memory['chan_nicks'][chan]:
                if who.hostname == willie.memory['chan_nicks'][chan][willie.memory['chan_nicks'][chan].index(who)].hostname:
                    if user in willie.memory['chan_ids'][chan]:
                        willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(user)].nicks.extend(user.nicks)
                    else:
                        willie.memory['chan_ids'][chan].append(deepcopy(user))


@rule(u'.*')
@event('353')
@unblockable
@priority('high')
@thread(False)  # Don't remove this or you'll break the willie.raw call
def names(willie, trigger):
    '''Parses NAMES responses from the server which happen on joining a channel'''
    # Freenode example:
    # <<1412452815.61 :card.freenode.net 353 botname = #channelname :botname +nick1 nick2 nick3 nick_4
    buf = willie.raw.strip()  # willie.raw is undocumented but seems to be the raw line received
    #willie.debug(__file__, log.format(u'Caught NAMES response'), u'verbose')
    #try:
    with willie.memory['nick_lock']:
        #willie.debug(__file__, log.format('trigger:', trigger), 'verbose')
        unprocessed_nicks = re.split(' ', trigger)
        stripped_nicks = [i.lstrip('+%@&~') for i in unprocessed_nicks]
        #willie.debug(__file__, [i for i in stripped_nicks], u'verbose')
        nicks = [NickPlus(i, None,None) for i in stripped_nicks]
        channel = re.findall('#\S*', buf)[0]
        channel = channel.lower()
        if not channel:
            return
        willie.memory['chan_nicks'][channel] = []
        willie.memory['chan_nicks'][channel].extend(nicks)
        willie.memory['chan_ids'][channel] = []
        #willie.debug(__file__, log.format(u'Refeshing hosts for ', channel), 'verbose')
        for n in nicks:
            if n not in willie.memory['whois_time'] or willie.memory['whois_time'][n] < time.time() - 600:
                # Send the server a whois query if we haven't gotten one
                # yet/recently
                willie.memory['whois_time'][n] = time.time()
                willie.write(['WHOIS', n])
                time.sleep(0.5)  # This keeps our aggregate whois rate reasonable
            else:
                # If the nick has been recently WHOIS'd just use that one
                # so we don't spam the server
                for chan in willie.memory['chan_nicks']:
                    match = next((nick for nick in willie.memory['chan_nicks'][chan] if nick == n and nick.hostname), None)
                    if match:
                        #willie.debug(__file__, log.format(u'Just matched %s to %r in place of a whois.' % (n, match)), 'verbose')
                        break
                if match:
                    # This should never generate a value error since we just
                    # added it a few lines above
                    willie.memory['chan_nicks'][channel].remove(n)  # Remove the nick with None host
                    willie.memory['chan_nicks'][channel].append(match)  # Add nick with an actual host
                    if match.ident in willie.memory['chan_ids'][channel]:
                        willie.memory['chan_ids'][channel][willie.memory['chan_ids'][channel].index(match.ident)].nicks.append(match)
                    willie.memory['chan_ids'][channel].append(UserID(match.ident, match))
                else:
                    # Do nothing. If a nick wasn't matched then we haven't
                    # gotten the chance to process the appropriate whois
                    # response yet. That whois will come in and overwrite
                    # the entry with a None hostname.
                    pass

        #willie.debug(__file__, log.format(u'Done refeshing hosts for ', channel), 'verbose')
    #except:
        #willie.debug(__file__, log.format(u'ERROR: Unprocessable NAMES response: ', buf), u'warning')
        #print(traceback.format_exc())
        # refresh_nicks(bot)
        #willie.msg(willie.config.owner, u'A name entry just broke. Check the logs for details.')
        #pass

@rule(u'.*')
@event('JOIN')
@unblockable
@thread(False)
@priority('high')
def join(willie, trigger):
    name = NickPlus(trigger.nick, trigger.host)
    if not trigger.sender.startswith('#'):
        return
    ident = getident(trigger.nick, trigger.host,willie)
    name = NickPlus(trigger.nick,trigger.host,ident)
    with willie.memory['nick_lock']:
        if not trigger.sender.lower() in willie.memory['chan_nicks']:
            return
        if trigger.nick not in willie.memory['chan_nicks'][trigger.sender.lower()]:
            willie.memory['chan_nicks'][trigger.sender.lower()].append(name)
            if ident not in willie.memory['chan_ids'][trigger.sender.lower()]:
                willie.memory['chan_ids'][trigger.sender.lower()].append(UserID(ident,name))
            else:
                willie.memory['chan_ids'][trigger.sender.lower()][willie.memory['chan_ids'][trigger.sender.lower()].index(ident)].nicks.append(name)

@rule(u'.*')
@event('NICK')
@unblockable
@thread(False)
@priority('high')
def nick(willie, trigger):
    # Trigger doesn't come from channel. Any replies will be sent to user.
    # Old nick is in trigger.nick while new nick is in trigger and
    # trigger.sender
#    try:
    old_nick = trigger.nick
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (time.time(), trigger.upper(),)
    cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)
    Db.commit()
    Db.close()
    ident=getident(trigger.nick, trigger.host,willie) # Called so that it registers new nicks to the db but can break if the ident is already in use
    for chan in willie.memory['chan_nicks']:
        if old_nick in willie.memory['chan_nicks'][chan]:
            if willie.memory['chan_nicks'][chan][willie.memory['chan_nicks'][chan].index(old_nick)].ident is not None:
                ident = willie.memory['chan_nicks'][chan][willie.memory['chan_nicks'][chan].index(old_nick)].ident
                break
    
    new_nick = NickPlus(trigger, trigger.host, ident)
    with willie.memory['nick_lock']:
        for chan in willie.memory['chan_nicks']:
            if old_nick in willie.memory['chan_nicks'][chan]:
                willie.memory['chan_nicks'][chan].remove(old_nick)
                willie.memory['chan_nicks'][chan].append(new_nick)
                if ident in willie.memory['chan_ids'][chan]:
                    if old_nick in willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks:
                        willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks.remove(old_nick)
                    willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks.append(new_nick)
#    except:
#        pass



@rule(u'.*')
@event('QUIT')
@unblockable
@thread(False)
@priority('high')
def quit(willie, trigger):
    #willie.debug(__file__, log.format(u'Caught QUIT by %s (%s)' % (trigger.nick, trigger)), u'verbose')
    # Quitting nick is trigger.nick, trigger and trigger.sender contain quit
    # reason. Don't use trigger.sender to determine if the user is in a
    # channel!
#    try:
    name = trigger.nick
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (time.time(), name.upper(),)
    cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)
    params = (time.time(), trigger.host.upper(),)
    cur.execute('update hostmasktrack_table set timestamp=? where upper(hostmask)=?', params)
    Db.commit()
    Db.close()
    with willie.memory['nick_lock']:
        for chan in willie.memory['chan_nicks']:
            #willie.debug(__file__, log.format(u'Looking for %s in %s' % (name, chan)), u'verbose')
            if name in willie.memory['chan_nicks'][chan]:
                #willie.debug(__file__, log.format(u'Found %s in %s to remove' % (name, chan)), u'verbose')
                ident = willie.memory['chan_nicks'][chan][willie.memory['chan_nicks'][chan].index(name)].ident
                willie.memory['chan_nicks'][chan].remove(name)
                if ident in willie.memory['chan_ids'][chan]:
                    if name in willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks:
                        if  len(willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks) > 1:
                            willie.memory['chan_ids'][chan][willie.memory['chan_ids'][chan].index(ident)].nicks.remove(name)
                        else:
                            willie.memory['chan_ids'][chan].remove(ident)
#    except:
 #       pass

@rule(u'.*')
@event('KICK')
@unblockable
@thread(False)
@priority('high')
def kick(willie, trigger):
    name = willie.raw.strip().split()
    name = name[3]
    # Trigger comes in as trigger==kicked, trigger.nick==kicker
    #willie.debug(__file__, log.format(u'Caught KICK of %s by %s in %s' % (trigger, trigger.nick, trigger.sender)), u'verbose')
#    try:
    if not trigger.sender.lower().startswith('#'):
        return
    with willie.memory['nick_lock']:
        if trigger == willie.nick:
            willie.memory['chan_nicks'].pop(trigger.sender.lower(), None)
            willie.memory['chan_ids'].pop(trigger.sender.lower(), None)
        else:
            ident = willie.memory['chan_nicks'][trigger.sender.lower()][willie.memory['chan_nicks'][trigger.sender.lower()].index(name)].ident
            willie.memory['chan_nicks'][trigger.sender.lower()].remove(name)
            if ident in willie.memory['chan_ids'][trigger.sender.lower()]:
                if  len(willie.memory['chan_ids'][trigger.sender.lower()][willie.memory['chan_ids'][trigger.sender.lower()].index(ident)].nicks) > 1:
                        willie.memory['chan_ids'][trigger.sender.lower()][willie.memory['chan_ids'][trigger.sender.lower()].index(ident)].nicks.remove(name)
                else:
                    willie.memory['chan_ids'][trigger.sender.lower()].remove(ident)
#    except:
#        pass
@rule(u'.*')
@event('PART')
@unblockable
@thread(False)
@priority('high')
def part(willie, trigger):
    #willie.debug(__file__, log.format(u'Caught PART by %s from %s' % (trigger.nick, trigger.sender)), u'verbose')
    #try:
    name = trigger.nick  # Don't want to use a NickPlus because hostname matching
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (time.time(), name.upper(),)
    cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)
    params = (time.time(), trigger.host.upper(),)
    cur.execute('update hostmasktrack_table set timestamp=? where upper(hostmask)=?', params)
    Db.commit()
    Db.close()
    if not trigger.sender.startswith('#'):
        return
    with willie.memory['nick_lock']:
        if trigger.nick == willie.nick:
            willie.memory['chan_nicks'].pop(trigger.sender.lower(), None)  # The bot left the room.
            willie.memory['chan_ids'].pop(trigger.sender.lower(), None)
        else:
            #try:
            ident = willie.memory['chan_nicks'][trigger.sender.lower()][willie.memory['chan_nicks'][trigger.sender.lower()].index(name)].ident
            willie.memory['chan_nicks'][trigger.sender.lower()].remove(name)
            if ident in willie.memory['chan_ids'][trigger.sender.lower()]:
                if  len(willie.memory['chan_ids'][trigger.sender.lower()][willie.memory['chan_ids'][trigger.sender.lower()].index(ident)].nicks) > 1:
                        willie.memory['chan_ids'][trigger.sender.lower()][willie.memory['chan_ids'][trigger.sender.lower()].index(ident)].nicks.remove(name)
                else:
                    willie.memory['chan_ids'][trigger.sender.lower()].remove(ident)
            #except KeyError:
    #willie.debug(__file__, log.format('%s not found in nick list when they parted from %s.' % (name, trigger.sender)), 'warning')
    #except:
    #pass
def getident(nick, host, willie):
    '''Get Identity attached to hostmask/nick pair.'''
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (host.upper(),)
    cur.execute('SELECT userid FROM hostmasktrack_table WHERE upper(hostmask)=?;', params)
    hostuserid = cur.fetchone()
    cur.execute('SELECT timestamp FROM hostmasktrack_table WHERE upper(hostmask)=?;', params)
    hosttimestamp = cur.fetchone()
    params = (nick.upper(),)
    cur.execute('SELECT userid,timestamp FROM nickstrack_table WHERE upper(nick)=?;', params)
    nickuserid = cur.fetchone()
    cur.execute('SELECT timestamp FROM nickstrack_table WHERE upper(nick)=?;', params)
    nicktimestamp = cur.fetchone()
    if not nickuserid and not hostuserid:
        params = (host, nick, time.time(),)
        cur.execute('Insert Into hostmasktrack_table values (?,?,?);', params)
        params = (nick, nick, time.time(),)
        cur.execute('Insert Into nickstrack_table values (?,?,?);', params)
        ident = nick
    elif not nickuserid and hostuserid is not None:
        ident = hostuserid[0]
        params = (time.time(), host.upper(),)
        cur.execute('update hostmasktrack_table set timestamp=? where upper(hostmask)=?', params)
        params = (nick, hostuserid[0], time.time(),)
        cur.execute('Insert Into nickstrack_table values (?,?,?);', params)
    elif not hostuserid and nickuserid is not None:
        ident = nickuserid[0]
        params = (time.time(), nick.upper(),)
        cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)
        params = (host, nickuserid[0], time.time(),)
        cur.execute('Insert Into hostmasktrack_table values (?,?,?);', params)
    elif nickuserid[0] == hostuserid[0]:
        params = (time.time(), host.upper(),)
        cur.execute('update hostmasktrack_table set timestamp=? where upper(hostmask)=?', params)
        params = (time.time(), nick.upper(),)
        cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)
        ident = nickuserid[0]
    else:
        #willie.msg('#gyrotech', "nickuserid[0]" + "hostuserid[0]")
        existshost = False
        existsnick = False
        for chan in willie.memory['chan_ids']:
            if hostuserid[0] in willie.memory['chan_ids'][chan]:
                existshost = True
            if nickuserid[0] in willie.memory['chan_ids'][chan]:
                existsnick = True
        if not existshost:
            ident = hostuserid[0]
            if time.time > nicktimestamp[0] + sunset:
                params = (time.time(), nick.upper(),)
                cur.execute('update nickstrack_table set timestamp=? where upper(nick)=?', params)

        elif not existsnick:
            ident = nickuserid[0]
        else:
            ident = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
            #willie.debug(__file__, log.format(u'ERROR: Unable to determine user identity of %s in %s' % (nick, channel), u'warning')
    Db.commit()
    Db.close()
    return ident

if __name__ == "__main__":
    print __doc__.strip()