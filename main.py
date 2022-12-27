#Imports
import os
import os.path
import psutil
import json
import time, datetime
import discord
import asyncio
import random
import praw
import api.auth
import utils.logger, utils.ping
from framework import *
from math import floor, sqrt
from random import randint
import framework.isobot.currency, framework.isobot.colors, framework.isobank.authorize, framework.isobank.manager, framework.isobot.embedengine
from discord import ApplicationContext, option
from discord.ext import commands, tasks
from discord.ext.commands import *
from threading import Thread

# Slash option types:
# Just use variable types to define option types.
# For example, if the option has to be only str:
# @option(name="something", description="A description", type=str)

#Variables
client = discord.Bot()
color = discord.Color.random()
wdir = os.getcwd()
reddit = praw.Reddit(client_id='_pazwWZHi9JldA', client_secret='1tq1HM7UMEGIro6LlwtlmQYJ1jB4vQ', user_agent='idk', check_for_async=False)
with open('database/warnings.json', 'r') as f: warnings = json.load(f)
with open('database/items.json', 'r') as f: items = json.load(f)
with open('config/shop.json', 'r') as f: shopitem = json.load(f)
with open('database/presence.json', 'r') as f: presence = json.load(f)
with open('database/levels.json', 'r') as f: levels = json.load(f)
with open('config/commands.json', 'r') as f: commandsdb = json.load(f)
with open('database/automod.json', 'r') as f: automod_config = json.load(f)

with open('database/special/new_years_2022.json', 'r') as f: presents = json.load(f)  # Temp

#Pre-Initialization Commands
def timenow(): datetime.datetime.now().strftime("%H:%M:%S")
def save():
    with open('database/warnings.json', 'w+') as f: json.dump(warnings, f, indent=4)
    with open('database/items.json', 'w+') as f: json.dump(items, f, indent=4)
    with open('database/presence.json', 'w+') as f: json.dump(presence, f, indent=4)
    with open('database/levels.json', 'w+') as f: json.dump(levels, f, indent=4)
    with open('database/automod.json', 'w+') as f: json.dump(automod_config, f, indent=4)
    with open('database/special/new_years_2022.json', 'w+') as f: json.dump(presents, f, indent=4)  # Temp

def get_user_networth(user_id:int):
    nw = currency["wallet"][str(user_id)] + currency["bank"][str(user_id)]
    #for e in items[str(user_id)]:
    #    if e != 0: nw += shopitem[e]["sell price"]
    return nw

if not os.path.isdir("logs"):
    os.mkdir('logs')
    try:
        open('logs/info-log.txt', 'x')
        utils.logger.info("Created info log", nolog=True)
        time.sleep(0.5)
        open('logs/error-log.txt', 'x')
        utils.logger.info("Created error log", nolog=True)
        time.sleep(0.5)
        open('logs/currency.log', 'x')
        utils.logger.info("Created currency log", nolog=True)
    except Exception as e: utils.logger.error(f"Failed to make log file: {e}", nolog=True)

#Classes
class plugins:
    economy = True
    moderation = True
    levelling = False
    music = False

class ShopData:
    def __init__(self, db_path: str):
        self.db_path = db_path 
        with open(db_path, 'r') as f: self.config = json.load(f)
        
    def get_item_ids(self) -> list:
        json_list = list()
        for h in self.config: json_list.append(str(h))
        return json_list
    
    def get_item_names(self) -> list:
        json_list = list()
        for h in self.config: json_list.append(str(h["stylized name"]))
        return json_list

#Framework Module Loader
colors = framework.isobot.colors.Colors()
currency_unused = framework.isobot.currency.CurrencyAPI(f'{wdir}/database/currency.json', f"{wdir}/logs/currency.log")  # Initialize part of the framework (Currency)
# isobank = framework.isobank.manager.IsoBankManager(f"{wdir}/database/isobank/accounts.json", f"{wdir}/database/isobank/auth.json")
isobankauth = framework.isobank.authorize.IsobankAuth(f"{wdir}/database/isobank/auth.json", f"{wdir}/database/isobank/accounts.json")
shop_data = ShopData(f"{wdir}/config/shop.json")

all_item_ids = shop_data.get_item_ids()

