#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import discord
from discord.ext import commands, tasks
from voice import Voice
from utils import load_pickle, respond, save_pickle, status_update
from env import *

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')
  await status_update(bot)
  pass

@bot.command(name="write")
async def mina(ctx, key, value):
  dict = {}
  dict[key] = value
  save_pickle(dict, "testpickle")
  await respond(ctx, "written to pickle!")

@bot.command(name="read")
async def mina(ctx, key):
  dict = load_pickle("testpickle")
  if key not in dict:
    await respond(ctx, "empty!")
    return
  await respond(ctx, f"value of {key} is {dict[key]}")

@tasks.loop(seconds=21600.0)
async def status_update_loop():
  await status_update(bot)

bot.add_cog(Voice(bot))
status_update_loop.start()
bot.run(MANASCHI_TOKEN)
