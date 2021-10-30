#! /usr/bin/python

# vim: set fileencoding=utf-8:

import asyncio
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
import pymysql.cursors
import json
import random
import re
import requests
import datetime
from discord.ext.commands import Bot
#from discord.ext import timers
from discord import FFmpegPCMAudio
# test comment


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

@tasks.loop(seconds=3600.0)
async def news_alert():
  guild = bot.get_guild(GUILD) 
  db, cursor = get_db_cursor()

  hour = int(datetime.datetime.now().hour)

  if (guild and hour == 16):

    counter = None

    try:
      sql = f"SELECT COUNT(*) FROM timers"
      cursor.execute(sql)
      counter = int(cursor.fetchone()['COUNT(*)'])
    except Exception as e:
      print(e)
      db.rollback()
      return

    if (counter == 0):
      return

    with open('counter.txt', 'r+') as f:
      current_offset = int(f.readlines()[0])
      
      f.seek(0)
      if (current_offset >= counter - 1):
        f.write("0")
      else:
        f.write(f"{current_offset + 1}")

      f.truncate()

      f.close()
    
    try:
      sql = f"SELECT * FROM timers ORDER By Name LIMIT 1 OFFSET {current_offset}"
      cursor.execute(sql)
      content = cursor.fetchone()['Content']
    except Exception as e:
      print(e)
      try:
        db.rollback()
      except Exception as e:
        print(re)
      return

    db.close()

    for ch in guild.channels:
      if ("колхоз" in ch.name or "погран-застава" in ch.name):
        await ch.send(content)

news_alert.start()

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

@bot.command(name="средство")
async def remedy(ctx, issue):

  url = f"http://albenz.xyz:8083/remedy?issue={issue}"

  response = requests.get(url)
  data = response.json()["files"]
  if not data:
    await ctx.send(f"<@!{ctx.author.id}>, средство для *«{issue}»* не найдено! « !средства », чтобы посмотреть все ключевые слова.")

  data = data[random.randint(0, len(data) - 1)]
  
  author = data["author"]
  title = data["title"]
  data = data["content"]

  data = data.split("\n\n")[1]
  #data = data.replace("\\n", "\n")
  data = data.replace("  ", " ")
  data = data.strip()
  
  await ctx.send(f"—\n\n*{title}. {author}.*\n\n\t{data}\n\n—")

@bot.command(name="средства")
async def remedies(ctx):
  url = f"http://albenz.xyz:8083/remedies"

  response = requests.get(url)
  data = response.json()["remedies"]

  if not data:
    await ctx.send(f"<@!{ctx.author.id}>, средства не найдены!")

  ret_str = ", ".join(data)
  await ctx.send(f"*<@!{ctx.author.id}>, вот список ключевых слов: \n\n\t{ret_str}.*")

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

  for mem in ctx.guild.embers:
    if (mem.id in actor_ids):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(truppa)
      await mem.remove_roles(actor_zapasa)
      await ctx.send(f"{mem.name} благополучно включён в Драматическую Труппу")

def get_id(ref):

  try:
    ret = int(ref)
    return ret
  except Exception as e:
    if(str(ref)[2] == '!' or str(ref)[2] == '&'): 
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
      words = {"zamechanie": "10 минут", "vigovor": "1 час", "zakluchenie": "сутки"}

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
        if ("гулаг" in ch.name):
          res = f"Заключённый <@!{mem_id}>! Ваше заключение составит {words[status]}. Узнать свой протокол можно с помощью команды « !начальник »"
          await ch.send(res)

      sql = f"REPLACE INTO prisoners(ID, Protocol, Status) VALUES(\"{mem.id}\", \"{protocol}\", \"{status}\")"
      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        db.rollback()
      db.close()

      await asyncio.sleep(length * 60)

      await ctx.send(f"Заключённый <@!{mem_id}> свободен!")
      await mem.add_roles(proletariat)
      await mem.remove_roles(politzek)

@bot.command(
  name='начальник',
)
async def nachalnik(ctx):
  if not await check_rights(ctx, ['Политзаключённый']):
    return

  db, cursor = get_db_cursor()
  name = ctx.author.id
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

  await ctx.send(res)
  db.close()

def is_me(m):
  return True 

