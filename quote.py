"""
quote.py: In-character quotes for BurpyHooves
Copyright (C) 2015 AppleDash

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import os
import re
import imp
import sys
import time
import random
import datetime
import psycopg2
import threading
import traceback

from willie.module import commands, rate

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

# This is seriously horrible but it's the best way I could think of.
def format_diff(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months, weeks = divmod(weeks, 4)
    years, months = divmod(months, 12)
    
    units = ""
    amount = 0

    if years > 0:
        units = "%d years"
        amount = years
    elif months > 0:
        units = "%d months"
        amount = months
    elif weeks > 0:
        units = "%d weeks"
        amount = weeks
    elif days > 0:
        units = "%d days"
        amount = days
    elif hours > 0:
        units = "%d hours"
        amount = hours
    elif minutes > 0:
        units = "%d minutes"
        amount = minutes
    else:
        units = "%d seconds"
        amount = seconds

    if amount == 1:
        units = units[:-1]

    return units % amount

Hostmask = hacky_import("ad_line").Hostmask

running_threads = []
lock = threading.Lock()
max_threads = 5

class QuoteSearchThread(threading.Thread):
    def __init__(self, name, reply_func, bot, sender):
        threading.Thread.__init__(self)
        self.name = name
        self.reply_func = reply_func
        self.bot = bot
        self.start_time = time.time()
        self.sender = sender
        
    def _run(self):
        actions = []
        
        con = psycopg2.connect("dbname='quassel' user='%s' password='%s' host='localhost' port=5433" % (self.bot.config.quotes.sql_user, self.bot.config.quotes.sql_pass))
        cur = con.cursor()

        if self.sender.lower()[0:5] == "#vore":
            where_buffer = " OR ".join(["buffer.buffername='%s'" % x for x in ["#vore", "#vore2", "#vore3", "#vore4", "#vore5"]])
        elif (self.sender.lower() == u"#appledash") | (self.sender.lower() == u"#gyrotech"):
            where_buffer = " OR ".join(["buffer.buffername='%s'" % x for x in self.bot.channels])
        else:
            self.bot.say(self.sender)
            where_buffer = "buffer.buffername='%s'" % self.sender
        name_fixed = "%s!%%" % self.name

        q = ("SELECT backlog.type, backlog.flags, sender.sender, EXTRACT(EPOCH FROM backlog.time), backlog.message FROM "
                "public.backlog, public.sender, public.buffer, public.network, public.quasseluser WHERE "
                "username='TecknoJock' AND backlog.senderid = sender.senderid AND networkname='Canternet After Dark' AND "
                "backlog.bufferid = buffer.bufferid AND (%s) AND buffer.networkid = network.networkid AND buffer.userid = quasseluser.userid AND "
                "type=4 AND (sender ILIKE %%s OR sender ILIKE %%s) ORDER BY backlog.messageid ASC"
            ) % where_buffer

        cur.execute(q, (name_fixed, self.name))

        real_nick = None

        for row in cur.fetchall():
            if not real_nick:
                hm_nick = Hostmask.parse(row[2]).nick
                real_nick = hm_nick if hm_nick else row[2]

            actions.append((row[-1], row[3]))

        if not actions:
            self.reply_func("It seems that %s has never performed any actions!" % self.name)
            return

        choice = None

        while not choice:
            a = random.choice(actions)
            m = re.search('"([^"]+)"', a[0])
            if m:
                choice = (m.group(1), a[1])

        diff = (datetime.datetime.now() - datetime.datetime.fromtimestamp(choice[1])).total_seconds()
        self.reply_func("\"%s\" --%s, %s ago." % (choice[0], real_nick, format_diff(diff)))

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.reply_func("An error has occured: %s" % str(e))
            traceback.print_exc()

        with lock:
            running_threads.remove(self)

@commands("icquote")
@rate(1)
def do_icquote(bot, trigger):
    arg = trigger.group(2)
    if not arg or not len(arg.strip()):
        bot.say("You must provide a user to find a quote for!")
        return

    arg = arg.strip()

    if len(running_threads) >= max_threads:
        for t in running_threads: # Get rid of timed-out threads.
            if (time.time() - t.start_time) > 60:
                running_threads.remove(t)
    
    if len(running_threads) >= max_threads: # Still?
        bot.say("%d quote searches are already running!" % max_threads)
        return

    t = QuoteSearchThread(arg, lambda msg: bot.write(("PRIVMSG", trigger.sender), msg), bot, trigger.sender)
    t.start()

    with lock:
        running_threads.append(t)
