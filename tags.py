"""
tags.py - A willie module to tag words
Copyright 2013, TecknoJock
Licensed under the Eiffel Forum License 2.

"""

from willie.tools import Nick
from willie.module import commands, example, priority, rule
import re

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


def setup(willie):
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists tag_table (tagTarget , tag, Primary Key (tagTarget, tag))')
    listoftags = cur.fetchall()
    Db.close()

@commands('tagadd|addtag')
@example(u'!tagadd thisTag http://example.com')
def tagadd(willie, trigger):
    '''Adds a new tag. !tagadd nick, Tag1|tag2|...|tagN'''
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if not trigger.group(2):
        willie.say("See !tags for help")
        return
    if (len(trigger.group(2).split(None, 2)) == 1):
        willie.reply("Insufficient arguments, see: !tagadd example, tag1|tag2|...|tagN")
        return
    #    content = trigger.group(2).split("|")
    #    tagTargeted = trigger.nick.lower()
    #else:
    #    tagTargeted, content = trigger.group(2).split(None, 1)
    #    tagTargeted = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagTargeted)
    #    tagTargeted = tagTargeted.lower()
    #    content = content.split("|")
    #    tagTargeted, content = trigger.group(2).split(None, 1)
    tagTargeted, content = trigger.group(2).split(None, 1)
    tagTargeted = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagTargeted)
    tagTargeted = tagTargeted.lower().strip()
    content = content.split("|")
    if "," == tagTargeted[-1]:
        tagTargeted = tagTargeted[0:-1]
    else:
        willie.reply("Tag target must be seperated with a comma ie: !tagadd example, tag1|tag2|...|tagN")
        return
    if tagTargeted == "stats" and not perm_chk(trigger.hostmask, "Ad", willie):
        willie.reply(unicode.format(u"You do not have permissions to access the tag {0}", tagTargeted))
        return
    try:
        Db = willie.db.connect()
        cur = Db.cursor()
        params = (tagTargeted.strip(),)
        cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
        listoftags = cur.fetchall()
        if (not listoftags == []):
            if re.search(u"\u0001","".join(elem[0] for elem in listoftags)):
                tagTargeted = re.sub(u"\u0001", "", "".join(elem[0] for elem in listoftags))
        for tagcontent in content:
            try:
                tagcontent = tagcontent.strip()
                tagcontent = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagcontent)
                if tagcontent != "":
                    params = (tagTargeted, tagcontent.upper())
                    cur.execute('Delete from tag_table where tagTarget=? and upper(tag)=?', params)
                    params = (tagTargeted, tagcontent)
                    cur.execute('Insert Into tag_table VALUES (?, ?)', params)
                    Db.commit()
            except:
                if len(content) == 1:
                    raise
        willie.reply('I have added the tag(s) for you.')
    except:
        willie.reply(tagTargeted + " is already tagged with " + tagcontent +".")
    finally:
        Db.close()
    
    
@commands('tagremove|removetag')
@example(u'!tagremove thisTag, http://example.com')
def tagremove(willie, trigger):
    '''Removes a tag. !tagremove nick, tag1|tag2|...|tagN'''
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if not trigger.group(2):
        willie.say("See !tags for help")
        return
    if (len(trigger.group(2).split(None, 2)) == 1): 
        willie.reply("Insufficient arguments, see: !tagadd example, tag1|tag2|...|tagN")
        return
    #    content = trigger.group(2).split("|")
    #    tagTargeted = trigger.nick.lower()
    #else:
    tagTargeted, content = trigger.group(2).split(None, 1)
    tagTargeted = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagTargeted)
    tagTargeted = tagTargeted.lower().strip()
    if "," == tagTargeted[-1]:
        tagTargeted = tagTargeted[0:-1]
    else:
        willie.reply("Tag target must be seperated with a comma ie: !tagremove example, tag1|tag2|...|tagN")
        return
    content = content.split("|")
    if tagTargeted == "stats" and not perm_chk(trigger.hostmask, "Ad", willie):
        willie.reply(unicode.format(u"You do not have permissions to access the tag {0}", tagTargeted))
        return
    try:
        Db = willie.db.connect()
        cur = Db.cursor()
        params = (tagTargeted.strip(),)
        cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
        listoftags = cur.fetchall()
        if (not listoftags == []):
            if re.search(u"\u0001","".join(elem[0] for elem in listoftags)):
                tagTargeted = re.sub(u"\u0001", "", "".join(elem[0] for elem in listoftags))
        for tagcontent in content:
            try:
                tagcontent = tagcontent.strip()
                tagcontent = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagcontent)
                if tagcontent != "":
                    params = (tagTargeted, tagcontent.upper())
                    cur.execute('Delete from tag_table where tagTarget=? and UPPER(tag) =? ', params)
                    Db.commit()
            except:
                if len(content) == 1:
                    raise
        
        params = (tagTargeted.strip(),)
        cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
        listoftags = cur.fetchall()
        if (listoftags == []):
            params = (u"\u0001" + tagTargeted,)
            cur.execute('Delete from tag_table where UPPER(tag) =UPPER(?)', params)
            Db.commit()
        willie.reply('I have removed the tag(s) for you.')
    except:
        willie.reply(tagTargeted + " is already tagged with " + tagcontent +".")
    finally:
        Db.close()

