#! /usr/bin/python
# vim: set fileencoding=utf-8:

import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
import pymysql.cursors
import json
import requests
import datetime

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))
ME = int(os.getenv('ME'))

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))
QUOTES = str(os.getenv('QUOTES_KEY'))
FOOD_KEY = str(os.getenv('FOOD_KEY'))

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

@tasks.loop(seconds=5.0)
async def looop():
    guild = bot.get_guild(GUILD) 
    if (guild):
        for ch in guild.channels:
            if ("технический" in ch.name):
                       
                url = 'https://quotes.rest/quote/random.json?maxlength=150'
                api_token = QUOTES
                headers = {'content-type': 'application/json',
                               'X-TheySaidSo-Api-Secret': format(api_token)}

                response = requests.get(url, headers=headers)
                response = response.json()['contents']['quotes'][0]

                quote = response['quote']
                author = response['author']
                text = quote + " — " + author
                await ch.send(text)

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
  brief='Убирает роль актёра, включает в труппу',
  pass_context=True
)
async def include(ctx, *, actor):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return
  
  actor_ids = str(actor).split()
  actor_ids = [int(i[3:-1]) for i in actor_ids]

  for mem in ctx.guild.members:
    if (mem.id in actor_ids):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(truppa)
      await mem.remove_roles(actor_zapasa)
      await ctx.send(f"{mem.name} благополучно включён в Драматическую Труппу")

def get_id(ref):
  return int(str(ref)[3:-1])

@bot.command(
  name='изтруппы',
  brief='Убирает роль Драм Труппы, возвращает в запас',
  pass_context=True
)
async def include(ctx, *, actor):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return


  actor_ids = str(actor).split()
  actor_ids = [int(i[3:-1]) for i in actor_ids]

  for mem in ctx.guild.members:
    if (mem.id in actor_ids):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(actor_zapasa)
      await mem.remove_roles(truppa)
      await ctx.send(f"{mem.name} благополучно исключён из Драматической Труппы")

@bot.command(
  name='распустить',
  brief='Распускает всю Драматическую Труппу разом',
  pass_context=True
)
async def include(ctx):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return

  truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
  actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')

  #for mem in ctx.guild.members:
  #  if (mem.)  

  for mem in truppa.members:
    await mem.add_roles(actor_zapasa)
    await mem.remove_roles(truppa)
    await ctx.send(f"{mem.name} благополучно исключён из Драматической Труппы")

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
  try:      
    db.close()
  except:
    print("Already closed")

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

  send_to = get_id(role)
  for r in ctx.guild.roles:
    if (r.id == send_to):
      for member in r.members:
        try:  
            await member.create_dm()
            await member.dm_channel.send("--------------------------------------------------------------------------\n*Сообщение от* **" + str(ctx.author.name) + "**!\n\n\t" + text + "\n\n[*Сообщения боту автоматически пересылаются Албанцу*]\n--------------------------------------------------------------------------")
        except Exception as e:
            print(e)

      return

@bot.command(
  name='список',
  brief='Список участников с данной ролью')
async def spisok(ctx, role):
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит'])):
    return
  send_to = get_id(role)
  ret = f"Список — {role}\n"
  for r in ctx.guild.roles:
    if (r.id == send_to):
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
  elif 'гулаг' not in message.channel.name:
    name = message.author.name
    iid = message.author.id
    time = message.created_at

    db, cursor = get_db_cursor()
    sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

    try:
      cursor.execute(sql)
      db.commit()
    except Exception as e:
      print(e)
      db.rollback()

    db.close()

  await bot.process_commands(message)

def get_guild():
  for guild in bot.guilds:
    print(guild.name)
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

# TODO uncomment to start the loop
#looop.start()

@bot.command(
  name='1',
  brief=''
)
async def nick1(ctx):
  if (not await check_rights(ctx, ['Krabick'])):
    return
  guild = bot.get_guild(GUILD) 
  await guild.get_member(277128557925367808).edit(nick="Чёрный Человек")
  response = "Дело сделано!"
  await ctx.send(response)

@bot.command(
  name='history',
)
async def print_history(ctx):

  db, cursor = get_db_cursor()

  guild = bot.get_guild(GUILD) 
  if (guild):
    total = len(guild.members)
    curr = 0
#    for mem in guild.members:

    cache = {} 
