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
from discord.ext.commands import Bot
#from discord.ext import timers
from discord import FFmpegPCMAudio

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

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")
#bot.timer_manager = timers.TimerManager(bot)

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

#@bot.command(
#  name='пьеса',
#  brief='Cообщает следующую пьесу'
#)
#async def play(ctx):
#  response = "Ромео и Джульетта — Уильям Шекспир"
#  await ctx.send(response)

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
  if(str(ref)[2] == '!'): 
    a = int(str(ref)[3:-1])
  else:
    a = int(str(ref)[2:-1])

  return a

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

#from datetime import timedelta
#
#@bot.command(name="remind")
#async def remind(ctx, seconds):
#    
#    date = datetime.datetime.now() + timedelta(seconds=int(seconds))
#    time = "21/08/15"
#    date = datetime.datetime(*map(int, time.split("/")))
#    
#    res = await bot.timer_manager.create_timer("reminder", date, args=(ctx.channel.id, ctx.author.id))
#    print(str(res))
#    print("created " + str(date))
#    # or without the manager
#    timers.Timer(bot, "reminder", date, args=(ctx.channel.id, ctx.author.id)).start()
#
#@bot.event
#async def on_reminder(channel_id, author_id):
#    print("got")
#    channel = bot.get_channel(channel_id)
#
#    await channel.send("Hey, <@{0}>, remember to:".format(author_id))

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

      status = None

      statuses = ["zamechanie", "vigovor", "zakluchenie"] 
      lengths = {"zamechanie": 10, "vigovor": 60, "zakluchenie": 1440}
      lengths = {"zamechanie": 1, "vigovor": 2, "zakluchenie": 3}

      mem_id = mem.id
      sql = f"SELECT * from prisoners WHERE ID={mem_id};"

      try:
        cursor.execute(sql)
        res = cursor.fetchone()['Status']
        newidx = statuses.index(res) + 1
        if (newidx == len(statuses)):
          newidx = 0
        status = statuses[newidx]
        
      except Exception as e:
        status = statuses[0]
      
      length = lengths[status]

      guild = bot.get_guild(GUILD) 
      for ch in guild.channels:
        if ("технический" in ch.name):
          res = f".remind here {length}m free {mem_id}"
          await ch.send(res)

      sql = f"REPLACE INTO prisoners(ID, Protocol, Status) VALUES(\"{mem.id}\", \"{protocol}\", \"{status}\")"
      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
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

  if message.author == bot.user and "!кто" not in str(message.content):
    return
  me = bot.get_user(ME)
  if not message.guild:
    await me.send("---------------------------------------\n *Сообщение от* **" + message.author.name + "**:\n\n\t\t" + message.content + "\n\n---------------------------------------")
  elif 'погран' not in message.channel.name:
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
  elif 'технический' in message.channel.name and message.author.id == 116275390695079945:
    msg = message.content
    mss = msg.split()
    if (mss[0] == "free"):
      lucky_id = message.author.id
      for mem in ctx.guild.members:
        if (mem.id == lucky_id):
          proletariat = discord.utils.get(ctx.guild.roles, name='Пролетарий')
          politzek = discord.utils.get(ctx.guild.roles, name='Политзаключённый')
          await mem.add_roles(proletariat)
          await mem.remove_roles(politzek)
      await channel.send("The guy is free!") 

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
  name='пропуск',
)
async def let_free(ctx):
  
  if not await check_rights(ctx, ['Апатрид']):
    return

  db, cursor = get_db_cursor()
  name = ctx.author.name
  
  guild = bot.get_guild(GUILD) 

  proletariat = discord.utils.get(guild.roles, name='Пролетарий')
  politzek= discord.utils.get(guild.roles, name='Апатрид')


  name = ctx.author.name
  iid = ctx.author.id
  time = ctx.message.created_at

  db, cursor = get_db_cursor()

  sql = f"SELECT * from confessions WHERE `ID` = \"{iid}\""
  try:
    cursor.execute(sql)
    res = cursor.fetchone()
    
    if (res is None):

      res = f"Гражданин <@!{iid}>! \n\nМы не можем установить вашу личность! Вам нужно зарекомендовать себя! \n\n\t\tЭто можно сделать с помощью команды **« !рассказать »**\n\n\t\t **Например:** !рассказать \"Привет, я Хитари, ну или просто Сергей. Мне 27, живу в городе Санкт-Петербург, люблю японские компьютерные игры, читать мангу и так, по мелочи...\"\n\n\t Не забудьте про **кавычки**! Боту можно написать и в личку. Соответственно рекомендации пользователя можно узнать с помощью команды **« !кто »**, например: !кто @Albanec69 . Учтите, что **записи о себе можно править только один раз в 7 дней!**"
      await ctx.send(res)
      return  

    else:

      res = f"Гражданин <@!{iid}>, проходите!"
      await ctx.send(res)
      await ctx.author.add_roles(proletariat)
      await ctx.author.remove_roles(politzek)

  except Exception as e:
    mistake = str(e)
    res = f"Гражданин <@!{iid}>, произошла ошибка!\n\n\t*{e}*"
    await ctx.send(res)

  sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

  try:
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()

  db.close()

