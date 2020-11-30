#! /usr/bin/python
# vim: set fileencoding=utf-8:

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ME = int(os.getenv('ME'))

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='пьеса')
async def play(ctx):
  response = "Тестовая пьеса"
  await ctx.send(response)

@bot.command(name='рассылка')
async def mems(ctx):
  send_to = ["Актёр Запаса"]
  for r in ctx.guild.roles:
    if (str(r) in send_to):
      for member in r.members:
        await member.create_dm()
        await member.dm_channel.send("Здоровеньки булы! Тестирую бота для спама. По идее он должен пересылать мне все ваши сообщения, можно проверить.")
      return

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  me = bot.get_user(ME)
  if not message.guild:
    await me.send(message.author.name + ": " + message.content)
  await bot.process_commands(message)

bot.run(TOKEN)

# test comment

