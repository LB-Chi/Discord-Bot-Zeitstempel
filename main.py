import discord
import time
from discord.ext import commands
import logging

from discord.ext.commands import command
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

test_role = "test"

times = {}

@bot.event
async  def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

#Gib Zeitformat zurück
def fmt(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

#Gib gespeicherten Stempel Satus vom User aus times dictionary
def get_state(user_id: int):
    return times.get(user_id)

#überprüft welcher status grad ist und passt die Zeit an
def update_acc(state: dict):
    now = time.monotonic()
    a = now - state["late_ts"]
    if state["mode"] == "work":
        state["work_acc"] += a
    else:
        state["break_acc"] += a
    state["last_ts"] = now

#Command zum einstempeln
@bot.command()
async def ein(ctx):
    if get_state(ctx.author.id):
        await ctx.send(f"{ctx.author.mention} hat sich schon eingestempelt")
        return

    now = time.monotonic()
    times[ctx.author.id] = {
        "clock_in": now,
        "work_acc": 0.0,
        "break_acc": 0.0,
        "mode": "work",
        "last_ts": now
    }
    await ctx.send(f"{ctx.author.mention} eingestempelt")

#command zur Pause einstempeln
@bot.command()
async def pause(ctx):
    state =  get_state(ctx.author.id)
    if not state:
        await ctx.send(f"{ctx.author.mention} ist nicht eingestempelt")
        return
    if state["mode"] == "break":
        await ctx.send(f"{ctx.author.mention} ist schon in der Pause")
        return

    update_acc(state)
    state["mode"] = "break"
    await ctx.send(f"{ctx.author.mention} ist in der Pause")

""" #Sachen probiert
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word")

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name= test_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {test_role}")
    else:
        await ctx.send("Role doesn't exists!")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=test_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {test_role} removed")
    else:
        await ctx.send("Role doesn't exists!")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll (ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_mgs = await ctx.send(embed=embed)
    await poll_mgs.add_reaction("👍")
    await poll_mgs.add_reaction("👎")

@bot.command()
@commands.has_role(test_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Loser")
"""

bot.run(token, log_handler=handler, log_level=logging.DEBUG)