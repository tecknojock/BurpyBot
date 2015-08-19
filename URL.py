"""
url.py - willie URL title module
Copyright 2013 Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""

import re
from htmlentitydefs import name2codepoint
from willie import web, tools
from willie.module import commands, rule, example
import urlparse
from socket import timeout

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


url_finder = None
exclusion_char = '!'
# TODO move these to the database
_EXCLUDE = ['[ imgur: the simple image sharer ] - imgur.com',
            '[ imgur: the simple image sharer ]',
            '[ imgur: the simple overloaded page] - imgur.com',
            '[ imgur: the simple overloaded page]']
# These are used to clean up the title tag before actually parsing it. Not the
# world's best way to do this, but it'll do for now.
title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
# This is another regex that presumably does something important.
re_dcc = re.compile(r'(?i)dcc\ssend')
# This sets the maximum number of bytes that should be read in order to find
# the title. We don't want it too high, or a link to a big file/stream will
# just keep downloading until there's no more memory. 640k ought to be enough
# for anybody.
max_bytes = 655360


def configure(config):
    """

    | [url] | example | purpose |
    | ---- | ------- | ------- |
    | exclude | https?://git\.io/.* | A list of regular expressions for URLs for which the title should not be shown. |
    | exclusion_char | ! | A character (or string) which, when immediately preceding a URL, will stop the URL's title from being shown. |
    """
    if config.option('Exclude certain URLs from automatic title display', False):
        if not config.has_section('url'):
            config.add_section('url')
        config.add_list('url', 'exclude', 'Enter regular expressions for each URL you would like to exclude.',
            'Regex:')
        config.interactive_add('url', 'exclusion_char',
            'Prefix to suppress URL titling', '!')


def setup(bot=None):
    global url_finder, exclusion_char

    if not bot:
        return

    if bot.config.has_option('url', 'exclude'):
        regexes = [re.compile(s) for s in
                   bot.config.url.get_list('exclude')]
    else:
        regexes = []

    # We're keeping these in their own list, rather than putting then in the
    # callbacks list because 1, it's easier to deal with modules that are still
    # using this list, and not the newer callbacks list and 2, having a lambda
    # just to pass is kinda ugly.
    if not bot.memory.contains('url_exclude'):
        bot.memory['url_exclude'] = regexes
    else:
        exclude = bot.memory['url_exclude']
        if regexes:
            exclude.extend(regexes)
        bot.memory['url_exclude'] = exclude

    # Ensure that url_callbacks and last_seen_url are in memory
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.WillieMemory()
    if not bot.memory.contains('last_seen_url'):
        bot.memory['last_seen_url'] = tools.WillieMemory()

    if bot.config.has_option('url', 'exclusion_char'):
        exclusion_char = bot.config.url.exclusion_char

    url_finder = re.compile(r'(?u)(%s?(?:http|https|ftp)(?:://\S+))' %
        (exclusion_char))


@commands('title')
@example('!title http://google.com', '[ Google ] - google.com')
def title_command(bot, trigger):
    """
    Show the title or URL information for the given URL, or the last URL seen
    in this channel.
    """

    if not perm_chk(trigger.hostmask, "Bc", bot):
        return
    if not trigger.group(2):
        if trigger.sender not in bot.memory['last_seen_url']:
            return
        matched = check_callbacks(bot, trigger,
                                  bot.memory['last_seen_url'][trigger.sender],
                                  True)
        if matched:
            return
        else:
            urls = [bot.memory['last_seen_url'][trigger.sender]]
    else:
        urls = re.findall(url_finder, trigger)

    results = process_urls(bot, trigger, urls)
    for title, domain in results[:4]:
        bot.reply('[ %s ] - %s' % (title, domain))

@rule('.*>>[0-9]{1,7}( |$).*')
def derpylinks(bot, trigger):
    ignoredchannels = []

    if re.match(bot.config.core.prefix + 'title', trigger) or \
            not perm_chk(trigger.hostmask, "Iu", bot) or \
            trigger.sender in ignoredchannels:
        return
    trigger.raw = "Passed " + re.sub("(>>)([0-9]{1,7}( |$))","https://derpiboo.ru/\\2",trigger)
    bot.say(", ".join(re.findall(url_finder, trigger.raw)))
    title_auto(bot, trigger)


@rule('.*https://ronxgr5zb4dkwdpt.onion/.*')
def onionlink(bot, trigger):
    ignoredchannels = []

    if re.match(bot.config.core.prefix + 'title', trigger) or \
            not perm_chk(trigger.hostmask, "Iu", bot) or \
            trigger.sender in ignoredchannels:
        return
    trigger.raw = "Passed " + re.sub("(https://ronxgr5zb4dkwdpt.onion/)([0-9]{1,7}( |$))","https://derpiboo.ru/\\2",trigger)
    bot.say(", ".join(re.findall(url_finder, trigger.raw)))
    title_auto(bot, trigger)

@rule('(?u).*(https?://\S+).*')
def title_auto(bot, trigger):
    """
    Automatically show titles for URLs. For shortened URLs/redirects, find
    where the URL redirects to and show the title for that (or call a function
    from another module to give more information).
    """

    ignoredchannels = ['#SRQsRoom','#techponiesafterdark']

    try:
        trigger.raw
    except:
        trigger.raw = trigger

    if re.match(bot.config.core.prefix + 'title', trigger) or \
            not perm_chk(trigger.hostmask, "Iu", bot) or \
            trigger.sender in ignoredchannels:
        return

    # Avoid fetching known malicious links
    if 'safety_cache' in bot.memory and trigger.raw in bot.memory['safety_cache']:
        if bot.memory['safety_cache'][trigger]['positives'] > 1:
            return

    urls = re.findall(url_finder, trigger.raw)
    if urls:
        try:
            results = process_urls(bot, trigger.raw, urls)
        except timeout:
            return  # The url timed out, so lets be quiet.
        bot.memory['last_seen_url'][trigger.sender] = urls[-1]

    for title, domain in results[:4]:
        if domain in trigger.bytes:
            message = '[ %s ]' % title
        else:
            message = '[ %s ] - %s' % (title, domain)
        # Filter for dumb titles
        if message in _EXCLUDE:
            return
        # Guard against responding to other instances of this bot.
        if message != trigger:
            message = re.sub(" - TecknoJock's library", "", message, 0, re.I)
            bot.say(message)


def process_urls(bot, trigger, urls):
    """
    For each URL in the list, ensure that it isn't handled by another module.
    If not, find where it redirects to, if anywhere. If that redirected URL
    should be handled by another module, dispatch the callback for it.
    Return a list of (title, hostname) tuples for each URL which is not handled by
    another module.
    """

    results = []
    for url in urls:
        url = url.strip('()[]{}<>').rstrip('.!?,\001')
        if not url.startswith(exclusion_char):
            # Magic stuff to account for international domain names
            try:
                url = bot.web.iri_to_uri(url)
            except:
                pass
            # First, check that the URL we got doesn't match
            matched = check_callbacks(bot, trigger, url, False)
            if matched:
                continue
            # Then see if it redirects anywhere
            new_url = follow_redirects(url)
            if not new_url:
                continue
            # Then see if the final URL matches anything
            matched = check_callbacks(bot, trigger, new_url, new_url != url)
            if matched:
                continue
            # Finally, actually show the URL
            title = find_title(url)
            if title:
                results.append((title, get_hostname(url)))
    return results


def follow_redirects(url):
    """
    Follow HTTP 3xx redirects, and return the actual URL. Return None if
    there's a problem.
    """
    try:
        connection = web.get_urllib_object(url, 60)
        url = connection.geturl() or url
        connection.close()
    except:
        return None
    return url


def check_callbacks(bot, trigger, url, run=True):
    """
    Check the given URL against the callbacks list. If it matches, and ``run``
    is given as ``True``, run the callback function, otherwise pass. Returns
    ``True`` if the url matched anything in the callbacks list.
    """
    # Check if it matches the exclusion list first
    matched = any(regex.search(url) for regex in bot.memory['url_exclude'])
    # Then, check if there's anything in the callback list
    for regex, function in tools.iteritems(bot.memory['url_callbacks']):
        match = regex.search(url)
        if match:
            if run:
                function(bot, trigger, match)
            matched = True
    return matched


def find_title(url):
    """Return the title for the given URL."""
    try:
        content, headers = web.get(url, return_headers=True, limit_bytes=max_bytes)
    except UnicodeDecodeError:
        return # Fail silently when data can't be decoded

    # Some cleanup that I don't really grok, but was in the original, so
    # we'll keep it (with the compiled regexes made global) for now.
    content = title_tag_data.sub(r'<\1title>', content)
    content = quoted_title.sub('', content)

    start = content.find('<title>')
    end = content.find('</title>')
    if start == -1 or end == -1:
        return
    title = web.decode(content[start + 7:end])
    title = title.strip()[:200]

    # title = ' '.join(title.split())  # cleanly remove multiple spaces

    # If the title has too many words, trim it.
    title_l = title.split()
    if len(title_l) > 10:
        title_l = title_l[:10]
        title_l.append(u'...')
    title = ' '.join(title_l)

    # More cryptic regex substitutions. This one looks to be myano's invention.
    title = re_dcc.sub('', title)

    return title or None


def get_hostname(url):
    idx = 7
    if url.startswith('https://'):
        idx = 8
    elif url.startswith('ftp://'):
        idx = 6
    hostname = url[idx:]
    slash = hostname.find('/')
    if slash != -1:
        hostname = hostname[:slash]
    return hostname

if __name__ == "__main__":
    from willie.test_tools import run_example_tests
    run_example_tests(__file__)

