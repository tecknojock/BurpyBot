import os
import re
import imp
import sys
import time
import random
import psycopg2
import threading
import traceback

from willie.module import commands

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

Hostmask = hacky_import("ad_line").Hostmask

running_thread = None

class QuoteSearchThread(threading.Thread):
    def __init__(self, name, reply_func, bot):
        threading.Thread.__init__(self)
        self.name = name
        self.reply_func = reply_func
        self.bot = bot
        
    def _run(self):
        actions = []
        
        con = psycopg2.connect("dbname='quassel' user='%s' password='%s' host='localhost'" % (self.bot.config.quotes.sql_user, self.bot.config.quotes.sql_pass))
        cur = con.cursor()

        where_buffer = " OR ".join(["buffer.buffername='%s'" % x for x in ["#vore", "#vore2", "#vore3", "#vore4", "#vore5"]])
        name_fixed = "%s%%" % self.name

        q = ("SELECT backlog.type, backlog.flags, sender.sender, backlog.message FROM "
                "public.backlog, public.sender, public.buffer, public.network, public.quasseluser WHERE "
                "username='TecknoJock' AND backlog.senderid = sender.senderid AND networkname='Canternet After Dark' AND "
                "backlog.bufferid = buffer.bufferid AND (%s) AND buffer.networkid = network.networkid AND buffer.userid = quasseluser.userid AND "
                "type=4 AND sender ILIKE %%s ORDER BY backlog.messageid ASC"
            ) % where_buffer

        cur.execute(q, (name_fixed,))

        real_nick = None

        for row in cur.fetchall():
            if not real_nick:
                real_nick = Hostmask.parse(row[2]).nick

            actions.append(row[-1])

        if not actions:
            self.reply_func("It seems that %s has never performed any actions!" % self.name)
            return

        choice = None

        while not choice:
            a = random.choice(actions)
            m = re.search('"([^"]+)"', a)
            if m:
                choice = m.group(1)

        self.reply_func("\"%s\" --%s" % (choice, real_nick))

    def run(self):
        global running_thread
        try:
            self._run()
        except Exception as e:
            self.reply_func("An error has occured: %s" % str(e))
            traceback.print_exc()

        running_thread = None

@commands("icquote")
def do_icquote(bot, trigger):
    global running_thread
    arg = trigger.group(2)
    if not arg:
        bot.say("You must provide a user to find a quote for!")
        return

    if running_thread:
        bot.say("A quote search is already running!")
        return

    running_thread = QuoteSearchThread(arg, lambda msg: bot.write(("PRIVMSG", trigger.sender), msg), bot)
    running_thread.start()
