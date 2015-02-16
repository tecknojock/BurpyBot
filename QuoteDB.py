"""
QuoteDB.py - A willie module to tag words
Copyright 2013, TecknoJock
Licensed under the Eiffel Forum License 2.

"""

from willie.tools import Nick
from willie.module import commands, example, priority, rule
import re
import random


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


def setup(willie):
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists quote_table (quoteID INTEGER, quote, Primary Key (quoteID))')
    listoftags = cur.fetchall()
    Db.close()

@commands('addquote')
@example(u'!addquote <example> Im going to mount it')
def quoteadd(willie, trigger):
        '''Adds a new quote. !tagadd <example> I'm going to mount it.'''
        if not perm_chk(trigger.hostmask, "Bc", willie):
            return
        if not trigger.group(2):
            willie.say("See !help !addquote for help")
            return
        quote = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', trigger.group(2))
#    try:
        Db = willie.db.connect()
        cur = Db.cursor()
        params = (quote,)
        cur.execute('Insert Into quote_table VALUES (null, ?)', params)
        Db.commit()
        willie.reply('Quote has been added.')
#    except:
        pass
#    finally:
        Db.close()
    
    
@commands('quoteremove')
@example(u'!quoteremove -1')
def quoteremove(willie, trigger):
    '''Removes a quote by quoteID. !quoteremove -1'''
    if not perm_chk(trigger.hostmask, "Ad", willie):
        return
    if not trigger.group(2):
        willie.say("See !help !quoteremove for help")
        return
    try:
        quoteref = int(trigger.group(2))
    except:
        willie.say("Quote to remove must be an int.")
    try:
        Db = willie.db.connect()
        cur = Db.cursor()
        if quoteref > 0:
            cur.execute('Delete from quote_table where quoteID=?', (quoteref,))
        else:
            cur.execute('Delete from quote_table where quoteID=((select max(quoteID) from quote_table)+?)', (quoteref,)) 
        Db.commit()
    except:
        willie.reply("Could not remove quote. It either does not exist or something went wrong.")
    finally:
        Db.close()


@commands('quote')
def getquote(willie, trigger):
    try:
        db = willie.db.connect()
        cur = db.cursor()
        if trigger.group(2):
            try:
                quoteref = trigger.group(2)
                try:
                    quoteref = int(quoteref)
                    try:
                        if quoteref > 0:
                            cur.execute('Select quote from quote_table where quoteID=?', (quoteref,))
                        else:
                            cur.execute('Select quote from quote_table where quoteID=((select max(quoteID) from quote_table)+?)', (quoteref,)) 
                        willie.say(cur.fetchone()[0])
                        return
                    except:
                        quoteref = str(quoteref)
                        raise
                except:
                    quoteref = "%%%s%%" % quoteref
                    cur.execute("Select quote FROM quote_table where quote LIKE ?", (quoteref,))
                    listofquotes = [x[0] for x in cur.fetchall()]
                    willie.say(random.choice(listofquotes))
                    return
            except:
                willie.say("Could not find quote.")
        else:
            cur.execute("Select quoteID from quote_table where quoteID=(select max(quoteID) from quote_table)")
            numberofquotes = cur.fetchone()
            quoteref = random.randint(1,numberofquotes[0])
            cur.execute('Select quote from quote_table where quoteID=?', (quoteref,))
            willie.say(cur.fetchone()[0])
    finally:
        db.close()

if __name__ == "__main__":
    print __doc__.strip()