#Theme Loader
with open("themes/halloween.theme.json", 'r') as f:
    theme = json.load(f)
    try:
        color_loaded = theme["theme"]["embed_color"]
        color = int(color_loaded, 16)
    except KeyError:
        print(f"{colors.red}The theme file being loaded might be broken. Rolling back to default configuration...{colors.end}")
        color = discord.Color.random()

# Discord UI Views
class PresentsDrop(discord.ui.View):
    @discord.ui.button(label="🎁 Collect Presents", style=discord.ButtonStyle.blurple)
    async def receive(self, button: discord.ui.Button, interaction: discord.Interaction):
        presents_bounty = randint(500, 1000)
        presents[str(interaction.user.id)] += presents_bounty
        save()
        button.disabled = True
        button.label = f"Presents Collected!"
        button.style = discord.ButtonStyle.grey
        newembed = discord.Embed(description=f"{interaction.user.name} collected **{presents_bounty} :gift: presents** from this drop!", color=discord.Color.green())
        await interaction.response.edit_message(embed=newembed, view=self)

#Events
@client.event
async def on_ready():
    print("""
Isobot  Copyright (C) 2022  PyBotDevs/NKA
This program comes with ABSOLUTELY NO WARRANTY; for details run `/w'.
This is free software, and you are welcome to redistribute it
under certain conditions; run `/c' for details.
__________________________________________________""")
    time.sleep(2)
    print(f'Logged in as {client.user.name}.')
    print('Ready to accept commands.')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"GitHub"), status=discord.Status.idle)
    print(f'[main/LOG] {colors.green}Status set to IDLE. Rich presence set.{colors.end}')
    print("[main/FLASK] Starting pinger service...")
    utils.ping.host()
    time.sleep(5)
    print("[main/Presents] Presents daemon started.")
    while True:
        print(f"[main/Presents] Dropping new presents in {colors.cyan}#general{colors.end} channel...")
        await asyncio.sleep(randint(450, 600))
        cyberspace_channel_context = await client.fetch_channel(880409977074888718)
        localembed = discord.Embed(title="**:gift: Presents have dropped in chat!**", description="Be the first one to collect them!", color=color)
        await cyberspace_channel_context.send(embed=localembed, view=PresentsDrop()) 

@client.event
async def on_message(ctx):
    if str(ctx.author.id) not in currency['wallet']: currency['wallet'][str(ctx.author.id)] = 5000
    if str(ctx.author.id) not in currency['bank']: currency['bank'][str(ctx.author.id)] = 0
    if str(ctx.guild.id) not in warnings: warnings[str(ctx.guild.id)] = {}
    if str(ctx.author.id) not in warnings[str(ctx.guild.id)]: warnings[str(ctx.guild.id)][str(ctx.author.id)] = []
    if str(ctx.author.id) not in items: items[str(ctx.author.id)] = {}
    if str(ctx.author.id) not in levels: levels[str(ctx.author.id)] = {"xp": 0, "level": 0}
    if str(ctx.guild.id) not in automod_config: automod_config[str(ctx.guild.id)] = \
    {
        "swear_filter": {
            "enabled": False,
            "keywords": {
                "use_default": True,
                "default": ["fuck", "shit", "pussy", "penis", "cock", "vagina", "sex", "moan", "bitch", "hoe", "nigga", "nigger", "xxx", "porn"],
                "custom": []
            }
        }
    }
    for z in shopitem:
        if z in items[str(ctx.author.id)]: pass
        else: items[str(ctx.author.id)][str(z)] = 0
    if str(ctx.author.id) not in presents: presents[str(ctx.author.id)] = 0  # Temp
    save()
    uList = list()
    if str(ctx.guild.id) in presence:
        for x in presence[str(ctx.guild.id)].keys(): uList.append(x)
    else: pass
    for i in uList:
        if i in ctx.content and not ctx.author.bot:
            fetch_user = client.get_user(id(i))
            await ctx.channel.send(f"{fetch_user.display_name} went AFK <t:{floor(presence[str(ctx.guild.id)][str(i)]['time'])}:R>: {presence[str(ctx.guild.id)][str(i)]['response']}")
    if str(ctx.guild.id) in presence and str(ctx.author.id) in presence[str(ctx.guild.id)]:
        del presence[str(ctx.guild.id)][str(ctx.author.id)]
        save()
        m1 = await ctx.channel.send(f"Welcome back {ctx.author.mention}. Your AFK has been removed.")
        await asyncio.sleep(5)
        await m1.delete()
    if not ctx.author.bot:
        levels[str(ctx.author.id)]["xp"] += randint(1, 5)
        xpreq = 0
        for level in range(int(levels[str(ctx.author.id)]["level"])):
            xpreq += 50
            if xpreq >= 5000: break
        if levels[str(ctx.author.id)]["xp"] >= xpreq:
            levels[str(ctx.author.id)]["xp"] = 0
            levels[str(ctx.author.id)]["level"] += 1
            await ctx.author.send(f"{ctx.author.mention}, you just ranked up to **level {levels[str(ctx.author.id)]['level']}**. Nice!")
        save()
        if automod_config[str(ctx.guild.id)]["swear_filter"]["enabled"] == True:
            if automod_config[str(ctx.guild.id)]["swear_filter"]["keywords"]["use_default"] and any(x in ctx.content.lower() for x in automod_config[str(ctx.guild.id)]["swear_filter"]["keywords"]["default"]):
                await ctx.delete()
                await ctx.channel.send(f'{ctx.author.mention} watch your language.', delete_after=5)
            elif automod_config[str(ctx.guild.id)]["swear_filter"]["keywords"]["custom"] is not [] and any(x in ctx.content.lower() for x in automod_config[str(ctx.guild.id)]["swear_filter"]["keywords"]["custom"]):
                await ctx.delete()
                await ctx.channel.send(f'{ctx.author.mention} watch your language.', delete_after=5)

