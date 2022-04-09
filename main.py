#Imports
import discord
from discord.ext import commands
from discord.ext.commands import *
from discord.ext import tasks
import os
import os.path
import json
import time
import asyncio
import random
import datetime
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import api.auth
import utils.logger

# Slash option types:
# sub command: 1
# sub command group: 2
# string: 3
# int: 4
# bool: 5
# user: 6
# channel: 7
# role: 8

#Variables
client = commands.Bot(command_prefix='s!', intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
color = discord.Color.random()
with open('./Desktop/Stock/database/currency.json', 'r') as f:
    global currency
    currency = json.load(f)
with open('./Desktop/Stock/database/warnings.json', 'r') as f:
    global warnings
    warnings = json.load(f)

#Pre-Initialization Commands
def timenow(): 
    datetime.datetime.now().strftime("%H:%M:%S")
def save():
    with open('./Desktop/Stock/database/currency.json', 'w+') as f:
        json.dump(currency, f, indent=4)
    with open(f'./Desktop/Stock/database/warnings.json', 'w+') as f:
        json.dump(warnings, f, indent=4)

#Classes
class colors:
    cyan = '\033[96m'
    red = '\033[91m'
    green = '\033[92m'
    end = '\033[0m'

#Events
@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + '.')
    print('Ready to accept commands.')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"Salad"), status=discord.Status.idle)
    print(f'[main/LOG] {colors.green}Status set to IDLE. Rich presence set.{colors.end}')

@client.event
async def on_message(ctx):
    if (str(ctx.author.id) in currency['cash']):
        pass
    else:
        currency['cash'][str(ctx.author.id)] = 5000
    if (str(ctx.author.id) in currency['crypto']):
        pass
    else:
        currency['crypto'][str(ctx.author.id)] = 0
    if str(ctx.guild.id) in warnings:
        pass
    else:
        warnings[str(ctx.guild.id)] = {}
    if str(ctx.author.id) in warnings[str(ctx.guild.id)]:
        pass
    else:
        warnings[str(ctx.guild.id)][str(ctx.author.id)] = []
    save()

#Error handler
@client.event
async def on_command_error(ctx, error):
    current_time = timenow()
    if isinstance(error, CommandNotFound):
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at CommandNotFound. Details: This command does not exist.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}CommandNotFound{colors.end}. Details: This command does not exist.')
        else:
            pass
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f':stopwatch: Not now! Please try after **{str(datetime.timedelta(seconds=int(round(error.retry_after))))}**')
        if os.name == 'nt':
            print(f'[{current_time}] Ignoring exception at {colors.cyan}CommandOnCooldown{colors.end}. Details: This command is currently on cooldown.')
        else:
            pass
    if isinstance(error, MissingRequiredArgument):
        await ctx.send(':warning: Missing required argument(s)', delete_after=8)
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at MissingRequiredArgument. Details: The command can\'t be executed because required arguments are missing.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}MissingRequiredArgument{colors.end}. Details: The command can\'t be executed because required arguments are missing.')
        else:
            pass
    if isinstance(error, MissingPermissions):
        await ctx.send('You don\'t have permission to do this!', hidden=True)
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at MissingPermissions. Details: The user doesn\'t have the required permissions.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}MissingPermissions{colors.end}. Details: The user doesn\'t have the required permissions.')
        else:
            pass
    if isinstance(error, BadArgument):
        await ctx.send(':x: Invalid argument.', delete_after=8)
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at BadArgument.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}BadArgument{colors.end}.')
        else:
            pass
    if isinstance(error, BotMissingPermissions):
        await ctx.send(':x: I don\'t have the required permissions to use this.')
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at BotMissingPermissions.\n Details: The bot doesn\'t have the required permissions.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}BotMissingPremissions{colors.end}. Details: The bot doesn\'t have the required permissions.')
        else:
            pass
    if isinstance(error, BadBoolArgument):
        await ctx.send(':x: Invalid true/false argument.', delete_after=8)
        if os.name == 'nt':
            with open(errorHandler_path, 'a') as f:
                f.write(f'[{current_time}] Ignoring exception at BadBoolArgument.\n')
                f.close()
            print(f'[{current_time}] Ignoring exception at {colors.cyan}BadBoolArgument{colors.end}.')
        else:
            pass
    else:
        report_target = client.get_user(738290097170153472)
        report_target.send(f'An unhandled exception occured during command execution: {error}')
        await ctx.send(f'An unhandled exception occured: {error}. This has automatically been reported to the devs.')