@commands("tagclear|cleartag")
@example(u"!tagclear Derpy")
def tagclear(willie, trigger):
    '''Clears all tags (Can only be used on self if not an admins.)'''
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    if (not hasattr(trigger.group(2), "lower")):
        willie.reply("Your command is missing arguments. See '!help tagclear' for more information.")
        return
    elif (len(trigger.group(2).split(None, 2)) > 1):
        willie.reply("Your command has too many arguments. See '!help tagclear' for more information.")
        return
    else:
        tagTargeted = trigger.group(2)
        tagTargeted = tagTargeted.lower()        
        tagTargeted = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', tagTargeted)
        try:
            if ((tagTargeted == trigger.nick) or perm_chk(trigger.hostmask, "Ad", willie)):
                Db = willie.db.connect()
                cur = Db.cursor()
                params = (tagTargeted,)
                cur.execute('Delete from tag_table where tagTarget=?', params)
                Db.commit()
                params = (u"\u0001" + tagTargeted,)
                cur.execute('Delete from tag_table where UPPER(tag) =UPPER(?)', params)
                Db.commit()
                Db.close()
                willie.reply('I have cleared that tag for you.')
            else:
                willie.reply("You must be an admin to clear tags that are not attached to your nick.")
        except:
            willie.reply(tagTargeted + " currently has no tags.")

@commands('tags?')
def tag(willie, trigger):
    if not perm_chk(trigger.hostmask, "Bc", willie):
        return
    '''Describes how to use !tag'''
    willie.reply("To view tags use ?tag where tag is the tag you want to view.")
    willie.reply("To add a tag use !tagadd and to remove a tag use !tagremove with the format !tagadd nick, tag1|tag2|...|tagN")
    willie.reply("Multiple tags can be added or removed by separating them with |. Please add tags in PMs")

@commands('linktag|taglink')
def linktag(willie,trigger):
    '''Links two tags together. !linktag nick1 nick2'''
    if (not trigger.group(2)) or len(trigger.group(2).split()) != 2:
        willie.say("Command requires 2 arguments.")
        return
    linkedtags = trigger.group(2).split()
    linkedtags[0] = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', linkedtags[0]).lower()
    linkedtags[1] = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', linkedtags[1]).lower()
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (linkedtags[0],)
    cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
    listoftags = cur.fetchall()
    if listoftags == []:
        tag1empty = 1
    elif re.search(u"\u0001", "".join(elem[0] for elem in listoftags[0])):
        tag1empty = 2
        parenttag = re.sub(u"\u0001", "", "".join(elem[0] for elem in listoftags[0]))
    else:
        tag1empty = 0
    params = (linkedtags[1],)
    cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
    listoftags = cur.fetchall()
    if listoftags == []:
        tag2empty = 1
    elif re.search(u"\u0001", "".join(elem[0] for elem in listoftags[0])):
        tag2empty = 2
        parenttag = re.sub(u"\u0001", "", "".join(elem[0] for elem in listoftags[0]))
    else:
        tag2empty = 0
    if tag1empty == tag2empty:
        if tag1empty == 0:
            willie.say("Both tags are empty")
        else:
            willie.say("Both tags contain tags")
    elif tag1empty == 2 or tag2empty == 2:
        willie.say(unicode.format(u"You cannont link to a link. Try Linking to {0} instead.", parenttag))
    else:
        if tag1empty == 1:
            params = (linkedtags[0], u"\u0001" + linkedtags[1])
            cur.execute('Insert Into tag_table VALUES (?, ?)', params)
            Db.commit()
            willie.say("The tags have been linked")
        else:
            params = (linkedtags[1], u"\u0001" + linkedtags[0])
            cur.execute('Insert Into tag_table VALUES (?, ?)', params)
            Db.commit()
            willie.say("The tags have been linked.")
    Db.close()