@bot.command(name='19273468236482734627846798326486')
async def vse(ctx):
  guild = bot.get_guild(GUILD) 
  db, cursor = get_db_cursor()
  proletariat = discord.utils.get(guild.roles, name='Пролетарий')
  politzek= discord.utils.get(guild.roles, name='Апатрид')
  npc = discord.utils.get(guild.roles, name='NPC can\'t meme')
  #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит', 'NPC can\'t meme']
  ms = []
  for m in proletariat.members:
    
    if (npc in m.roles):
      continue

    iid = m.id
    sql = f"SELECT * from confessions WHERE `ID` = \"{iid}\""
    try:
     cursor.execute(sql)
     res = cursor.fetchone()
    
     if (res is None):
       ms.append(m)
       await m.add_roles(politzek)
       await m.remove_roles(proletariat)       

    except Exception as e:
      print(e)

  for ch in guild.channels:
    if ("погранnnn" in ch.name):
      mentions = ""
      for m in ms:
        mentions += f"<@!{m.id}> "
      
      res = f"Граждане {mentions}! \n\nМы не можем установить вашу личность! Вам нужно зарекомендовать себя! \n\n\t\tЭто можно сделать с помощью команды **« !рассказать »**\n\n\t\t Например: !рассказать \"Привет, я Албанец. Мне 22 года, по образованию программист. Устраиваю читки пьес в дискорде, пытаюсь собрать народ на групповые чтения поэзии и просмотры японских мультиков. В свободное время люблю почитать что-то по философии или религии. Могу сыграть на гитаре твой реквест. В видео-игры не играю. Играю в Го. Энтузиаст Высокой Мошны.\"\n\n\t Не забудьте про **кавычки**! Боту можно написать и в личку. Соответственно рекомендации пользователя можно узнать с помощью команды **« !кто »**, например: !кто @Albanec69 . Учтите, что **записи о себе можно править только один раз в 7 дней!**"
      await ch.send(res)
      break

@tasks.loop(seconds=86400.0)
async def scan():

  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD) 
  day = int(datetime.datetime.now().day)

  if (guild and day % 3 == 0):

    super_roles = ['Политбюро ЦКТМГ', 'NPC can\'t meme']

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Апатрид')
    ms = []
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
          ms.append(m)
          await m.add_roles(politzek)
          await m.remove_roles(proletariat)

      except Exception as e:
        print(e)

    for ch in guild.channels:
      if ("погран" in ch.name):
        mentions = ""
        for m in ms:
          mentions += f"<@!{m.id}> "
        
        res = f"Граждане {mentions}! \n\nВы были неактивны более 3-х дней и нам нужно убедиться, что вы ещё живы! « **!пропуск** » чтобы пересечь границу Мошны!"
        await ch.send(res)
        break

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
      if ("колхоз" in ch.name):
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
      if ("колхоз" in ch.name):
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
      if ("колхоз" in ch.name):
        url = linkFetch()
        res = f"{politzek.mention}! Обед! \n\n {url}"
        res = f"Обед! \n\n {url}"
        await ch.send(res)

import random

@tasks.loop(seconds=3600.0)
async def important_info():

  guild = bot.get_guild(GUILD) 
  
  hour = int(datetime.datetime.now().hour)

  if (guild and hour == 9):

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    npc = discord.utils.get(guild.roles, name='NPC can\'t meme')

    ps = proletariat.members 
    ns = npc.members
    ps = [p for p in ps if p not in ns]

    m = ps[random.randint(0, len(ps) - 1)]

    for ch in guild.channels:
      if ("колхоз" in ch.name or "погран" in ch.name):

        db, cursor = get_db_cursor()

        select = f"SELECT * from confessions WHERE ID={m.id};"

        try:
          cursor.execute(select)
          confession = cursor.fetchone()['Confession']
          res = f"Товарищи! А знали ли вы что-нибудь о {m.name}? Вот что {m.name} говорит о себе: \n\n\t*{confession}*\n\nНе забывайте, что можно обновить своё описание (« **!рассказать** ») как минимум раз в 7 дней."
          await ch.send(res)
           
        except Exception as e:
          print(e)
          db.rollback()
          
        db.close()


#looop.start()
scan.start()
#dinner.start()
#lunch.start()
important_info.start()
#breakfast.start()