#Error handler
@client.event
async def on_command_error(ctx, error):
    current_time = floor(time.time()).strftime("%H:%M:%S")
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.channel.send(f':stopwatch: Not now! Please try after **{str(datetime.timedelta(seconds=int(round(error.retry_after))))}**')
        print(f'[{current_time}] Ignoring exception at {colors.cyan}CommandOnCooldown{colors.end}. Details: This command is currently on cooldown.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.channel.send('You don\'t have permission to do this!', ephemeral=True)
        print(f'[{current_time}] Ignoring exception at {colors.cyan}MissingPermissions{colors.end}. Details: The user doesn\'t have the required permissions.')
    elif isinstance(error, commands.BadArgument):
        await ctx.channel.send(':x: Invalid argument.', delete_after=8)
        print(f'[{current_time}] Ignoring exception at {colors.cyan}BadArgument{colors.end}.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.channel.send(':x: I don\'t have the required permissions to use this.')
        print(f'[{current_time}] Ignoring exception at {colors.cyan}BotMissingPremissions{colors.end}. Details: The bot doesn\'t have the required permissions.')
    elif isinstance(error, commands.BadBoolArgument):
        await ctx.channel.send(':x: Invalid true/false argument.', delete_after=8)
        print(f'[{current_time}] Ignoring exception at {colors.cyan}BadBoolArgument{colors.end}.')

#Commands
@client.slash_command(
    name="help",
    description="Gives you help with a specific command, or shows a list of all commands"
)
@option(name="command", description="Which command do you need help with?", type=str, default=None)
async def help(ctx: ApplicationContext, command:str=None):
    if command is not None:
        try:
            localembed = discord.Embed(title=f"{commandsdb[command]['name']} Command (/{command})", description=commandsdb[command]['description'], color=color)
            localembed.add_field(name="Command Type", value=commandsdb[command]['type'], inline=False)
            if commandsdb[command]['cooldown'] is not None: localembed.add_field(name="Cooldown", value=f"{str(datetime.timedelta(seconds=commandsdb[command]['cooldown']))}", inline=False)
            localembed.add_field(name="Usable By", value=commandsdb[command]['usable_by'], inline=False)
            if commandsdb[command]['args'] is not None:
                r = ""
                for x in commandsdb[command]['args']: r += f"`{x}` "
                localembed.add_field(name="Arguments", value=r, inline=False)
            if commandsdb[command]['bugged'] == True: localembed.set_footer(text="⚠ This command might be bugged (experiencing issues), but will be fixed later.")
            if commandsdb[command]['disabled'] == True: localembed.set_footer(text="⚠ This command is currently disabled")
            await ctx.respond(embed=localembed)
        except KeyError: return await ctx.respond(embed=discord.Embed(description=f"No results found for {command}."), ephemeral=True)
    else:
        r = ""
        for x in commandsdb: 
            if commandsdb[x]["type"] != "DevTools": r += f"`/{x}`\n"
        localembed = discord.Embed(title="Isobot Command Help", description=f"**Bot Commands:**\n{r}", color = color)
        user = client.fetch_user(ctx.author.id)
        await user.send(embed=localembed)
        await ctx.respond("Check your direct messages.", ephemeral=True)

