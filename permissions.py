from willie.tools import Nick
from willie.module import commands, example, priority, rule
import re
def setup(willie):
    Db = willie.db.connect()
    cur = Db.cursor()
    
    cur.execute('create table if not exists permissions_table (permissions , hostmask, Primary Key (hostmask))')
    Db.close()
#Ow = Owner 
#Ad = Admin
#Ia = Ignore AI
#Bc = Block Commands
#Op = Channel Op
#Gb = Not actually going to bed
#Iu = Ignore URL

blockpermissions = "Ia|Bc|Iu"
permissionlist = "Ow|Ad|Ia|Bc|Op|Gb|Iu"
oppermissions = "Bc|Ia|Iu"
adpermissions = "Op|Gb"

@commands("Listpermissions")
def listperm(willie, trigger):
    '''Lists all availible permissions'''
    willie.msg(trigger.nick, "Current permissions are Ow: owner, Ad: bot admin, Op: channel op, Bc: Block commands, Ia: ignore AI, Iu: Dont follow URLs Gb: Repeatedly doesn't go to bed when they say. Currently no permission implies other permissions.")
    willie.msg(trigger.nick, "Ops may add or remove the permissions Bc, Ia, Iu, whilst admins can also add or remove the permissions Op, Gb")
    willie.msg(trigger.nick, "To add or remove permissions use !addpermission or !removepermission respectivly. The format is !command hostmask permission")
    willie.msg(trigger.nick, "To check a users current permission level, use !checkpermissions hostmask")

def perm_chk(hostmask, level,willie):
    hostmask = hostmask.split('@', 1)[-1]
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (hostmask,)
    cur.execute('SELECT permissions FROM permissions_table WHERE Upper(hostmask)=upper(?)', params)
    try:
        permission = cur.fetchone()[0]
    except:
        permission = ""
    Db.close()
    if re.search(level,permission):
        if re.search(level,blockpermissions):
            return False
        return True
    else:
        if re.search(level,blockpermissions):
            return True
        return False

@commands("AddPermission")
def addper(willie, trigger):
    '''For adding new permsions. Use syntax hostmask Permission'''
    if not trigger.group(2):
        willie.say("Please use the following format: !addpermission hostmask permNoission.")
        return
    if not (len(trigger.group(2).split(None, 2)) == 2):
        willie.say("Please use the following format: !addpermission hostmask permission.")
        return
    if not perm_chk(trigger.hostmask, "Ow", willie):
        if not perm_chk(trigger.hostmask, "Ad", willie) and re.search(newpermission, adpermissions):
            if not perm_chk(trigger.hostmask, "Op", willie) and re.search(newpermission, oppermissions):
                willie.say("You don't have permission.")
                return
    hostmask, newpermission = trigger.group(2).split(None, 1)
    newpermission = newpermission.strip()
    if re.search(newpermission,permissionlist):
        Db = willie.db.connect()
        cur = Db.cursor()
        params = (hostmask,)
        cur.execute('SELECT permissions FROM permissions_table WHERE Upper(hostmask)=upper(?)', params)
        try:
            permissions = cur.fetchone()[0]
            if re.search(newpermission, permissions):
                willie.say("User already has permission.")
                return
        except:
            permissions = ""
        params = (hostmask,)
        cur.execute('Delete from permissions_table where Upper(hostmask)=upper(?)', params)
        newpermissions = "".join((permissions, newpermission, "|"))
        params = (newpermissions, hostmask)
        cur.execute('Insert Into permissions_table VALUES (?, ?)', params)
        Db.commit()
        Db.close()
        willie.say("Permission Added")
    else:
        willie.say("Not a valid permission.")
        return

@commands("RemovePermission")
def remper(willie, trigger):
    '''For removing permsions. Use syntax hostmask Permission'''
    if not trigger.group(2):
        willie.say("Please use the following format: !removepermission hostmask permission.")
        return
    if not (len(trigger.group(2).split(None, 2)) == 2):
        willie.say("Please use the following format: !removepermission hostmask permission.")
        return
    hostmask, newpermission = trigger.group(2).split(None, 1)
    if not perm_chk(trigger.hostmask, "Ow", willie):
        if not perm_chk(trigger.hostmask, "Ad", willie) and re.search(newpermission, adpermissions):
            if not perm_chk(trigger.hostmask, "Op", willie) and re.search(newpermission, oppermissions):
                willie.say("You don't have permission.")
                return
    if re.search(newpermission,permissionlist):
        Db = willie.db.connect()
        cur = Db.cursor()
        params = (hostmask,)
        cur.execute('SELECT permissions FROM permissions_table WHERE Upper(hostmask)=upper(?)', params)
        try:
            permissions = cur.fetchone()[0]
            if not re.search(newpermission, permissions):
                return
                willie.say("User does not have that permission.")
        except:
            willie.say("User does not have that permission.")
            return
        params = (hostmask,)
        cur.execute('Delete from permissions_table where Upper(hostmask)=upper(?)', params)
        newpermission = "".join(("\||".join(newpermission.split("|")), "\|"))
        newpermissions = re.sub(newpermission, "", permissions)
        if newpermissions != "":
            params = (newpermissions, hostmask)
            cur.execute('Insert Into permissions_table VALUES (?, ?)', params)
        Db.commit()
        Db.close()
        willie.say("Permission has been removed.")
    else:
        willie.say("Not a valid permission.")
        return


@commands("CheckPermissions")
def checkPerm(willie, trigger):
    '''For checking user permissions. !checkpermissions hostmask'''
    try:
        if not (len(trigger.group(2).split(None, 2)) == 1):
            return
        
        hostmask = trigger.group(2)
    except:
        hostmask = trigger.hostmask.split('@', 1)[-1]
    Db = willie.db.connect()
    cur = Db.cursor()
    params = (hostmask,)
    cur.execute('SELECT permissions FROM permissions_table WHERE Upper(hostmask)=upper(?)', params)
    try:
        permissions = cur.fetchone()[0]
        willie.say(permissions)
    except:
        willie.say("Hostmask not found")
    finally:
        Db.close()
