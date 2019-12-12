# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 22:56:16 2019

@author: stijn
"""

import asyncio
import discord
from discord.errors import InvalidArgument
import aiohttp
import datetime

class ErrorCode(Exception):
    def __init__(self, code):
        self.code = code


import utility







async def Log_command(message, client, db_conn, theCursor):
    if message.channel.permissions_for(message.author).view_audit_log != True:
        return
    result = theCursor.execute("SELECT EditChanl, ModChanl FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
    result = result.fetchall()
    # You receive a list of lists that hold the result
    for row in result:
        EditChanl =  row[0]
        ModChanl =  row[1]
        
    if message.channel.id == EditChanl:
        sended_message = await message.channel.send("Do you want to remove this channel as edits-log channel or also spam mod logs here?\n\U0001F1E6 => To remove it \n\U0001F1E7 => To also spam mod logs in here\n\u274C => to cancel the command")
        try:
            reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\U0001F1E6", u"\U0001F1E7","\u274C"]) #{u"\u274C": "red cross",  u"\u2705": "Green V"}
        except asyncio.TimeoutError: 
            await message.channel.send("Timedout - please try the command again if you were too late!")
            await sended_message.delete()
            return
        if str(reaction.emoji) == u"\u274C":
            await sended_message.delete()
            return
        elif str(reaction.emoji) == u"\U0001F1E6":
            print("delting channel")
            db_conn.execute("UPDATE GuildSettings SET EditChanl = NULL WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await sended_message.clear_reactions()
            await sended_message.edit(content= "Succesfull removed this channel from logging edits")
        elif str(reaction.emoji) == u"\U0001F1E7":
            db_conn.execute("UPDATE GuildSettings SET ModChanl = {0.channel.id}, LastModAction = NULL WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await sended_message.clear_reactions()
            await sended_message.edit(content= "Succesfull added this channel to log also administrator stuff")
    elif message.channel.id == ModChanl:
        sended_message = await message.channel.send("Do you want to remove this channel as mods-log channel or also spam edit logs here?\n\U0001F1E6 => To remove it \n\U0001F1E7 => To also spam edit logs in here\n\u274C => to cancel the command")
        try:
            reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\U0001F1E6", u"\U0001F1E7","\u274C"]) #{u"\u274C": "red cross",  u"\u2705": "Green V"}
        except asyncio.TimeoutError: 
            await message.channel.send("Timedout - please try the command again if you were too late!")
            await sended_message.delete()
            return
        if str(reaction.emoji) == u"\u274C":
            await sended_message.delete()
            return
        elif str(reaction.emoji) == u"\U0001F1E6":
            print("delting channel")
            db_conn.execute("UPDATE GuildSettings SET ModChanl = NULL, LastModAction = NULL WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await sended_message.clear_reactions()
            await sended_message.edit(content= "Succesfull deleted this channel to log administrator stuff")
        elif str(reaction.emoji) == u"\U0001F1E7":
            db_conn.execute("UPDATE GuildSettings SET EditChanl = {0.channel.id} WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await sended_message.clear_reactions()
            await sended_message.edit(content= "Succesfull added this channel to log also edits stuff")

    else:
        sended_message = await message.channel.send("Do you want to set this channel as log-spam?")
        try:
            reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\u2705", u"\u274C"]) #{u"\u274C": "red cross",  u"\u2705": "Green V"}
        except asyncio.TimeoutError: 
            await message.channel.send("Timedout - please try the command again if you were too late!")
            await sended_message.delete()
            return
        if str(reaction.emoji) == u"\u274C":
            await sended_message.delete()
            return
        await sended_message.clear_reactions()
        await sended_message.edit(content= u"Which logs do you want here?\n\U0001F1E6 for users interactions (edits/deletions) \n\U0001F1E7 for admin interactions logs")
        reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\U0001F1E6", u"\U0001F1E7"])
        if reaction == "TimeOut":
            await message.channel.send("Timedout - please try the command again if you were too late!")
            await sended_message.delete()
            return
        elif str(reaction.emoji) == u"\U0001F1E6":
            db_conn.execute("UPDATE GuildSettings SET EditChanl = {0.channel.id} WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
        elif str(reaction.emoji) == u"\U0001F1E7":
            db_conn.execute("UPDATE GuildSettings SET ModChanl = {0.channel.id}, LastModAction = NULL WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
        await sended_message.clear_reactions()
        await sended_message.edit(content= "Succesfull guild settings updated")
        





async def Get_audit_logs(message, client, db_conn, theCursor):
    if message.channel.permissions_for(message.author).view_audit_log == True:
        result = theCursor.execute("SELECT GuildID, GuildName, EditChanl, ModChanl, LastModAction, RankSys FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
        result = result.fetchall()
        for row in result:
            ModChanl = row[3]

        if ModChanl == None:
            ModChanl = message.channel.id
            
        str_message = ''
        async for entry in message.guild.audit_logs(limit=10):
            if str(entry.action).strip("AuditLogAction.")[:6] == "role_d":
                str_message += '{0.created_at}: {0.user} did {0.action}\n'.format(entry)
            else:
                str_message += '{0.created_at}: {0.user} did {0.action} to {0.target}\n'.format(entry)
        await client.get_channel(int(ModChanl)).send(str_message)


async def log_on_message_edit(before, after, client, db_conn, theCursor):
    result = theCursor.execute("SELECT EditChanl FROM GuildSettings WHERE GuildID = {0.guild.id}".format(before))
    result = result.fetchall()
    for row in result:
        EditChanl =  row[0]
    
    if EditChanl != None:
        embed=discord.Embed(title="Message edit", color=0x00ff00)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.add_field(name="channel", value=after.channel.name, inline=False)
        embed.timestamp = before.edited_at
        embed.set_author(name = before.author.name, url=before.author.avatar_url, icon_url=before.author.default_avatar_url)
        await client.get_channel(int(EditChanl)).send(embed= embed)





async def scan_new_moderatorstuff(client, db_conn, theCursor): 
    while True:
        await asyncio.sleep(30)
        try:
            result = theCursor.execute("SELECT GuildID, ModChanl, LastModAction FROM GuildSettings")
            result = result.fetchall()
            for row in result:
                GuildID = row[0]
                ModChanl = row[1]
                LastModAction = row [2]
                
                if ModChanl == None:
                    continue
                if LastModAction == None:
                    print('None detected')
                    async for entry in client.get_guild(int(GuildID)).audit_logs(limit=1):
                        db_conn.execute("UPDATE GuildSettings SET LastModAction = ? WHERE GuildID = ?",('{0.created_at}: {0.user} did {0.action}'.format(entry),GuildID))
                        db_conn.commit()
                        print('{0.created_at}: {0.user} did {0.action}'.format(entry))
                    continue
                else:
                    count = 0
                    async for entry in client.get_guild(int(GuildID)).audit_logs(limit=10):
                        str_entry = '{0.created_at}: {0.user} did {0.action}'.format(entry)
                        if count == 0:
                            first_entry= str_entry
                            count = 1
                        
                        if str_entry != LastModAction:
                            if entry.user == client.user:
                                continue
                            
                            print("New action detected")
                            action = str(entry.action)
                            embed=discord.Embed(title="Moderator action", color=0x00ff00)
                            embed.add_field(name="Action", value=action.strip("AuditLogAction."), inline=False)
                            embed.timestamp = entry.created_at
                            if  action.strip("AuditLogAction.")[:4] == "role":
                                embed.add_field(name="Target", value=client.get_guild(int(GuildID)).get_role(entry.target.id), inline=False)
                            else:
                                embed.add_field(name="Target", value=entry.target, inline=False)
                            
                            embed.set_author(name = entry.user.name, url=entry.user.avatar_url, icon_url=entry.user.default_avatar_url)
                            
                            await client.get_channel(int(ModChanl)).send(embed=embed)
                        else:
                            break
                    db_conn.execute("UPDATE GuildSettings SET LastModAction = ? WHERE GuildID = ?",(first_entry,GuildID))
                    db_conn.commit()
        except aiohttp.client_exceptions.ClientConnectorError:
            print("Error aiohttp.client_exceptions.ClientConnectorError apeard", datetime.datetime.now())
        except:
            continue








async def autoroles(message, client, db_conn, theCursor):
    if not message.channel.permissions_for(message.author).administrator:
        return
    
    sended_message = await message.channel.send(Autorolemessage)
    try:
        reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\u2705", u"\u274C"]) #{u"\u274C": "red cross",  u"\u2705": "Green V"}
    except asyncio.TimeoutError: 
        await message.channel.send("Timedout - please try the command again, you were too slow!")
        await sended_message.delete()
        return
    if str(reaction.emoji) == u"\u274C":
        await sended_message.delete()
        return




    await sended_message.clear_reactions()
    await sended_message.edit(content = "Please enter a name for the role you want to assign. \nIt can either be a excisting role or a new one.")
    
    while True:
        autoroles = []
        result = theCursor.execute("SELECT * FROM AutoRoles WHERE GuildID = {0}".format(message.guild.id))
        print('checking roles!')
        result = result.fetchall()
        for row in result:
            role_id = row[2]
            autoroles+=[role_id]
        try:
            react_message = await utility.await_message(client, message.author, message.channel, timeout = 60)
            role = await utility.check_rolename_excist(react_message.guild, react_message.content) #return role if excist else None
            if role == None:
                role = await react_message.guild.create_role(name = react_message.content)
            else:
                for role_id in autoroles: 
                    if int(role_id) == role.id:
                        await react_message.delete()
                        await sended_message.channel.send("Role has already a autoroles message assigned, please try other rolename or delete previous autorole message",delete_after=10)
                        raise ErrorCode("AutoroleExsist")
            break #loop when succesfully get the role and past all checks
        
        except asyncio.TimeoutError: 
            await message.channel.send("Timedout - please try the command again, you were too slow!")
            await sended_message.delete()
            return
        except InvalidArgument: #Not tested as I didn't found any forbidden character on my keyboard yet
            await sended_message.channel.send("invalid role name, please enter a correct one :-)\nTry again!",delete_after=10)
        except ErrorCode as err:
            if err.code== "AutoroleExsist":
                print("Role Exsist")
    await react_message.delete()
    #sended_message and role are defined
    

    await sended_message.edit(content = u"Do you want opt-in or op-out for auto-role?\n\U0001F1E6 opt-in (= react to get role) \n\U0001F1E7 opt-out (=reactio to remove the role)")
    try:
        reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [u"\U0001F1E6", u"\U0001F1E7"])
    except asyncio.TimeoutError:
        await message.channel.send("Timedout - please try the command again, you were too slow!")
        await sended_message.delete()
        return
    if str(reaction.emoji) == u"\U0001F1E6":
        option = "in"
    elif str(reaction.emoji) == u"\U0001F1E7":
        option = "out"
    await sended_message.clear_reactions()
    #sended_message, role and option are defined
    
    
    await sended_message.edit(content = "Please add any emoji on this message, that emoji will be used as the autorole emoji")
    reaction = await utility.get_reaction(message, message.author, client, timeout = 60)
    emoji = str(reaction.emoji)
    #sended_message, role, option and emoji are defined
    
    
    await sended_message.edit(content = "You next message will be used as autorole message, please provide a message within 60 seconds \nps. You can always edit afterwards ;)")
    try:
        reaction = await utility.await_message(client, message.author, message.channel, timeout = 60)
    except asyncio.TimeoutError: 
        await message.channel.send("Timedout - please try the command again, you were too slow!")
        await sended_message.delete()
        return
    # all defined
    
    
    await sended_message.delete()
    await reaction.add_reaction(emoji)
    
    
    
    
    
    db_conn.execute("INSERT INTO AutoRoles(GuildID, GuildName, role_id, channel_id,message_id, emoji, option) VALUES (?,?,?,?,?,?,?)",
                    (sended_message.guild.id,sended_message.guild.name,role.id,sended_message.channel.id,reaction.id,emoji,option))
    db_conn.commit()
    #autorole is saved
    
    
    
async def delete_messages(message, client, theCursor):
    try:
        amount = int(message.content.strip("!delete")) + 1
    except ValueError:
        amount = 2
    messages = await message.channel.history(limit=amount).flatten()
    await message.channel.delete_messages(messages)
    result = theCursor.execute("SELECT ModChanl FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
    result = result.fetchall()
    for row in result:
        ModChanl = row[0]


    amount -= 1
    if ModChanl != None:
        embed=discord.Embed(title="Moderator action", color=0x00ff00)
        embed.add_field(name="Action", value="Bulk delete {0} messages".format(amount), inline=False)
        embed.timestamp = message.created_at
        embed.add_field(name="Target", value=message.channel.name, inline=False)
        
        embed.set_author(name = message.author.name, url=message.author.avatar_url, icon_url=message.author.default_avatar_url)
        
        await client.get_channel(int(ModChanl)).send(embed=embed)





    

async def Stop_guild(message, client, db_conn):
    sended_message = await message.channel.send("Do you want to remove this guild? \n\u2705 => Will delete all guild settings and stop the bot working in your guild!\n\u274C => To cancel the command!")
    try:
        reaction = await utility.get_reaction(sended_message, message.author, client, timeout = 60, reactions = [ u"\u2705","\u274C"]) #{u"\u274C": "red cross",  u"\u2705": "Green V"}
    except asyncio.TimeoutError: 
        await message.channel.send("Timedout - please try the command again if you were too late!")
        await sended_message.delete()
        return
    if str(reaction.emoji) == u"\u274C":
        await sended_message.delete()
    elif str(reaction.emoji) == u"\u2705":
        print("delting channel")
        db_conn.execute("DELETE FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message)) # => id is always good ;-)
        db_conn.commit()
        await message.channel.send("Deleted all guildsettings! \nRank system is still archived, but no exp will be gained!")


async def settings(message, client, theCursor):
    
    result = theCursor.execute("SELECT GuildID, GuildName, EditChanl, ModChanl, LastModAction, RankSys FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
    result = result.fetchall()
    # You receive a list of lists that hold the result
    for row in result:
        GuildID = row[0]
        GuildName= row[1]
        EditChanl = row[2]
        if EditChanl != None:
            EditChanlName = message.guild.get_channel(int(EditChanl)).name
        else:
            EditChanlName = "Not defined"
            
        ModChanl = row[3]
        if ModChanl != None:
            ModChanlName = message.guild.get_channel(int(ModChanl)).name
        else:
            ModChanlName = "Not defined"
        LastModAction = row[4]
        if row[5] == 1:
            RankSys = "On"
        else:
            RankSys = "Off"
            
        setting_message = "The setting for your guild:\nguildID: `{0}`\nEdit log channel: `#{1}`\nModerator log channel: `#{2}`\nRanksystem: `{3}`".format(GuildID,EditChanlName, ModChanlName, RankSys)
    await message.channel.send(setting_message)



Autorolemessage= u"""Do you want to set a message with reaction for autoroles?
Autorole = poeple get automatically a role assigned when they add or remove their reaction on the message.

You have two option: 
`opt-in` => When poeple react they get a role assinged
`opt-out`=> When poeple react a role gets removed (on start everyone get's the role)

If the bot ever missed a role press `!role` to force him to recheck every role. 
This means the only way to change someone role is to react on the messag...

Press \u2705 to continue
Press \u274C to stop

"""




    




