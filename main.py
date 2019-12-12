# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 22:34:15 2019

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 17:04:32 2019

@author: Admin
"""
import sqlite3
import importlib
import asyncio
import datetime
import discord  #pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
                #discord documentation: https://discordpy.readthedocs.io/en/rewrite/api.html



import commands_def
import rank_system
import autoroles
import command


import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



'''
Used to check all nightbot commands ;-)
#          
#HTML = requests.get("https://api.nightbot.tv/1/commands", headers = headers).content.decode("utf-8")
#
#g = re.search("\"_total\":",HTML)        
#HTML = HTML[g.end():]
#g = re.search(",",HTML)        
##Total_commands = int(HTML[:g.start()])
##        print (Total_commands)
#HTML = HTML [g.end()+26:-3]
#
#commands = HTML.split("},{")
#for i in range(len(commands)):
#    commands[i] = commands[i].split(",")
#    commands[i] = [commands[i][3][8:-1],commands[i][7][11:-1]]
#
##
'''

#reactions can be found at: https://www.fileformat.info/info/unicode/char/search.htm




token = "Super secret!"

class MyClient(discord.Client):
    async def on_ready(self):
        print('Start mods')
        asyncio.create_task(commands_def.scan_new_moderatorstuff(client,db_conn, theCursor))
        print("Start autoroles")
        await autoroles.get_autoroles(client, db_conn, theCursor)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await autoroles.check_roles(db_conn, theCursor, client)
        
        
        
        
        
        
    async def on_message(self, message):
        if message.author == self.user:
        # don't respond to ourselves bot, you fool!
            return
        
        
        
        
        if discord.channel.TextChannel == type(message.channel) and not message.content.startswith("!startguilding"):
            result = theCursor.execute("SELECT GuildName FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
            result = result.fetchall()
            if result == []:
                return
        if message.content[0] == "!":            
            await command.commands(self, message, db_conn, theCursor)
            
        if discord.channel.TextChannel == type(message.channel):
            await rank_system.on_message_rank(client, message, db_conn, theCursor)
        
        


    async def on_message_edit(self, before, after):
        if before.author == self.user:
        # don't respond to ourselves bot and prevent infinate spam here :D
            return
        await commands_def.log_on_message_edit(before, after, client, db_conn, theCursor)
        
    async def on_message_delete(self, message):
        result = theCursor.execute("SELECT EditChanl FROM GuildSettings WHERE GuildID = {0.guild.id}".format(message))
        result = result.fetchall()
        for row in result:
            EditChanl =  row[0]
        
        if EditChanl != None:
            embed=discord.Embed(title="Message deletion", color=0x00ff00)
            embed.add_field(name="Deleted message", value=message.content)
            embed.add_field(name="Posted orginal at", value=message.created_at.strftime("%b %d %H:%M.%S"))
            embed.add_field(name="channel", value=message.channel.name)
            embed.timestamp = datetime.datetime.now()
            embed.set_author(name = message.author.name, url=message.author.avatar_url, icon_url=message.author.default_avatar_url)
            await client.get_channel(int(EditChanl)).send(embed= embed)

    async def on_raw_message_delete(self, payload):
        db_conn.execute("DELETE FROM AutoRoles WHERE message_id = {0}  AND GuildID= {1} AND channel_id = {2} ".format(int(payload.message_id), int(payload.guild_id), int(payload.channel_id)))
        db_conn.commit()

    
    async def on_raw_reaction_add(self, payload):
        result = theCursor.execute("SELECT * FROM AutoRoles WHERE message_id = ? AND emoji= ? AND GuildID= ? AND channel_id = ? ",
                                   (int(payload.message_id), str(payload.emoji), int(payload.guild_id), int(payload.channel_id)))
        result = theCursor.fetchall()
        for row in result:
            GuildID = row[0]
            role_id = row[2]
            option = row[6]
#            
#            for autorole in autoroles:
#                message_int = int(message_id)
#                if payload.message_id == message_int:
#                    if str(payload.emoji) == emoji:
            guild = client.get_guild(int(GuildID))
            for member in guild.members:
                if member.id == payload.user_id:
                    role = guild.get_role(int(role_id))
                    if   option == "in":
                        await member.add_roles(role)
                        return
                    elif option == "out":
                        await member.remove_roles(role)
                        return
        
    async def on_raw_reaction_remove(self, payload):
        result = theCursor.execute("SELECT * FROM AutoRoles WHERE message_id = ? AND emoji= ? AND GuildID= ? AND channel_id = ? ",
                                   (int(payload.message_id), str(payload.emoji), int(payload.guild_id), int(payload.channel_id)))
        result = result.fetchall()
        for row in result:
            GuildID = row[0]
            role_id = row[2]
            option = row[6]
            guild = client.get_guild(int(GuildID))
            for member in guild.members:
                if member.id == payload.user_id:
                    role = guild.get_role(int(role_id))
                    if   option == "out":
                        await member.add_roles(role)
                        return
                    elif option == "in":
                        await member.remove_roles(role)
                        return

    async def on_member_join(self, member):
        result = theCursor.execute("SELECT * FROM AutoRoles WHERE GuildID= ? ",(member.guild.id))
        result = result.fetchall()
        for row in result:
            role_id = row[2]
            option = row[6]
            if option == "out":
                role = member.guild.get_role(int(role_id))
                await member.add_roles(role)







async def Check_Commands(): #scan every 30 to new commands in .txt file
    global commands 
    count = 1
    
    importlib.reload(commands_def)
    importlib.reload(rank_system)
    print("commands_def updated ", count, end = "\r")
    count += 1
    commands = []
    with open("Commands.txt","r") as txt:
        archive = txt.readlines()
        for i in archive:
            commands += [i.split(";")]





global db_conn
global theCursor
db_conn = sqlite3.connect('PythonBotStinosko.db')
theCursor = db_conn.cursor()


def printDB():
    # To retrieve data from a table use SELECT followed
    # by the items to retrieve and the table to
    # retrieve from
 
    try:
        result = theCursor.execute("SELECT GuildID, GuildName, EditChanl, ModChanl, LastModAction, RankSys FROM GuildSettings")
        result = result.fetchall()
        # You receive a list of lists that hold the result
        for row in result:
            print("GuildID :", row[0])
            print("GuildName :", row[1])
            print("EditChanl :", row[2])
            print("ModChanl :", row[3])
            print("LastModAction :", row[4])
            print("RankSys :", row[5])
 
    except sqlite3.OperationalError:
        print("The Table Doesn't Exist")
 
    except:
        print("Couldn't Retrieve Data From Database")

"""
# initiate the database if you start over
db_conn.execute("CREATE TABLE GuildSettings(GuildID INTEGER PRIMARY KEY NOT NULL, GuildName TEXT NOT NULL, EditChanl INTEGER DEFAULT NULL, ModChanl INTEGER DEFAULT NULL, LastModAction TXT DEFAULT NULL, ranksys INTEGER DEFAULT NULL);")
db_conn.commit()

db_conn.execute("CREATE TABLE AutoRoles(GuildID INTEGER NOT NULL, GuildName TEXT NOT NULL, role_id INTEGER NOT NULL, channel_id INTEGER NOT NULL,message_id INTEGER NOT NULL, emoji TXT NO NULL, option TEXT NOT NULL);")
db_conn.commit()

db_conn.execute("CREATE TABLE RankSystem(GuildID INTEGER NOT NULL, GuildName TEXT NOT NULL, user_id INTEGER NOT NULL, UserName TEXT NOT NULL, exp INTEGER NOT NULL DEFAULT 0,level INTEGER NOT NULL DEFAULT 0, Date_time_joined INTEGER NOT NULL, last_message INTEGER NOT NULL DEFAULT 0);")
db_conn.commit()

"""



client = MyClient()

print("Starting discord!")
asyncio.run(client.run(token)) #Here we start the bot
print("Discord has shut down (should never be happening)")


