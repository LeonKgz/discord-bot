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

@bot.command(
  name='пьеса',
  brief='Cообщает следующую пьесу',
  help='Cообщает следующую пьесу'
)
async def play(ctx):
  response = "Тестовая пьеса"
  await ctx.send(response)

@bot.command(
  name='посадить',
  brief='отправить пролетария в гулаг',
  help='Убирает роль Пролетария и даёт роль Политзаключённого. Пользоваться командой могут Политбюро и ВЧК. '
)
async def jail(ctx, poor_guy):
  if not check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК']):
    return
  for mem in ctx.guild.members:
    if (mem.name == poor_guy):
      proletariat = discord.utils.get(ctx.guild.roles, name='Пролетарий')
      politzek = discord.utils.get(ctx.guild.roles, name='Политзаключённый')
      await mem.add_roles(politzek)
      await mem.remove_roles(proletariat)

@bot.command(
  name='выпустить',
  brief='выпустить политзэка из гулага',
  help='Убирает роль Политзаключённого и даёт роль Пролетария. Пользоваться командой могут Политбюро и ВЧК.'
)
async def free(ctx, lucky_guy):
  if not check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК']):
    return
  for mem in ctx.guild.members:
    if (mem.name == lucky_guy):
      proletariat = discord.utils.get(ctx.guild.roles, name='Пролетарий')
      politzek = discord.utils.get(ctx.guild.roles, name='Политзаключённый')
      await mem.add_roles(proletariat)
      await mem.remove_roles(politzek)

@bot.command(
  name='рассылка',
  brief='Рассылка в лс по роли',
  help='Делает рассылку сообщения в лс всем участникам сервера с данной ролью. Так же указывает кто сделал рассылку. Пользоваться командой могут Политбюро, ВЧК, СовНарМод и Главлит. \nПример: !рассылка \"Актёр Запаса\" \"Пьеса завтра в 8 вечера!\"')
async def mems(ctx, role, text):
  # Old way of adressing the issue, now multiple roles can use the command (in check_rights)
  #if not ctx.author == bot.get_user(ME):
  #  return
  if (not check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return

  send_to = [role]
  for r in ctx.guild.roles:
    if (str(r) in send_to):
      for member in r.members:
        await member.create_dm()
        await member.dm_channel.send("--------------------------------------------------------------------------\n*Сообщение от* **" + str(ctx.author.name) + "**!\n\n\t" + text + "\n\n[*Сообщения боту автоматически пересылаются Албанцу*]\n--------------------------------------------------------------------------")
      return

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  me = bot.get_user(ME)
  if not message.guild:
    await me.send("---------------------------------------\n *Сообщение от* **" + message.author.name + "**:\n\n\t\t" + message.content + "\n\n---------------------------------------")
  await bot.process_commands(message)

def get_guild():
  for guild in bot.guilds:
    if (guild.name == GUILD):
      return guild

def check_rights(ctx, acceptable_roles):
  #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит']
  super_roles = acceptable_roles 
  for role in list(map(str, ctx.author.roles)):
    if (role in super_roles):
      return True
  return False


bot.run(TOKEN)

# test comment