@bot.command(name='on')
async def play(ctx, number):
    channel = ctx.message.author.voice.channel
    player = await channel.connect()
    number = int(number)
    if (number == 0):
      # Музыка
      player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/music128'))
    elif number == 1:  
      # Старое радио
      player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/ices128'))
    elif number == 2:  
      # Детское радио
      player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/detskoe128'))

@bot.command(name='onn')
async def kaligula(ctx, url: str = 'http://stream.radioparadise.com/rock-128'):
    channel = ctx.message.author.voice.channel
    player = await channel.connect()
    player.play(FFmpegPCMAudio('/files/kaligula.mp3'))

@bot.command(name='off', pass_context = True)
async def leavevoice(ctx):
    for x in bot.voice_clients:
        if(x.guild == ctx.message.guild):
            return await x.disconnect()

    return await ctx.send("I am not connected to any voice channel on this server!")

@bot.command(name="кто")
async def confess(ctx, mem):
 
    id_author = ctx.author.id
    id_to_search = get_id(mem)
    mem = bot.get_user(id_to_search)
    
    #if (mem is None):
    #  await ctx.send(f"<@!{id_author}>, к сожалению эта команда не работает в мобильном приложении. \nВсе вопросы к дикорду!")
    #  return

    db, cursor = get_db_cursor()

    select = f"SELECT * from confessions WHERE ID={id_to_search};"

    try:
      cursor.execute(select)
      confession = cursor.fetchone()['Confession']
      await ctx.send(f"<@!{id_author}>, вот что {mem.name} говорит о себе: \n\n\t*{confession}*")
      
    except Exception as e:
      print(e)
      db.rollback()
      await ctx.send(f"<@!{id_author}>, пока нам ничего не известно о {mem.name}.")
      
    db.close()

@bot.command(name='рассказать')
async def confess(ctx, confession):
  
    name = ctx.author.name
    iid = ctx.author.id
    confession = str(confession)

    check = confession.split()
    if len(check) == 1:
      await ctx.send(f"<@!{iid}> твоё описание либо **слишком короткое** либо ты забыл(а) **кавычки**!")
      return

    time = datetime.datetime.now()

    db, cursor = get_db_cursor()

    select = f"SELECT * from confessions WHERE ID={iid};"
    replace = f"REPLACE INTO confessions(ID, Name, Confession, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{confession}\", \"{time}\")"

    try:
      cursor.execute(select)
      timestamp = cursor.fetchone()['Timestamp']
      period = datetime.datetime.now() - timestamp
      days_passed = period.days
      if (days_passed < 7):
        diff = 7 - days_passed
        await ctx.send(f"<@!{iid}> своё описание можно обновлять только один раз в 7 дней! \n\n\t**Вы сможете обновить своё через {diff}**")
        return
      
      else:

        try:
          cursor.execute(replace)
          db.commit()
          await ctx.send(f"<@!{iid}> ваше описание обновлено!")
        except Exception as e:
          print(e)
          await ctx.send(f"<@!{iid}> c вашим описанием была проблема!")
          db.rollback()

    except Exception as e:
      print(e)
      print(f"No entry for {name}...\nInserting new entry...")
      
      try:
        cursor.execute(replace)
        db.commit()
        await ctx.send(f"<@!{iid}> ваше описание обновлено!")
      except Exception as e:
        print(e)
        db.rollback()
        await ctx.send(f"<@!{iid}> c вашим описанием была проблема!")
      
    db.close()

@bot.event 
async def on_member_join(member):
  guild = bot.get_guild(GUILD) 
  apatrid = discord.utils.get(guild.roles, name='Апатрид')
  await member.add_roles(apatrid)
  db, cursor = get_db_cursor()
  name = member.name
  for ch in guild.channels:
    if "manifesto" in ch.name:
      manifesto = ch

  for ch in guild.channels:
    if "погран" in ch.name:
      await ch.send(f"<@!{member.id}>, добро пожаловать в ТМГ!\n\nЭто пограничная застава, охраняющая суверенитет Мошны.\n В канале {manifesto.mention} ты найдёшь Трактат о Мошне — основополагающий документ сего сообщества.\nЧтобы получить доступ ко всем остальным каналам сервера и стать полноценным гражданином, достаточно ввести команду « !пропуск ». \n\nДа прибудет с тобой Мошна!")
    if "карандаш" in ch.name:
      await ch.send(f"<@!{member.id}> вступил в ТМГ!")

@bot.event 
async def on_member_remove(member):
  guild = bot.get_guild(GUILD) 

  for ch in guild.channels:
    if "карандаш" in ch.name:
      await ch.send(f"<@!{member.id}> **покинул** ТМГ!")

bot.run(TOKEN)