@commands('alltags')
def alltags(willie, trigger):
    '''Lists all tags in database.'''
    Db = willie.db.connect()
    cur = Db.cursor()
    cur.execute('SELECT DISTINCT tagTarget FROM tag_table')
    listoftags = cur.fetchall()
    Db.close()
    if not trigger.sender[1:] == "gorgerbot":
        if (not listoftags == []):
            willie.msg(trigger.nick, "All the tags are: " + u' \u0002|\u000F '.join(elem[0] for elem in listoftags), 5)
        else:
            Willi.msg(trigger.nick, "No tags have been added.")
    else:
        if (not listoftags == []):
            willie.say("All the tags are: " + u' \u0002|\u000F '.join(elem[0] for elem in listoftags), 5)
        else:
            Willi.say("No tags have been added.")

@priority('low')
@commands('alltagged')
def alltags(willie, trigger):
    '''Lists all tags in database.'''
    Db = willie.db.connect()
    cur = Db.cursor()
    cur.execute('SELECT DISTINCT tag Target FROM tag_table')
    listoftags = cur.fetchall()
    Db.close()
    if not trigger.sender[1:] == "gorgerbot":
        if (not listoftags == []):
            willie.msg(trigger.nick, "All the tags are: " + u' \u0002|\u000F '.join(elem[0] for elem in listoftags), 5)
        else:
            Willi.msg(trigger.nick, "No tags have been added.")
    else:
        if (not listoftags == []):
            willie.say("All the tags are: " + u' \u0002|\u000F '.join(elem[0] for elem in listoftags), 5)
        else:
            Willi.say("No tags have been added.")      
@rule(u'\\?\S+?\s*\Z')
def checktag(willie, trigger):
    tag = trigger[1:]
    taglow = tag.lower()
    Db = willie.db.connect()
    cur = Db.cursor()
    taglow = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', taglow)

    params = (taglow.strip(),)

    cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
    listoftags = cur.fetchall()
    if listoftags:
        if re.search(u"\u0001","".join(elem[0] for elem in listoftags)):
            parenttag = re.sub(u"\u0001", "", "".join(elem[0] for elem in listoftags))
            params = (parenttag,)
            cur.execute('SELECT tag FROM tag_table WHERE tagTarget=?', params)
            listoftags = cur.fetchall()
            tag = parenttag
        willie.say(u"\u0002" + tag.strip() + u'\u000F has the following tags\u0002:\u000F ' + u' \u0002|\u000F '.join(elem[0] for elem in listoftags))
    Db.close()

@priority('low')
@commands('searchtag|tagsearch')        
def searchtag(willie, trigger):
    Db = willie.db.connect()
    cur = Db.cursor()
    try:
        taglow = trigger.group(2).lower()
        taglow = re.sub('([\00-\x02]|[\x04-\x1f])|(\x03[1-9][0-6]?(,[1-9][0-6]?)?)', '', taglow)

        params = (taglow.strip(),)

        cur.execute('SELECT tagTarget FROM tag_table WHERE lower(tag)=?', params)
        listoftags = cur.fetchall()
        if listoftags:
            willie.say(u"\u0002" + trigger.group(2) + u'\u000F is tagged on \u0002:\u000F ' + u' \u0002|\u000F '.join(elem[0] for elem in listoftags))
        else:
            willie.reply("No nothing is tagged with %s" % (trigger.group(2)))
    except:
        willie.reply("Needs a tag to search for. !searchtag example")

    Db.close()


if __name__ == "__main__":
    print __doc__.strip()