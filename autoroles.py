# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 22:35:07 2019

@author: Admin
"""
import discord



async def get_autoroles(client, db_conn, theCursor):
    
    autoroles = theCursor.execute("SELECT * FROM AutoRoles").fetchall()
    i=0
    
    for autorole in autoroles:
        i+=1
        GuildID = autorole[0]
        role_id = autorole[2]
        channel_id = autorole[3]
        message_id = autorole[4]
        try:
            await client.get_guild(int(GuildID)).get_channel(int(channel_id)).fetch_message(int(message_id))
        except discord.errors.NotFound:
            i-=1
            db_conn.execute("DELETE FROM AutoRoles WHERE GuildID = {0} AND role_id = {1}".format(GuildID, role_id)) # => id is always good ;-)
            db_conn.commit()
            print("autorole deleted?")
    print('got autoroles total: ', i)
    




async def check_roles(db_conn, theCursor, client):
    result = theCursor.execute("SELECT * FROM AutoRoles")
    print('checking roles!')
    result = result.fetchall()
    for autorole in result:
        GuildID = autorole[0]
        role_id = autorole[2]
        channel_id = autorole[3]
        message_id = autorole[4]
        emoji = autorole[5]
        option = autorole[6]
        
        guild = client.get_guild(int(GuildID))
        role = guild.get_role(int(role_id))
        channel = guild.get_channel(int(channel_id))
        message = await channel.fetch_message(int(message_id))
        for reaction in message.reactions:
            if str(reaction.emoji) == emoji:
                reaction_users = []
                if option == "in":
                    async for user in reaction.users(limit=None, after=None):
                        reaction_users += [user]
                        if user in role.members:
                            continue
                        else:
                            print("gave role to ", user.name)
                            await user.add_roles(role)
                    for member in role.members:
                        if member not in reaction_users:
                            print("GOt deviant")
                            await member.remove_roles(role)
                elif option == "out":
                    async for user in reaction.users(limit=None, after=None):
                        reaction_users += [user]
                        if user in role.members:
                            print("here, remove role of ", user.name)
                            await user.remove_roles(role)
                    for member in channel.members:
                        if member not in reaction_users and member not in role.members:
                            print("here, Got deviant ", member.name)
                            await member.add_roles(role)
    print("Roles checked!")