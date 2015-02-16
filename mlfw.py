"""
mlfw.py - A simple willie module to parse tags and return results from the
mlfw site
Copyright 2013, Tim Dreyer
Licensed under the Eiffel Forum License 2.

http://bitbucket.org/tdreyer/fineline
"""
import json
from urllib import quote

import willie.web as web
from willie.module import commands, example


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

def mlfw_search(willie, terms):
    base_url = u'http://mylittlefacewhen.com/api/v3/face/'
    query_strings = u'?removed=false&limit=1' + terms
    willie.debug(u"mlfw.py:mlfw_search", query_strings, u"verbose")
    result = web.get(base_url + query_strings, 10)
    try:
        json_results = json.loads(result)
    except ValueError:
        willie.debug(u"mlfw.py:mlfw_search", u"Bad json returned", u"warning")
        willie.debug(u"mlfw.py:mlfw_search", result, u"warning")
    willie.debug(u"mlfw.py:mlfw_search",
                 json.dumps(json_results, sort_keys=False, indent=2),
                 u"verbose"
                 )
    try:
        return json_results['objects'][0]['image']
    except IndexError:
        return None
    except TypeError:
        return False


@commands(u'mlfw')
@example(u"!mlfw tag one, tag two, tag three")
def mlfw(willie, trigger):
    """Searches mlfw and returns the top result with all tags specified."""
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    willie.debug(u"mlfw.py:mlfw", u"Triggered ==============", u"verbose")
    willie.debug(u"mlfw.py:mlfw", trigger.groups()[1], u"verbose")
    list = trigger.groups()[1]
    if not list:
        willie.reply(u"try something like %s" % mlfw.example)
    else:
        willie.debug(u"mlfw.py:mlfw", list, u"verbose")
        args = list.split(u',')
        for i, str in enumerate(args):
            args[i] = quote(str.strip())
        willie.debug(u"mlfw.py:mlfw", args, u"verbose")
        tags = u'&tags__all=' + u','.join(args)
        willie.debug(u"mlfw.py:mlfw", tags, u"verbose")
        mlfw_result = mlfw_search(willie, tags)
        if mlfw_result:
            willie.debug(u"mlfw.py:mlfw", mlfw_result, u"verbose")
            willie.reply(u'http://mylittlefacewhen.com%s' % mlfw_result)
        elif mlfw_result is False:  # looks bad, but must since might be None
            willie.reply(u"Uh oh, MLFW isn't working right. Try again later.")
        else:
            willie.reply(u"That doesn't seem to exist.")


if __name__ == "__main__":
    print __doc__.strip()