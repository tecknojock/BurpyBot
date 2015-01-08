import time
from willie.module import commands, rule, example, priority

@commands("ref")
def reference(willie, trigger):
    time.sleep(1)
    taglow = trigger.group(2).lower()
    tag = trigger.group(2)
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('SELECT tag FROM tag_table WHERE tagTarget="' + taglow + '"')
    listoftags = cur.fetchall()
    Db.close()
    if (not listoftags == []):
        willie.say("Do you not like me " + trigger.nick + "? I can do that too.")
        
        willie.say(tag + ' has the following tags: ' + ' | '.join(elem[0] for elem in listoftags))