#    obj = load_obj("history")
#    print(obj)

    curr += 1
    lastMessage = None
    for ch in guild.channels:
      if (not str(ch.type) == 'text'):
        continue
      
      #fetchMessage = await ch.history(limit=10000).find(lambda m: m.author.id == mem.id)
      print("checking...")
      history = await ch.history(limit=10000).flatten()
      for m in history:
        if (m.author.id not in cache):
          cache[m.author.id] = m
        else:
          if (cache[m.author.id].created_at < m.created_at):
            cache[m.author.id] = m

    for mem in guild.members:
      if (mem.id in cache):
        content = cache[mem.id]
        try:
          await ctx.send(f"For user {mem.name} — last message is \t\t\t \"{content.content}\"")
          sql = f"""INSERT INTO activity(ID, name, timestamp)
                  VALUES(\"{mem.id}\", \"{mem.name}\", \"{content.created_at}\")
                """
          try:
            cursor.execute(sql)
            db.commit()
          except Exception as e:
            print(e)
            db.rollback()

        except Exception as e:
          #await ctx.send(f"For user {mem.name} — ERROR")
          print(f"For user {mem.name} — ERROR")
      else:
        #await ctx.send(f"For user {mem.name} — no message was found")
        print(f"For user {mem.name} — no message was found")

    try:      
      db.close()
    except:
      print("Already closed")
    print("Scanning is finished.")  

@bot.command(
  name='выпусти',
)
async def let_free(ctx):
  
  if not await check_rights(ctx, ['Политзаключённый']):
    return

  db, cursor = get_db_cursor()
  name = ctx.author.name
  
  guild = bot.get_guild(GUILD) 

  proletariat = discord.utils.get(guild.roles, name='Пролетарий')
  politzek= discord.utils.get(guild.roles, name='Политзаключённый')

  await ctx.author.add_roles(proletariat)
  await ctx.author.remove_roles(politzek)

  name = ctx.author.name
  iid = ctx.author.id
  time = ctx.message.created_at

  db, cursor = get_db_cursor()
  sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

  try:
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()

  db.close()

@tasks.loop(seconds=86400.0)
async def scan():

  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD) 
  day = int(datetime.datetime.now().day)

  if (guild and day % 3 == 0):

    super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит', 'NPC can\'t meme']

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Политзаключённый')

    for m in proletariat.members:
      done = False
      for role in list(map(str, m.roles)):
        if (role in super_roles):
         print(f"{m.name}")
         done = True
         break
      if (done):
        continue

      iid = m.id
      sql = f"SELECT * from cache WHERE `ID` = \"{iid}\""
      try:
        cursor.execute(sql)
        res = cursor.fetchone()
      
        if (res is None):

          await m.add_roles(politzek)
          await m.remove_roles(proletariat)
          
          for ch in guild.channels:
            if ("гулаг" in ch.name):
              res = f"Заключённый <@!{m.id}>! Вы были неактивны более 3-х дней! «!выпусти» чтобы выйти из гулага"
              await ch.send(res)


      except Exception as e:
        print(e)

    sql = f"DELETE FROM cache"

    try:
      cursor.execute(sql)
      db.commit()
    
  #    if (res is None):
  #
  #      await m.add_roles(politzek)
  #      await m.remove_roles(proletariat)

    except Exception as e:
      db.rollback()
      print(e)

    try:      
      db.close()
    except:
      print("Already closed")

def linkFetch():
    key = FOOD_KEY
    url = f"https://api.unsplash.com/photos/random/?query=meal&client_id={key}"

    response = requests.get(url)
    data = response.json()["urls"]["raw"]
    return data

@tasks.loop(seconds=3600.0)
async def breakfast():

  guild = bot.get_guild(GUILD) 
  
  hour = int(datetime.datetime.now().hour)
  if (guild and hour == 5):

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Политзаключённый')

    for ch in guild.channels:
      if ("гулаг" in ch.name):
        url = linkFetch()
        res = f"{politzek.mention}! Завтрак! \n\n {url}"
        res = f"Завтрак! \n\n {url}"
        await ch.send(res)

@tasks.loop(seconds=3600.0)
async def dinner():

  guild = bot.get_guild(GUILD) 
  
  hour = int(datetime.datetime.now().hour)
  
  if (guild and hour == 15):

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Политзаключённый')

    for ch in guild.channels:
      if ("гулаг" in ch.name):
        url = linkFetch()
        res = f"{politzek.mention}! Ужин! \n\n {url}"
        res = f"Ужин! \n\n {url}"
        await ch.send(res)

@tasks.loop(seconds=3600.0)
async def lunch():

  guild = bot.get_guild(GUILD) 
  
  hour = int(datetime.datetime.now().hour)
  if (guild and hour == 10):

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Политзаключённый')

    for ch in guild.channels:
      if ("технический" in ch.name):
        url = linkFetch()
        res = f"{politzek.mention}! Обед! \n\n {url}"
        res = f"Обед! \n\n {url}"
        await ch.send(res)

scan.start()
#looop.start()
dinner.start()
lunch.start()
breakfast.start()

bot.run(TOKEN)

