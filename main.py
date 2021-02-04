#! /usr/bin/python
# vim: set fileencoding=utf-8:

import os
import discord
from discord.ext import commands
from discord.utils import get
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

def get_db_cursor():
  db = pymysql.connect(host=HOST,
                       user=USER,
                       password=PASSWORD,
                       db=DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
  return db, db.cursor()

# test commit

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")


@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

@bot.command(
  name='пьеса',
  brief='Cообщает следующую пьесу'
)
async def play(ctx):
  response = "Ромео и Джульетта — Уильям Шекспир"
  await ctx.send(response)

@bot.command(
  name='втруппу',
  brief='Убирает роль актёра, включает в труппу'
)
async def include(ctx, actor):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return
  
  actor_id = int(str(actor)[3:-1])
  name = ""

  for mem in ctx.guild.members:
    if (mem.id == actor_id):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(truppa)
      await mem.remove_roles(actor_zapasa)
  await ctx.send(f"{actor} благополучно включён в Драматическую Труппу")

def get_id(ref):
  return int(str(ref)[3:-1])

@bot.command(
  name='изтруппы',
  brief='Убирает роль Драм Труппы, возвращает в запас'
)
async def include(ctx, actor):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return

  actor_id = int(str(actor)[3:-1])
  name = ""

  for mem in ctx.guild.members:
    if (mem.id == actor_id):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(actor_zapasa)
      await mem.remove_roles(truppa)
  await ctx.send(f"{actor} благополучно исключён из Драматической Труппы")

@bot.command(
  name='посадить',
  brief='Отправить пролетария в гулаг, с протоколом',
  help='Убирает роль Пролетария и даёт роль Политзаключённого. Можно заполнить протокол, который сохраняется в базе данных. Задержанный может ознакомиться с протоколом после задержания. Пользоваться командой могут Политбюро и ВЧК. '
)
async def jail(ctx, poor_guy, protocol):
  if not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК']):
    return
  db, cursor = get_db_cursor()
  for mem in ctx.guild.members:
    if (mem.id == get_id(poor_guy)):
      proletariat = discord.utils.get(ctx.guild.roles, name='Пролетарий')
      politzek = discord.utils.get(ctx.guild.roles, name='Политзаключённый')
      await mem.add_roles(politzek)
      await mem.remove_roles(proletariat)

      sql = f"""INSERT INTO prisoners(ID, Protocol)
        VALUES(\"{mem.name}\", \"{protocol}\")
      """
      try:
        cursor.execute(sql)
        db.commit()
      except:
        db.rollback()
        db.close()
  db.close()

@bot.command(
  name='начальник',
)
async def nachalnik(ctx):
  if not await check_rights(ctx, ['Политзаключённый']):
    return

  db, cursor = get_db_cursor()
  name = ctx.author.name
  sql = f""" SELECT Protocol 
    FROM prisoners
    WHERE ID = \"{name}\"
  """ 
  res = f"Заключённый <@!{ctx.author.id}>! Ошибочка вышла!"
  try:
    cursor.execute(sql)
    res = cursor.fetchone()['Protocol']
    res =  f"Заключённый <@!{ctx.author.id}>!\nВаш протокол: *" + res + "*"
  except:
    db.rollback()
    db.close()
  await ctx.send(res)
  db.close()

@bot.command(
  name='протокол',
  rest_is_raw=False,
)
async def protocol(ctx, name):
  if not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК']):
    return
  nname = "" 
  for mem in ctx.guild.members:
    if (mem.id == get_id(name)):
      nname = mem.name

  db, cursor = get_db_cursor()
  sql = f""" SELECT Protocol 
    FROM prisoners
    WHERE ID = \"{nname}\"
  """ 
  res = f"Товарищ <@!{ctx.author.id}>! Ошибочка вышла!"
  try:
    cursor.execute(sql)
    res1 = cursor.fetchone()['Protocol']
    higher_rank_name = ctx.author.name
    res =  f"Товарищ <@!{ctx.author.id}>!\nПротокол заключённого {name}: *" + res1 + "*"
  except:
    db.rollback()
    db.close()
  await ctx.send(res)
  db.close()

@bot.command(
  name='выпустить',
  brief='Выпустить политзэка из гулага',
  help='Убирает роль Политзаключённого и даёт роль Пролетария. Пользоваться командой могут Политбюро и ВЧК.'
)
async def free(ctx, lucky_guy):
  if not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК']):
    return
  for mem in ctx.guild.members:
    if (mem.id == get_id(lucky_guy)):
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
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return

  send_to = [role]
  for r in ctx.guild.roles:
    if (str(r) in send_to):
      for member in r.members:
        await member.create_dm()
        await member.dm_channel.send("--------------------------------------------------------------------------\n*Сообщение от* **" + str(ctx.author.name) + "**!\n\n\t" + text + "\n\n[*Сообщения боту автоматически пересылаются Албанцу*]\n--------------------------------------------------------------------------")
      return

@bot.command(
  name='списки',
  brief='Список участников с данной ролью')
async def spisok(ctx, role):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return

  send_to = [role]
  ret = f"Список — \"{role}\"\n"
  for r in ctx.guild.roles:
    if (str(r) in send_to):
      for member in r.members:
        ret += "\t" + member.name + ";\n"
  await ctx.send(ret)      
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

async def check_rights(ctx, acceptable_roles):
  #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит']
  super_roles = acceptable_roles 
  for role in list(map(str, ctx.author.roles)):
    if (role in super_roles):
      return True
  response = "**" + str(ctx.author.name) + "**, ты кто " + str(get(bot.emojis, name='peepoClown'))
  await ctx.send(response) 
  return False

def convert_brief(message):
  # REPLACE BAD PRACTISE
  total = 61
  desired_indent = 5
  actual_indent = 0

#bot.remove_command("help")
#
#@bot.command(
#  name='help',
#  brief='Shows this message KKona',
#)
#async def help(ctx):
#  desc =  ""
#  for cmd in list(bot.commands):
#    desc += f'\t{cmd.name}\t\t\t{cmd.brief}\n' 
#  embed=discord.Embed(title="Как управляться с Манкуртом", description=desc, color=0x8c8c8c)
#  await ctx.channel.send(embed=embed)

bot.run(TOKEN)

# test comment

