# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 22:24:45 2019

@author: Admin
"""
import commands_def
import rank_system
import sqlite3
import autoroles
import asyncio
import discord

async def commands(client, message, db_conn, theCursor):
    if message.content.startswith('!test'):
        await message.channel.send('I\'m online and working!')
    elif message.content.startswith('!ReStart'): #Restart server => Not tested and probably brake the bot enerily now
        if not message.channel.permissions_for(message.author).administrator:
            return
#                rank_df = await rank_system.on_first_guild_boot_rank(message.guild)
#                
#                autoroles = []
#                with open('autoroles.csv',"w"):
#                    return
    elif message.content.startswith("!help"):
        await message.channel.send(helptext)

    elif message.content.startswith("!logchannel"):
        if discord.channel.TextChannel == type(message.channel):

            await commands_def.Log_command(message, client, db_conn, theCursor)
        
    elif message.content.startswith("!audit"):
        if discord.channel.TextChannel == type(message.channel):

            await commands_def.Get_audit_logs(message, client, db_conn, theCursor)
        
    elif message.content.startswith("!autorole"):
        await commands_def.autoroles(message, client, db_conn, theCursor)
        await asyncio.sleep(5)
        await autoroles.check_roles(db_conn, theCursor, client)
        
    elif message.content.startswith("!stoplog"):
        if discord.channel.TextChannel == type(message.channel):

            db_conn.execute("UPDATE GuildSettings SET EditChanl = NULL, ModChanl = NULL, LastModAction = NULL  WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await message.channel.send("Stop all logging for this guild!")
    elif message.content.startswith("!rank"):
        if discord.channel.TextChannel == type(message.channel):
            if len(message.mentions) == 0:
                await rank_system.get_rank(message, message.author, theCursor, db_conn)
            else:
                for member in message.mentions:
                    await rank_system.get_rank(message, member, theCursor, db_conn)
        elif discord.channel.DMChannel == type(message.channel):
            print("private channel")
            await rank_system.Get_all_ranks(client, message, theCursor, db_conn)

    elif message.content.startswith("!list"):
        if discord.channel.TextChannel == type(message.channel):
            await rank_system.get_list(message, message.author, theCursor, db_conn)
            

        elif discord.channel.DMChannel == type(message.channel):
            print("private channel")
            await rank_system.Get_all_ranks(client, message, theCursor, db_conn)
    elif message.content.startswith("!roles"):
        if discord.channel.TextChannel == type(message.channel):
            if not message.channel.permissions_for(message.author).administrator:
                return
            await autoroles.check_roles(db_conn, theCursor, client)
        
        
    
    
    elif  message.content.startswith("!startguilding"):
        if discord.channel.TextChannel == type(message.channel):
            if not message.channel.permissions_for(message.author).administrator:
                return
            await message.channel.send("Startguilding!")
            try:
                db_conn.execute("INSERT INTO GuildSettings(GuildID, GuildName) VALUES (?,?)",(message.guild.id, message.guild.name))
                db_conn.commit()
            except sqlite3.IntegrityError:
                print("Guild already started")
            
    elif  message.content.startswith("!stopguild"):
        if discord.channel.TextChannel == type(message.channel):
            if not message.channel.permissions_for(message.author).administrator:
                return
            await commands_def.Stop_guild(message, client, db_conn)
    
    
    elif  message.content.startswith("!startrank"):
        if not message.channel.permissions_for(message.author).administrator:
            return
        db_conn.execute("UPDATE GuildSettings SET ranksys = 1 WHERE GuildID = {0.guild.id}".format(message))
        db_conn.commit()
        await message.channel.send("Ranking has started for this guild!")
    elif  message.content.startswith("!stoprank"):
        if discord.channel.TextChannel == type(message.channel):
            if not message.channel.permissions_for(message.author).administrator:
                return
            db_conn.execute("UPDATE GuildSettings SET ranksys = NULL WHERE GuildID = {0.guild.id}".format(message))
            db_conn.commit()
            await message.channel.send("Rank system is still archived, but no exp will be gained!\nYou can resume the ranking at any time by sending `!startrank`!")
    elif  message.content.startswith("!Cleanroles"):
        if not message.channel.permissions_for(message.author).administrator:
            return
        autoroles.get_autoroles(client, db_conn, theCursor)
    
    elif message.content.startswith("!delete"):
        if not message.channel.permissions_for(message.author).administrator:
            return
        await commands_def.delete_messages(message, client, theCursor) 
        
    elif  message.content.startswith("!settings"):
        if discord.channel.TextChannel == type(message.channel):
            if not message.channel.permissions_for(message.author).administrator:
                return
            await commands_def.settings(message, client, theCursor)

        
helptext= """Available for all users:
`!test` test is bot still react on messages 
`!rank` return current user rnag in the guild


Needing admin rights in the guild:
`!startguilding` enable bot in the server
`!stopguild` disable bot in guild and delete all settings!!!!
`!logchannel` enables you to changes the channel where the bot logs changes (dived into moderator stuff and message edits/deletes)
`!stoplog` stops all logging of the bot for the guild
`!audit` return last 10 moderator stuff
`!autorole` used to setup autorole messages
`!roles` Trigger check of all autoroles to see if any are missed 
`!startrank` Will start the rank system in the guild
`!stoprank` Will stop the rank system in the guild
`!delete` delete last message provide a number to delete last x message from the channel"""