@client.slash_command(
  name='echo',
  description='Sends a bot message in the channel'
)
@option(name="text", description="What do you want to send?", type=str)
async def echo(ctx: ApplicationContext, text:str): 
    await ctx.respond("Echoed!", ephemeral=True)
    await ctx.channel.send(text)

@client.slash_command(
    name='whoami',
    description='Shows information on a user'
)
@option(name="user", description="Who do you want to know about?", type=discord.User, default=None)
async def whoami(ctx: ApplicationContext, user: discord.User=None):
    if user == None: user = ctx.author
    username = user
    displayname = user.display_name
    registered = user.joined_at.strftime("%b %d, %Y, %T")
    pfp = user.avatar_url
    localembed_desc = f"`AKA` {displayname}"
    if str(user.id) in presence[str(ctx.guild.id)]: localembed_desc += f"\n`🌙 AFK` {presence[str(ctx.guild.id)][str(user.id)]['response']} - <t:{floor(presence[str(ctx.guild.id)][str(user.id)]['time'])}>"
    localembed = discord.Embed(
        title=f'User Info on {username}', 
        description=localembed_desc
    )
    localembed.set_thumbnail(url=pfp)
    localembed.add_field(name='Username', value=username, inline=True)
    localembed.add_field(name='Display Name', value=displayname, inline=True)
    localembed.add_field(name='Joined Discord on', value=registered, inline=False)
    localembed.add_field(name='Avatar URL', value=f"[here!]({pfp})", inline=True)
    role_render = ""
    for p in user.roles:
        if p != user.roles[0]: role_render += f"<@&{p.id}> "
    localembed.add_field(name='Roles', value=role_render, inline=False)
    localembed.add_field(name="Net worth", value=f"{get_user_networth(user.id)} coins", inline=False)
    await ctx.respond(embed=localembed)

# DevTools commands
@client.slash_command(
    name='sync',
    description='Syncs all of the local databases with their latest version'
)
async def sync(ctx: ApplicationContext):
    if ctx.author.id != 738290097170153472: return await ctx.respond('Sorry, this command is only for my developer\'s use.')
    try:
        with open('database/warnings.json', 'r') as f: warnings = json.load(f)
        with open('database/items.json', 'r') as f: items = json.load(f)
        with open('config/shop.json', 'r') as f: shopitem = json.load(f)
        await ctx.respond('Databases resynced.', ephemeral=True)
    except Exception as e:
        print(e)
        await ctx.respond('An error occured while resyncing. Check console.', ephemeral=True)

@client.slash_command(
    name='stroketranslate',
    description='Gives you the ability to make full words and sentences from a cluster of letters'
)
@option(name="strok", description="What do you want to translate?", type=str)
async def stroketranslate(ctx: ApplicationContext, strok: str):
        try:
            if len(strok) > 300: return await ctx.respond("Please use no more than `300` character length", ephemeral=True)
            else:
                with open(f"{os.getcwd()}/config/words.json", "r") as f: words = json.load(f)
                var = str()
                s = strok.lower()
                for i, c in enumerate(s): var += random.choice(words[c])
                return await ctx.respond(f"{var}")
        except Exception as e: return await ctx.respond(f"{type(e).__name__}: {e}")
        var = ''.join(arr)
        await ctx.respond(f"{var}")