@bot.command(name="clear")
async def clear(ctx, num):
  if not await check_rights(ctx, ['Политбюро ЦКТМГ']):
    return
  num = int(num) + 1
  await ctx.channel.purge(limit=num, check=is_me)

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
    WHERE ID = \"{get_id(name)}\"
  """ 
  res = f"Товарищ <@!{ctx.author.id}>! Ошибочка вышла!"
  try:
    cursor.execute(sql)
    res1 = cursor.fetchone()['Protocol']
    higher_rank_name = ctx.author.name
    res =  f"Товарищ <@!{ctx.author.id}>!\nПротокол заключённого {name}: *" + res1 + "*"
  except:
    db.rollback()
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
  #if message.author == bot.user and "!кто" not in str(message.content):
    return

  me = bot.get_user(ME)

  # For now if the bot is on some other server, do nothing!
  if (message.guild):
    if (message.guild.name != "ТМГ"):
      return

  #if not message.guild and message.content[0] != "!" and int(message.author.id) != ME :
  if not message.guild:
    
    #print(message.author.mutual_guilds[0].get_member(message.author.id).id)

    # if int(message.author.id) != ME:
    if int(message.author.id) != ME and not "!донести" in message.content:
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

  try:
    res_roles = ctx.author.roles
  except Exception as e:
    res_roles = bot.get_user(ctx.author.id).roles

  for role in list(map(str, res_roles)):
    if (role in super_roles):
      return True
  response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(get(bot.emojis, name='peepoClown'))
  await ctx.send(response)
  return False

async def check_rights_dm(ctx):
  super_roles = [214320783357378560, 696405991876722718, ***REMOVED***, 498264068415553537]
  if ctx.author.id in super_roles:
      return True
  response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(get(bot.emojis, name='peepoClown'))
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

# @bot.command(
#   name='1',
#   brief=''
# )
# async def nick1(ctx):
#   if (not await check_rights(ctx, ['Krabick'])):
#     return
#   guild = bot.get_guild(GUILD)
#   await guild.get_member(names["frolov"]).edit(nick="Калигула")

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

      res = f"Гражданин <@!{iid}>! \n\nМы не можем установить вашу личность! Вам нужно зарекомендовать себя! \n\n\t\tЭто можно сделать с помощью команды **« !рассказать »**\n\n\t\t **Например:** !рассказать \"Привет, я Хитари, ну или просто Сергей. Мне 27, живу в городе Санкт-Петербург, люблю японские компьютерные игры, читать мангу и так, по мелочи...\"\n\n\t Не забудьте про **кавычки**! Боту можно написать и в личку. Соответственно рекомендации пользователя можно узнать с помощью команды **« !кто »**, например: !кто <@!***REMOVED***> . Учтите, что **записи о себе можно править только один раз в 7 дней!**"
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
  day = int(datetime.datetime.today().weekday())

  if (guild):
    super_roles = ['Политбюро ЦКТМГ', 'NPC can\'t meme']


    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Апатрид')
    sovnarmod = discord.utils.get(guild.roles, name='СовНарМод')

    # Scan through all the unmarked descriptions and remind SovNarMod members to mark them immediately
    snm_dict = {}
    for m in sovnarmod.members:
      snm_dict[str(m.id)] = []
    
    select = "SELECT * FROM unmarked_confessions"
    try:
      cursor.execute(select)
      entries = cursor.fetchall()
      for e in entries:
        to_remind = [i.strip() for i in e["Markers"].split(",")]
        for i in to_remind:
          snm_dict[i].append(e["ID"])

    except Exception as e:
      print(e)
      db.rollback()
   
    for sovok, spiski in snm_dict.items():
      sovok = bot.get_user(int(sovok))
      await sovok.create_dm()
      quotes = ",\n\t".join([(str(j) + ") \t" + str(i)) for j, i in enumerate(spiski)])
      if(len(spiski) > 0):
        await sovok.dm_channel.send(f"Товарищ Народный Модератор! Вот ваша квота **описаний** за прошедшие сутки: \n\n\t{quotes}")

  if (guild and day == 0):

    super_roles = ['Политбюро ЦКТМГ', 'NPC can\'t meme']

    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Апатрид')
    sovnarmod = discord.utils.get(guild.roles, name='СовНарМод')

    # Scan through all the Proletariat and put to Pogran-Zastava channel all who are not in the «cache» database
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
        
        res = f"Граждане {mentions}! \n\nВы были неактивны более 7 дней и нам нужно убедиться, что вы ещё живы! « **!пропуск** » чтобы пересечь границу Мошны!"
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

    bl = [351749038497988621, 249503118885257216, 486137719647633408, 376990474466099201, 355781240479023115, 347757889210810369]

    ps = [item for item in ps if item.id not in bl]      
    m = ps[random.randint(0, len(ps) - 1)]

    for ch in guild.channels:
      if ("колхоз" in ch.name or "погран" in ch.name):

        db, cursor = get_db_cursor()

        select = f"SELECT * from confessions WHERE ID={m.id};"

        try:
          cursor.execute(select)
          confession = cursor.fetchone()['Confession']
          res = f"Товарищи! А знали ли вы что-нибудь о {m.name}? Вот что {m.name} говорит о себе: \n\n\t*{confession}*\n\nНе забывайте, что можно обновить своё описание (« **!рассказать** ») максимум один раз в 7 дней."
          await ch.send(res)
           
        except Exception as e:
          print(e)
          db.rollback()
          
        db.close()

@tasks.loop(seconds=30000000.0)
async def start_records():
    try:
      guild = bot.get_guild(GUILD) 
      proletariat = discord.utils.get(guild.roles, name='Пролетарий')
      politzek= discord.utils.get(guild.roles, name='Апатрид')
      print(guild.members)

      db, cursor = get_db_cursor()
      points = 0
      
      for m in guild.members:
        name = m.name
        id_to_search = m.id

        replace = f"REPLACE INTO rating(ID, Name, Points) VALUES(\"{id_to_search}\", \"{name}\", \"{points}\")"

        try:
          cursor.execute(replace)
          db.commit()
          
        except Exception as e:
          print(e)
          db.rollback()
      db.close()
      exit(0)

    except Exception as e:
      print("oof")

#start_records.start()
 

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

# @bot.command(name='31')
# async def kaligula1(ctx):
#     channel = ctx.message.author.voice.channel
#     player = await channel.connect()
#
#     for x in bot.voice_clients:
#
#        if (x.is_connected()):
#            x.stop()
#            while (True):
#                x.play(FFmpegPCMAudio('files/gong.mp3'))
#        else:
#
#            channel = ctx.message.author.voice.channel
#            player = await channel.connect()
#            while (True):
#                player.play(FFmpegPCMAudio('files/gong.mp3'))

@bot.command(name='off', pass_context = True)
async def leavevoice(ctx):
    for x in bot.voice_clients:
        if(x.guild == ctx.message.guild):
            return await x.disconnect()

    return await ctx.send("I am not connected to any voice channel on this server!")

def get_db_row(db_name, id_to_search):

    db, cursor = get_db_cursor()

    select = f"SELECT * from {db_name} WHERE ID={id_to_search};"

    try:
      cursor.execute(select)
      row = cursor.fetchone()
      return row
      
    except Exception as e:
      print(e)
      db.rollback()
      db.close()
      return False

import json
import numpy as np

@bot.command(name="оценить")
async def evaluate(ctx, mem, points):

    if (not await check_rights_dm(ctx)):
      return
 
    id_author = ctx.author.id
    id_to_search = get_id(mem)
    mem = bot.get_user(id_to_search)
    points = int(points)
    guild = bot.get_guild(GUILD)
    
    if (points < 0 or points > 10):
      await ctx.send(f"<@!{id_author}>, количество очков должно быть между 0 и 10")
      return
    
    row = get_db_row("confessions", id_to_search)

    if (row):
      if (row["Points"] is None):
        data = {
          int(id_author): points          
        }
        
      else:
        data = json.loads(row["Points"])
      
      if (len(data) == 0):
        prev_mean = 0
      else:
        prev_mean = np.mean(list(data.values()))
      data[f"{id_author}"] = points
      curr_mean = np.mean(list(data.values()))

      status1 = await remove_points_quick(id_to_search, prev_mean)
      status2 = await add_points_quick(id_to_search, curr_mean)

      if (not(status1 and status2)):
        await ctx.send(f"<@!{id_author}>, произошла ошибка корректировки социального рейтинга!")
        return
      
      data = json.dumps(data)
      data = data.replace("\"", "\\\"")

    else:
      await ctx.send(f"<@!{id_author}>, оценивать нечего!")
      return

    db, cursor = get_db_cursor()
    #name = row["Name"]
    #confession = row["Confession"]
    #confession = confession.replace("\"", "\\\"")
    #confession = confession.replace("\'", "\\\'")
    #time = row["Timestamp"]

    #replace = f"REPLACE INTO confessions(ID, Name, Confession, Timestamp, Points) VALUES(\"{id_to_search}\", \"{name}\", \"{confession}\", \"{time}\", \"{data}\")"
    update = f"UPDATE confessions SET Points = \"{data}\" WHERE ID =\"{id_to_search}\""

    try:
      cursor.execute(update)
      db.commit()
      
    except Exception as e:
      await ctx.send(f"<@!{id_author}>, проблема с описанием!")
      print(e)
      db.rollback()
      return

    await ctx.send(f"<@!{id_author}>, оценка обновлена!")
    
    # Now update unmarked_confessions
    mods = get_db_row("unmarked_confessions", id_to_search)
    if (mods != None):
      mods = mods["Markers"].split(", ")
    else:
      mods = []

    try:
      mods.remove(str(id_author))
    except Exception as e:
      print(e)

    # If all the mods have marked this user, remove from unmarked_confessions table
    if (len(mods) == 0):
      sql = f"DELETE FROM unmarked_confessions WHERE ID=\"{id_to_search}\""
      for ch in guild.channels:
        if ("гласность" in ch.name):
          await ch.send(f"Все Модераторы оценили описание гражданина <@!{mem.id}>!\n\n\t\t Окончательная оценка — **{int(curr_mean)}**\n\n----------------------------------------------------------------------")

    
    else:  
      mods = ", ".join([str(m) for m in mods])
      sql = f"UPDATE unmarked_confessions SET Markers = \"{mods}\" WHERE ID=\"{id_to_search}\""

    try:
      cursor.execute(sql)
      db.commit()
    except Exception as e:
      print(e)
      await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка: {str(e)}")
      db.rollback()

    db.close()

async def remove_points_quick(target_id, points):

  try:
      points = int(points)

      db, cursor = get_db_cursor()
      row = get_db_row("raiting", target_id)
      if (not row):
        #return False
        curr = 0
      else:
        curr = row["Points"]

      end = curr - points
      if (end < 0):
        end = 0

      db, cursor = get_db_cursor()
      sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target_id}\""

      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return False

      db.close()
  
  except Exception as e:
    print(e)
    return False

  return True

async def add_points_quick(target_id, points):

  try:
      points = int(points)

      db, cursor = get_db_cursor()
      row = get_db_row("raiting", target_id)

      if (not row):
        #return False
        curr = 0
      else:
        curr = row["Points"]

      end = curr + points

      if (end < 0):
        end = 0

      db, cursor = get_db_cursor()
      sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target_id}\""

      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return False

      db.close()
  
  except Exception as e:
    print(e)
    return False

  return True

@bot.command(name="remove")
async def remove_points(ctx, target_id, points):
  if (not await check_rights_dm(ctx)):
    return

  if (ctx.guild):
      msg_id = ctx.message.id
      await ctx.message.delete()
      # await ctx.send(f"<@!{ctx.message.author.id}>, ваше сообщение было удалено!")
  else:
      try:
          try:
              points = int(points)
          except Exception as e:
              await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
              return

          if (points < 1 or points > 15):
              await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
              return

          db, cursor = get_db_cursor()
          row = get_db_row("raiting", target_id)
          if (not row):
            await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка соединения! Попробуйте ещё раз.")

          curr = row["Points"]
          end = curr - points
          if (end < 0):
            end = 0

          db, cursor = get_db_cursor()
          sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target_id}\""

          try:
            cursor.execute(sql)
            db.commit()
          except Exception as e:
            print(e)
            await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка: {str(e)}")

            db.rollback()

          db.close()
          await ctx.send(f"<@!{ctx.message.author.id}>, очки успешно сняты ! Текущий рейтинг - {end}")

      except Exception as e:
        print(e)
        await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка: {str(e)}")

@bot.command(name="add")
async def add_points(ctx, target_id, points):
  if (not await check_rights_dm(ctx)):
    return

  if (ctx.guild):
      msg_id = ctx.message.id
      await ctx.message.delete()
      # await ctx.send(f"<@!{ctx.message.author.id}>, ваше сообщение было удалено!")
  else:

      try:
        points = int(points)
      except Exception as e:
          await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
          return

      if (points < 1 or points > 15):
          await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
          return

      db, cursor = get_db_cursor()
      row = get_db_row("raiting", target_id)
      if (not row):
        await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка соединения! Попробуйте ещё раз.")

      curr = row["Points"]
      end = curr + points

      db, cursor = get_db_cursor()

      sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target_id}\""

      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка: {str(e)}")

        db.rollback()

      db.close()
      await ctx.send(f"<@!{ctx.message.author.id}>, очки успешно добавлены! Текущий рейтинг - {end}")

#db, cursor = get_db_cursor()
#
#select = f"SELECT * from confessions"
#markers = "***REMOVED***, 696405991876722718, 214320783357378560"
#try:
#  cursor.execute(select)
#  confession = cursor.fetchall()
#  for i, c in enumerate(confession):
#    iid = c["ID"]
#    name = c["Name"]
#    replace = f"REPLACE INTO unmarked_confessions(ID, Name, Markers) VALUES(\"{iid}\", \"{name}\",\"{markers}\")"
#    cursor.execute(replace)
#    db.commit()
#    print(f"{i}) Done for {iid}")
#  
#except Exception as e:
#  print(e)
#  db.rollback()
#  
#db.close()
#
#exit(1)

@bot.command(name="донести")
async def donos(ctx, *, args=None):
    
    # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
    if (ctx.guild):
      await ctx.message.delete()
      return

    source_id = ctx.author.id
    user = bot.get_user(source_id)
    db, cursor = get_db_cursor()
    guild = bot.get_guild(GUILD)

    blacklist_row = get_db_row("tellings_blacklist", source_id)

    if blacklist_row:
      unban_time = blacklist_row["Timestamp"]
      now = datetime.datetime.now()
      if now < unban_time:
        period = unban_time - now
        await user.create_dm()
        await user.dm_channel.send(f"Вы получили бан на функцию доноса! Бан продлится ещё {period.days} дней.")
        return


    # Check that user has a description
    cnfs = get_db_row("confessions", source_id)
    if not cnfs:
      await ctx.send(f"<@!{source_id}>, для использования данной функции нужно иметь описание на сервере!")
      return

    # Check that user has at least 5 social points
    points = get_db_row("raiting", source_id)["Points"]
    if (points < 1):
      await ctx.send(f"<@!{source_id}>, для использования данной функции нужно иметь минимум 1 очко социального рейтинга! Его можно заработать, например, качественно обновив своё описание.")
      return
      
    iid = args[:args.find("\"")].strip()
    after_quote = args[(args.find("\"") + 1):]
    inside = after_quote[:after_quote.find("\"")].strip()
    links = after_quote[after_quote.find("\"") + 1:].strip().split()
    links = ", ".join(links)
    time = datetime.datetime.now()

    # Now update the general log of tellings, with an AUTOINCREMENT column ID
    try:
      sql = f"INSERT INTO tellings(Timestamp, Target, Source, Description, Evidence, Status) VALUES(\"{time}\", \"{iid}\", \"{source_id}\", \"{inside}\", \"{links}\", \"TBD\")"
      cursor.execute(sql)
      db.commit()
      res_id = cursor.lastrowid

    except Exception as e:
      print(e)
      db.rollback()
      await ctx.send(f"<@!{source_id}>, ошибка обновления базы данных! Убедитесь, что в вашей приписке нет кавычек!")
      return
    
    await ctx.send(f"<@!{source_id}>, ваше заявление принято и вскоре будет рассмотрено одним из Модераторов!")


    # Now keep track of unprocessed tellings through the 'Status' field

    sovnarmod = discord.utils.get(guild.roles, name='СовНарМод')

    links = "\n\t\t\t\t\t\t\t".join(links.split(","))
    # Scan through all the unmarked descriptions and remind SovNarMod members to mark them immediately
    for m in sovnarmod.members:
      await m.create_dm()
      await m.dm_channel.send(f"Товарищ Народный Модератор! Поступило заявление!\n\n\t\tНомер —  {res_id}\n\n\t\tПриписка — *{inside}*\n\n\t\tСсылки — {links}")
       
    #
    #select = "SELECT * FROM unmarked_confessions"
    #try:
    #  cursor.execute(select)
    #  entries = cursor.fetchall()
    #  for e in entries:
    #    to_remind = [i.strip() for i in e["Markers"].split(",")]
    #    for i in to_remind:
    #      snm_dict[i].append(e["ID"])

    #except Exception as e:
    #  print(e)
    #  db.rollback()
   
    #for sovok, spiski in snm_dict.items():
    #  sovok = bot.get_user(int(sovok))
    #  await sovok.create_dm()
    #  quotes = ",\n\t".join([(str(j) + ") \t" + str(i)) for j, i in enumerate(spiski)])
    #  await sovok.dm_channel.send(f"Товарищ Народный Модератор! Вот ваша квота **описаний** за прошедшую неделю: \n\n\t{quotes}")










    


    #id_author = ctx.author.id
    #id_to_search = get_id(mem)
    #mem = bot.get_user(id_to_search)

    #for member in ctx.guild.members:
    #  p = await member.profile()
    #  print(p)

@bot.command(name="статьи")
async def statji(ctx):
  if (not await check_rights_dm(ctx)):
      return

  if (ctx.guild):
    await ctx.message.delete()
    return

  res = "1) Ненормативная лексика\n2) Прескриптивная лингвистика\n3) Спам\n4) Необоснованное оскорбление\n5) низкая Мошна"

  await ctx.send(res)

@bot.command(name="approve")
async def approve_donos(ctx, donos_id, priority, evidence):

  # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
  if (ctx.guild):
    await ctx.message.delete()
    return

  priority = int(priority)
  donos_id = int(donos_id)

  if (priority < 1 or priority > 5):
    await ctx.send(f"<@!{ctx.author.id}>, приоритет должен быть между 1 и 5!")
    return

  source_id = ctx.author.id
  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD)

  row = get_db_row("tellings", donos_id)
  if (row):
    status = row["Status"]

    if status == "TBD":

      await add_points_quick(row["Source"], priority)
      await remove_points_quick(row["Target"], priority)

      try:
        update = f"UPDATE tellings SET Status = \"Approved\" WHERE ID =\"{donos_id}\""
        cursor.execute(update)
        db.commit()

      except Exception as e:
        print(e)
        db.rollback()
        await ctx.send(f"<@!{ctx.author.id}>, ошибка обновления базы данных!")
        return

      await ctx.send(f"<@!{ctx.author.id}>, донос рассмотрен!")

      wording1 = {
        1: "Статья 3. Пункт 2.",
        2: "Статья 1. Пункт 3. (д)",
        3: "Статья 1. Пункт 3. (а)",
        4: "Статья 1. Пункт 3. (в)",
        5: "Статья 2. Пункт 2.",
      }

      wording2 = {
        1: "Ненормативная лексика",
        2: "Прескриптивная лингвистика",
        3: "Спам",
        4: "Необоснованное оскорбление",
        5: "низкая Мошна",
      }

      for ch in guild.channels:
        if "гласность" in ch.name:
          user = bot.get_user(row["Target"])
          await ch.send(f"Модераторы рассмотрели донос на гражданина **{user.display_name}**!\n\n\t\t Дело рассмотрено по статье: *{wording1[priority]} — {wording2[priority]}*\n\n\t\t*Материалы дела* — {evidence}\n\n----------------------------------------------------------------------")


    else:
      await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
      return


  else:
    await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
    return

def get_line(i):
  total = 50
  empty = " "
  line = "="
  ret = ""
  return (line * i) +  (empty * (total - i))

import random
@bot.command(name="мина")
async def dismiss_donos(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, вы наступили на мину!")
  ret = await ctx.send("*Взрыв через 3...*")
  await asyncio.sleep(1)
  await ret.edit(content="*Взрыв через 2...*")
  await asyncio.sleep(1)
  await ret.edit(content="*Взрыв через 1...*")
  await asyncio.sleep(1)
  if (random.random() < 0.5):

    b = await ctx.send("https://i.pinimg.com/originals/0e/14/e8/0e14e85756dbdfe2979998bf8e76e3c4.gif")
    await ctx.message.delete()
    await asyncio.sleep(0.01)
    await ret.edit(content="**Б**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУ**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУУ**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУУУ**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУУУУ**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУУУУУ**")
    await asyncio.sleep(0.05)
    await ret.edit(content="**БУУУУУМ**")
    await asyncio.sleep(1)
    await b.delete()
    await ret.delete()
    await asyncio.sleep(1)
    await ctx.send("Помянем...")

  else:
    # await ret.edit(content="*Уфф... вам повезло и мина не сработала*")
    await slow_printout(ctx, "Уфф... вам повезло и мина не сработала", around="*")

  # Взрывом может зацепить людей вокруг (ближайшие 5 сообщений)

async def slow_printout(ctx, content, around=""):
  msg = await ctx.send(around + content[0] + around)
  for i in range(2, len(content) + 1):
    final = around + content[:i] + around
    await msg.edit(content=final)

@bot.command(name="dismiss")
async def dismiss_donos(ctx, donos_id):

  # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
  if (ctx.guild):
    await ctx.message.delete()
    return

  donos_id = int(donos_id)

  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD)

  row = get_db_row("tellings", donos_id)
  if (row):
    status = row["Status"]

    if status == "TBD":

      try:
        update = f"UPDATE tellings SET Status = \"Dismissed\" WHERE ID =\"{donos_id}\""
        cursor.execute(update)
        db.commit()

      except Exception as e:
        print(e)
        db.rollback()
        await ctx.send(f"<@!{ctx.author.id}>, ошибка обновления базы данных!")
        return

      await ctx.send(f"<@!{ctx.author.id}>, донос рассмотрен!")

      user = bot.get_user(row["Source"])
      await user.create_dm()
      iid = row["ID"]
      await user.dm_channel.send(f"Ваш донос под номером {iid} был отклонён за недостатком улик!")

      await ch.send(f"Модераторы рассмотрели донос на гражданина **{user.display_name}**!\n\n\t\t Дело рассмотрено по статье: *{wording1[priority]} — {wording2[priority]}*\n\n----------------------------------------------------------------------")

    else:
      await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
      return
  else:
    await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
    return

@bot.command(name="blacklist")
async def blacklist_donos(ctx, donos_id):
  # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
  if (ctx.guild):
    await ctx.message.delete()
    return

  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD)

  row = get_db_row("tellings", donos_id)
  if (row):
    status = row["Status"]

    if status == "TBD":

      try:
        update = f"UPDATE tellings SET Status = \"Blacklisted\" WHERE ID =\"{donos_id}\""
        cursor.execute(update)
        db.commit()

      except Exception as e:
        print(e)
        db.rollback()
        await ctx.send(f"<@!{ctx.author.id}>, ошибка обновления статуса доноса!")
        return

      await ctx.send(f"<@!{ctx.author.id}>, донос рассмотрен!")

      black_row = get_db_row("tellings_blacklist", row["Source"])
      user = bot.get_user(row["Source"])

      user_id = row['Source']
      strikes = 0
      name = user.name
      now = datetime.datetime.now()

      if black_row:
        strikes = int(black_row["Strikes"])

      unban_time = now + datetime.timedelta(days=7+strikes)

      try:
        update = f"REPLACE INTO tellings_blacklist(ID, Name, Strikes, Timestamp) VALUES(\"{user_id}\", \"{name}\", \"{strikes + 1}\", \"{unban_time}\")"
        cursor.execute(update)
        db.commit()

      except Exception as e:
        print(e)
        db.rollback()
        await ctx.send(f"<@!{ctx.author.id}>, ошибка обновления бракованных доносов!")
        return

      user = bot.get_user(row["Source"])
      await user.create_dm()
      iid = row["ID"]
      await user.dm_channel.send(f"Ваш донос под номером {iid} был забракован модератором! Вы получаете бан на данную функцию на {7 + strikes} дней. Если вы считаете, что донос был забракован по ошибке, напишите Албанцу в личку.")


    else:
      await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
      return
  else:
    await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
    return

@bot.command(name="кто")
async def who(ctx, mem):
    
    # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
    if (ctx.guild):
      try:
        holder = int(mem)
        msg_id = ctx.message.id
        await ctx.message.delete()
        return
      except Exception as e: 
        print(e)

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

@bot.command(name='resetforgetforgetforget9832164382746')
async def confesss(ctx):

    guild = bot.get_guild(GUILD) 
    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Апатрид')

    db, cursor = get_db_cursor()
    for m in proletariat.members:
      try:
        sql = f"REPLACE INTO raiting(ID, Name, Points) VALUES(\"{m.id}\", \"{m.name}\", \"0\")"
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        print(f"mistake with {m.name}")
        db.rollback()

    for m in politzek.members:
      try:
        sql = f"REPLACE INTO raiting(ID, Name, Points) VALUES(\"{m.id}\", \"{m.name}\", \"0\")"
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        print(f"mistake with {m.name}")
        db.rollback()

    db.close()

@bot.command(name='рассказать')
async def confess(ctx, *, args=None):
#async def confess(ctx, confession):

    name = ctx.author.name
    iid = ctx.author.id
    confession = str(args)
    confession = confession.strip()
    quotes = confession.count("\"")
    backed = confession.count("\\\"")
    quotes -= backed
    
    # was a description updated in the end
    updated = False

    guild = bot.get_guild(GUILD) 
    proletariat = discord.utils.get(guild.roles, name='Пролетарий')
    politzek= discord.utils.get(guild.roles, name='Апатрид')

    if (quotes == 0):
      await ctx.send(f"<@!{iid}> ты забыл(а) **кавычки**!")
      return
    elif (confession[0] != "\"" or confession[-1] != "\""):
      await ctx.send(f"<@!{iid}> **кавычки** должны быть вокруг!")
      return
    elif (quotes > 2):
      await ctx.send(f"<@!{iid}> если ты хочешь использовать **кавычки** в описании, нужно перед ними поставить **« \\\\ »**, то есть например:\nВместо \"Я работаю в комании \"Комплекс\" три года\" =>  \"Я работаю в комании \\\\\"Комплекс\\\\\" три года\"")
      return
    confession = confession[1:-1]
    confession = confession.strip()
    check = confession.split()
    #check = qu        otes.split()
    if len(check) == 1:
      await ctx.send(f"<@!{iid}> твоё описание либо **слишком короткое** либо ты забыл(а) **кавычки**!")
      return

    time = datetime.datetime.now()

    #data = json.dumps(None)
    #data = data.replace("\"", "\\\"")

    row = get_db_row("confessions", iid)
    if row:
      #points = row["Points"]

      if (row["Points"] is None):
        data = {}
        
      else:
        data = json.loads(row["Points"])
        #data[f"{id_author}"] = points

      data = json.dumps(data)
      data = data.replace("\"", "\\\"")

    else:
      data = {}

    db, cursor = get_db_cursor()

    select = f"SELECT * from confessions WHERE ID={iid};"
    replace = f"REPLACE INTO confessions(ID, Name, Confession, Timestamp, Points) VALUES(\"{iid}\", \"{name}\", \"{confession}\", \"{time}\", \"{data}\")"

    try:
      cursor.execute(select)
      timestamp = cursor.fetchone()['Timestamp']
      period = datetime.datetime.now() - timestamp
      days_passed = period.days

      if (days_passed < 0):
        days_passed = 0

      if (days_passed < 7):
        diff = 7 - days_passed
        await ctx.send(f"<@!{iid}> своё описание можно обновлять максимум один раз в 7 дней! \n\n\t**Вы сможете обновить своё через {diff}**")
        return
      
      else:

        try:
          cursor.execute(replace)
          db.commit()

          time = datetime.datetime.now()

          # Now also save user into cache, updating one's description counts as activity on server (same as messaging)
          db, cursor = get_db_cursor()
          sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

          try:
            cursor.execute(sql)
            db.commit()
          except Exception as e:
            print(e)
            db.rollback()

          await ctx.send(f"<@!{iid}> проходите, ваше описание обновлено!")

          #author = bot.get_user(ctx.author.id)
          author = guild.get_member(ctx.author.id) 

          await author.add_roles(proletariat)
          await author.remove_roles(politzek)
          updated = True

        except Exception as e:
          print(e)
          await ctx.send(f"<@!{iid}> c вашим описанием была проблема или проблема подключения к базе данных. \nПопробуйте ещё раз чуть позже или напишите в личку Албанцу.")
          db.rollback()
          
    # If no entry for that user yet exists
    except Exception as e:
      print(e)
      print(f"No entry for {name}...\nInserting new entry...")
      
      try:
        cursor.execute(replace)
        db.commit()
        await ctx.send(f"<@!{iid}> ваше описание обновлено, проходите!")
        updated = True

        time = datetime.datetime.now()

        db, cursor = get_db_cursor()
        sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

        try:
          cursor.execute(sql)
          db.commit()
        except Exception as e:
          print(e)
          db.rollback()

        await ctx.author.add_roles(proletariat)
        await ctx.author.remove_roles(politzek)

      except Exception as e:
        print(e)
        db.rollback()

    # If description was updated successfully need to reinsert user into the unmarked_confessions table
    if updated:

      snm = discord.utils.get(guild.roles, name='СовНарМод')
      markers = ", ".join([str(mem.id) for mem in snm.members])

      replace = f"REPLACE INTO unmarked_confessions(ID, Name, Markers) VALUES(\"{iid}\", \"{name}\", \"{markers}\")"

      try:
        cursor.execute(replace)
        db.commit()
      except Exception as e:
        print(e)
        await ctx.send(f"Проблема учёта оценок новых описаний!")
        db.rollback()

    db.close()

from status import Status

#guild = bot.get_guild(GUILD)
bot.add_cog(Status(bot))
bot.run(TOKEN)
