# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 22:27:44 2019

@author: stijn
"""

import asyncio




async def get_reaction(message, author, client, timeout = 60, reactions= []):
    for reaction in reactions:
        await message.add_reaction(reaction)
    def check_reaction(reaction, user):
        if reactions:
            if str(reaction.emoji) in reactions and user == author:
                return True
        else:
            if user == message.author:
                return True
    reaction, user = await client.wait_for('reaction_add', timeout=timeout, check=check_reaction)
    return reaction





async def find_message(channel_id, message_id, client):
    return await client.get_channel(channel_id).fetch_message(message_id)
    



async def reaction_choise(message, author, client, timeout = 60):
    await message.add_reaction(u"\U0001F1E6") #Green V
    await message.add_reaction(u"\U0001F1E7") 

    def check_reaction(reaction, user):
        if user == author and str(reaction.emoji) == u"\U0001F1E6":
            return True
        if user == author and str(reaction.emoji) == u"\U0001F1E7":
            return True
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=timeout, check=check_reaction)
        print("reaction_choise test")
    except asyncio.TimeoutError: 
        return "TimeOut"
    
    if str(reaction.emoji) == u"\U0001F1E6":
        return "A"
    if str(reaction.emoji) == u"\U0001F1E7":
        return "B"

    

async def await_message(client, author, channel, timeout = 60):
    def check_message(m):
        if m.author == author and m.channel == channel:
            return True
    reaction = await client.wait_for('message', timeout=timeout, check=check_message)
    return reaction



async def check_rolename_excist(guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return role #When role name already excist 
    return None #when nothing is found