@client.slash_command(
    name='prediction',
    description='Randomly predicts a yes/no question.'
)
@option(name="question", description="What do you want to predict?", type=str)
async def prediction(ctx: ApplicationContext, question:str): await ctx.respond(f"My prediction is... **{random.choice(['Yes', 'No'])}!**")

@client.slash_command(
    name="status",
    description="Shows the current client info"
)
async def status(ctx: ApplicationContext):
    os_name = os.name
    sys_ram = str(f"{psutil.virtual_memory()[2]}GiB")
    sys_cpu = str(f"{psutil.cpu_percent(1)}%")
    bot_users = 0
    for x in levels.keys(): bot_users += 1
    localembed = discord.Embed(title="Client Info")
    localembed.add_field(name="OS Name", value=os_name)
    localembed.add_field(name="RAM Available", value=sys_ram)
    localembed.add_field(name="CPU Usage", value=sys_cpu)
    localembed.add_field(name="Registered Users", value=f"{bot_users} users", inline=True)
    localembed.add_field(name="Uptime History", value="[here](https://stats.uptimerobot.com/PlKOmI0Aw8)")
    localembed.add_field(name="Release Notes", value="[latest](https://github.com/PyBotDevs/isobot/releases/latest)")
    localembed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    await ctx.respond(embed=localembed)

# AFK System Commands
afk_system = client.create_group("afk", "Commands for interacting with the built-in AFK system.")

@afk_system.command(
    name="set",
    description="Sets your AFK status with a custom response"
)
@option(name="response", description="What do you want your AFK response to be?", type=str, default="I'm AFK")
async def afk_set(ctx: ApplicationContext, response:str="I'm AFK"):
    exctime = time.time()
    if str(ctx.guild.id) not in presence: presence[str(ctx.guild.id)] = {}
    presence[str(ctx.guild.id)][str(ctx.author.id)] = {"type": "afk", "time": exctime, "response": response}
    save()
    localembed = discord.Embed(title=f"{ctx.author.display_name} is now AFK.", description=f"Response: {response}", color=discord.Color.dark_orange())
    await ctx.respond(embed=localembed)

@afk_system.command(
    name="remove",
    description="Removes your AFK status"
)
async def afk_remove(ctx: ApplicationContext):
    try: 
        del presence[str(ctx.guild.id)][str(ctx.author.id)]
        save()
        await ctx.respond(f"Alright {ctx.author.mention}, I've removed your AFK.")
    except KeyError: return await ctx.respond("You weren't previously AFK.", ephemeral=True)

@afk_system.command(
    name="mod_remove",
    description="Removes an AFK status for someone else"
)
@option(name="user", description="Whose AFK status do you want to remove?", type=discord.User)
async def afk_mod_remove(ctx: ApplicationContext, user:discord.User):
    if not ctx.author.guild_permissions.manage_messages: return await ctx.respond("You don't have the required permissions to use this.", ephemeral=True)
    try: 
        del presence[str(ctx.guild.id)][str(user.id)]
        save()
        await ctx.respond(f"{user.display_name}'s AFK has been removed.")
    except KeyError: return await ctx.respond("That user isn't AFK.", ephemeral=True)

@client.slash_command(
    name="repo",
    description="Shows the open-source code links for isobot."
)
async def repo(ctx: ApplicationContext):
    localembed = discord.Embed(title="Source-code Repositories", description="See and contribute to **isobot's [GitHub repository](https://github.com/PyBotDevs/isobot)**\nSee our **[GitHub organization](https://github.com/PyBotDevs)**", color=color)
    await ctx.respond(embed=localembed)

@client.slash_command(
    name="embedbuilder",
    description="Builds a custom embed however you want"
)
@option(name="title", description="The title of the embed", type=str)
@option(name="description", description="The body of the embed", type=str)
@option(name="image_url", description="The main image you want to show for the embed (URL ONLY)", type=str, default=None)
@option(name="thumbnail_url", description="The thumbnail image you want to show for the embed (URL ONLY)", type=str, default=None)
@option(name="color", description="The embed's accent color (Use -1 for random color)", type=int, default=None)
@option(name="footer_text", description="The text at the footer of the embed", type=str, default=None)
@option(name="footer_icon_url", description="The icon you want to show in the embed's footer (URL ONLY)", type=str, default=None)
async def embedbuilder(ctx: ApplicationContext, title: str, description: str, image_url: str = None, thumbnail_url: str = None, color: int = None, footer_text: str = None, footer_icon_url: str = None):
    await ctx.respond("Embed Built!", ephemeral=True)
    await ctx.channel.send(embed=framework.isobot.embedengine.embed(title, description, image=image_url, thumbnail=thumbnail_url, color=color, footer_text=footer_text, footer_img=footer_icon_url))

