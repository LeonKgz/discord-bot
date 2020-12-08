#! /usr/bin/python
# vim: set fileencoding=utf-8:

import os
import discord
from discord.ext import commands
import pymysql.cursors

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD = str(os.getenv('DISCORD_GUILD'))
ME = int(os.getenv('ME'))

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))

connection = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             db=DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

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
  if not ctx.author == bot.get_user(ME):
    return
  send_to = ["Копия №7"]
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
    await me.send("**" + message.author.name + "**: " + message.content)
  await bot.process_commands(message)

def get_guild():
  for guild in bot.guilds:
    if (guild.name == GUILD):
      return guild

bot.run(TOKEN)

# test comment