#Commands
@slash.slash(name='balance', description='Shows your balance, or another user\'s balance.', options=[create_option(name='user', description='The user\'s balance you want to see.', option_type=6, required=False)])
async def balance(ctx:SlashContext, user=None):
    try:
        if user == None:
            e = discord.Embed(title=f'{ctx.author.display_name}\'s balance', color=color)
            e.add_field(name='Cash', value=currency['cash'][str(ctx.author.id)], inline=True)
            e.add_field(name='Crypto-currency', value=f'{currency["crypto"][str(ctx.author.id)]} ISOcoins', inline=True)
            await ctx.send(embed=e)
        else:
            try:
                e = discord.Embed(title=f'{user.display_name}\'s balance', color=color)
                e.add_field(name='Cash', value=currency['cash'][str(user.id)], inline=True)
                e.add_field(name='Crypto-currency', value=f'{currency["crypto"][str(user.id)]} ISOcoins', inline=True)
                await ctx.send(embed=e)
            except:
                await ctx.reply('Looks like that user is not indexed in our server. Try again later.')
                return
    except Exception as e:
        await ctx.send(f'An error occured: `{e}`. This has automatically been reported to the devs.')

@slash.slash(
    name='kick', 
    description='Kicks a member from this server.', 
    options=[
        create_option(name='user', description='The user you will kick', option_type=6, required=True), 
        create_option(name='reason', description='Why you want to kick the user', option_type=3, required=False)
    ]
)
async def kick(ctx:SlashContext, user, reason=None):
    if not ctx.author.guild_permissions.kick_members:
        raise(MissingPermissions)
    else:
        try:
            if reason == None: await user.kick()
            else: await user.kick(reason=reason)
            await ctx.send(embed=discord.Embed(title=f'{user} has been kicked.', description=f'Reason: {str(reason)}'))
        except:
            await ctx.send(embed=discord.Embed(title='Well, something happened...', description='Either I don\'t have permission to do this, or my role isn\'t high enough.', color=discord.Colour.red()))

@slash.slash(
    name='ban', 
    description='Bans a member from this server.', 
    options=[
        create_option(name='user', description='The user you will ban', option_type=6, required=True), 
        create_option(name='reason', description='Why you want to ban the user', option_type=3, required=False)
    ]
)
async def ban(ctx:SlashContext, user, reason=None):
    if not ctx.author.guild_permissions.ban_members:
        raise(MissingPermissions)
    else:
        try:
            if reason == None: await user.ban()
            else: await user.ban(reason=reason)
            await ctx.send(embed=discord.Embed(title=f'{user} has been banned.', description=f'Reason: {str(reason)}'))
        except:
            await ctx.send(embed=discord.Embed(title='Well, something happened...', description='Either I don\'t have permission to do this, or my role isn\'t high enough.', color=discord.Colour.red()))

@slash.slash(
    name='warn',
    description='Warn someone in your server.',
    options=[
        create_option(name='user', description='The person you want to warn', option_type=6, required=True),
        create_option(name='reason', description='Why you are warning the user', option_type=3, required=True)
    ]
)
async def warn(ctx:SlashContext, user, reason):
    if not ctx.author.guild_permissions.manage_messages:
        raise(MissingPermissions)
    warnings[str(ctx.guild.id)][str(user.id)].append('reason')
    save()
    target=client.get_user(user.id)
    try:
        await target.send(embed=discord.Embed(title=f':warning: You\'ve been warned in {ctx.guild} ({ctx.guild.id})', description=f'Reason {reason}'))
        await ctx.send(embed=discord.Embed(description=f'{user} has been warned. I couldn\'t DM them, but their warning is logged.'))
    except:
        await ctx.send(embed=discord.Embed(description=f'{user} has been warned. I couldn\'t DM them, but their warning is logged.'))

@slash.slash(
    name='warns_clear',
    description='Clear someone\'s warnings.',
    options=[
        create_option(name='user', description='The person you want to remove warns from', option_type=6, required=True)
    ]
)
async def warn_clear(ctx:SlashContext, user):
    if not ctx.author.guild_permissions.manage_messages:
        raise(MissingPermissions)
    warnings[str(ctx.guild.id)][str(user.id)] = []
    save()
    await ctx.send(embed=discord.Embed(description=f'All warnings have been cleared for {user}.'))

# Initialization
client.run(api.auth.token)