@client.slash_command(
    name="profile",
    description="Shows basic stats about your isobot profile, or someone else's profile stats"
)
@option(name="user", description="Whose isobot profile do you want to view?", type=discord.User, default=None)
async def profile(ctx:  ApplicationContext, user: discord.User = None):
    recache()
    if user == None: user = ctx.author
    localembed = discord.Embed(title=f"{user.display_name}'s isobot stats", color=color)
    localembed.set_thumbnail(url=user.avatar_url)
    localembed.add_field(name="Level", value=f"Level {levels[str(user.id)]['level']} ({levels[str(user.id)]['xp']} XP)", inline=False)
    localembed.add_field(name="Balance in Wallet", value=f"{currency['wallet'][str(user.id)]} coins", inline=True)
    localembed.add_field(name="Balance in Bank Account", value=f"{currency['bank'][str(user.id)]} coins", inline=True)
    localembed.add_field(name="Net-Worth", value=f"{get_user_networth(user.id)} coins", inline=True)
    # More stats will be added later
    # Maybe I should make a userdat system for collecting statistical data to process and display here, coming in a future update.
    await ctx.respond(embed=localembed)

# New Year's in-game Event Commands
special_event = client.create_group("event", "Commands related to the New Years special in-game event.")

@special_event.command(
    name="leaderboard", 
    description="View the global leaderboard for the special in-game event."
)
async def leaderboard(ctx: ApplicationContext):
    undicted_leaderboard = sorted(presents.items(), key=lambda x:x[1], reverse=True)
    dicted_leaderboard = dict(undicted_leaderboard)
    parsed_output = str()
    y = 1
    for i in dicted_leaderboard:
        if y < 10:
            try:
                if presents[i] != 0:
                    user_context = await client.fetch_user(i)
                    if not user_context.bot and presents[i] != 0:
                        print(i, presents[i])
                        if y == 1: yf = ":first_place:"
                        elif y == 2: yf = ":second_place:"
                        elif y == 3: yf = ":third_place:"
                        else: yf = f"#{y}"
                        parsed_output += f"{yf} **{user_context.name}:** {presents[i]} presents\n"
                        y += 1
            except discord.errors.NotFound: continue
    localembed = discord.Embed(title="New Years Special Event global leaderboard", description=parsed_output, color=color)
    await ctx.respond(embed=localembed)

@special_event.command(
    name="stats",
    description="See your current stats in the special in-game event."
)
@option(name="user", description="Who's event stats do you want to view?", type=discord.User, default=None)
async def stats(ctx: ApplicationContext, user: discord.User):
    if user == None: user = ctx.author
    localembed = discord.Embed(title=f"{user.display_name}'s New Years Special Event stats", description="Event ends on **1st January 2023**.", color=color)
    localembed.add_field(name=":gift: Presents", value=presents[str(user.id)], inline=True)
    await ctx.respond(embed=localembed)

# Initialization
active_cogs = ["economy", "maths", "moderation", "reddit", "minigames", "automod", "isobank", "levelling"]
i = 1
cog_errors = 0
for x in active_cogs:
    print(f"[main/Cogs] Loading isobot Cog ({i}/{len(active_cogs)})")
    i += 1
    try: client.load_extension(x)
    except Exception as e:
        cog_errors += 1 
        print(f"[main/Cogs] {colors.red}ERROR: Cog \"{x}\" failed to load: {e}{colors.end}")
if cog_errors == 0: print(f"[main/Cogs] {colors.green}All cogs successfully loaded.{colors.end}")
else: print(f"[main/Cogs] {colors.yellow}{cog_errors}/{len(active_cogs)} cogs failed to load.{colors.end}")
print("--------------------")
client.run(api.auth.get_token())




# btw i use arch
