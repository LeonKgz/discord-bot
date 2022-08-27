#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import base64
import requests
import discord
from discord.utils import get as du_get
from googletrans import Translator
import json
import numpy as np
import os
import pickle
import pymysql.cursors
import urllib.request
import random
import string
from bs4 import BeautifulSoup
from env import *
import datetime

id_repository = {
  "glasnost_channel": "894988536305033228",
}

def get_db_cursor():                                                                                                                                                                                                                                                               
  db = pymysql.connect(host=HOST,
                       user=USER,
                       password=PASSWORD,
                       db=DB,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
  return db, db.cursor()

async def respond(ctx, response):
  return await ctx.send(f"{mention_author(ctx)}, {response}")

async def respond_pkl(bot, pklctx, response):
  
  guild = bot.get_guild(GUILD)
  id_to_search = pklctx.channel_id
  
  for ch in guild.channels:
    if (str(ch.id) == str(id_to_search)):
      return await ch.send(f"<@!{pklctx.author_id}>, {response}")

  return None

def clear_db_table(table):
  db, cursor = get_db_cursor()
  sql = f"DELETE FROM {table}" 
  try:
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()

async def status_update(bot):
    db, cursor = get_db_cursor()
    try:
      sql = f"SELECT COUNT(*) FROM media_records"
      cursor.execute(sql)
      counter = cursor.fetchone()['COUNT(*)']
    except Exception as e:
      print(e)
      db.rollback()

    try:
      n = int(random.random() * counter)
      sql = f"SELECT * FROM media_records ORDER BY Original LIMIT {n-1},1"
      cursor.execute(sql)
      row = cursor.fetchone()
      name = row['Original']
      type = row['DiscordType']
      activity = discord.Activity(name=name, type=type)
      await bot.change_presence(status=discord.Status.online, activity=activity)

    except Exception as e:
      print(e)
      db.rollback()

    db.close()

def delete_row(table, id_val):
  db, cursor = get_db_cursor()
  sql = f"DELETE FROM {table} WHERE ID = \"{id_val}\""  
  try:
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()

def remove_balance(id, amount):
  row = get_db_row("raiting", id)
  
  if not row:
    return False
  curr = row["Money"]
  
  if amount > curr:
    return False

  new = curr - amount
  update_db_entry("raiting", "Money", new, id)

def update_db_entry(table, field_name, new_val, id_val):
  if not DB == str(os.getenv('TEST_DB_DATABASE')):
    print("Can only rewrite tables in test mode!")
    return 

  db, cursor = get_db_cursor()
  sql = f"UPDATE {table} SET {field_name} = \"{new_val}\" WHERE ID = \"{id_val}\""  
  try:
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()

async def rename_all_channels(bot, ctx, lang):

    message = await respond_pkl(bot, ctx, "переименовываю все каналы! Это займёт несколько секунд...")
    guild = bot.get_guild(GUILD)
    is_random = lang.lower() == "random"
    tr = Translator()

    curr_lang_name_in_russian = tr.translate(lang + " language", dest='ru').text.lower()
    if "язык" in curr_lang_name_in_russian:
      curr_lang_name_in_russian = curr_lang_name_in_russian.replace("язык", "").strip()

    for ch in guild.channels:
      row = get_db_row("tmg_channels", str(ch.id))
      if not row:
        print(f"{ch.name} was not found!")
        continue
      
      russian = row['Russian']
      if lang in row:
        res = row['Prefix'] + row[lang]
      elif is_random:
        lang = random.choice(list(LANGUAGE_CODES.keys()))
        res = row['Prefix'] + tr.translate(russian, dest=LANGUAGE_CODES[lang]).text
      else:
        # google translate from russian to the 'lang' via google translate
        res = row['Prefix'] + tr.translate(russian, dest=LANGUAGE_CODES[lang.lower()]).text

      if is_random:     
        curr_lang_name_in_russian = tr.translate(lang + " language", dest='ru').text.lower()
        if "язык" in curr_lang_name_in_russian:
          curr_lang_name_in_russian = curr_lang_name_in_russian.replace("язык", "").strip()

      await ch.edit(name=res, topic=f"{russian} ({curr_lang_name_in_russian})")
      # break

    await message.delete()
    await respond_pkl(bot, ctx, "все каналы переименованы!")
    lang_name = tr.translate(lang, dest='ru').text

    lcode = "random" if is_random else LANGUAGE_CODES[lang.lower()]
    if "-" in lcode:
      lcode = lcode.split("-")[0].strip()

    url = f"http://albenz.xyz:6969/flag?code={lcode}"
    response = requests.get(url)
    thumb = response.json()["url"]
    
    if not thumb:
      thumb = "https://c.tenor.com/KEceaHH8vkkAAAAM/%D0%BC%D0%BE%D1%80%D0%B3%D0%B5%D0%BD%D0%B0%D0%BB.gif"
    
    if is_random:
      curr_lang_name_in_russian = "Случайный" 
    
    embed = await get_simple_embed(
            title=f"запрещает вам срать!",
            message=f"Названия всех каналов переведены на **{curr_lang_name_in_russian.title()}** язык!",
            thumbnail_url=thumb,
            color_hex_code=0x000000,
            footer=""
          )
    embed.set_author(name=ctx.display_name, icon_url=ctx.avatar_url)
    gl = get_channel_by_name(bot, "гласность", 'Russian')
    await gl.send(embed=embed)

def get_str_hour(num):
  counter_str = "часов"
  if 11 <= num <= 20:
    return counter_str

  mod = num % 10

  if mod == 1:
    counter_str = "час"

  if mod > 1 and mod < 5:
    counter_str = "часа"

  return counter_str     

def get_str_minute(num):
  counter_str = "минут"
  if 11 <= num <= 20:
    return counter_str
    
  mod = num % 10

  if mod == 1:
    counter_str = "минуту"

  if mod > 1 and mod < 5:
    counter_str = "минуты"

  return counter_str

def save_pickle(dictionary, filename):
  outfile = open(filename, 'wb')
  pickle.dump(dictionary, outfile)
  outfile.close()

def load_pickle(filename):
  dictionary = {}
  if os.path.exists(filename):
    infile = open(filename,'rb')
    dictionary = pickle.load(infile)      
    infile.close()
  return dictionary

def execute_custom(sql):
  db, cursor = get_db_cursor()
  try:
    cursor.execute(sql)
    db.commit()
    db.close()
    return True
    
  except Exception as e:
    print(e)
    db.rollback()
    db.close()
  return False

def get_rows_custom(sql):
  db, cursor = get_db_cursor()
  try:
    cursor.execute(sql)
    rows = cursor.fetchall()
    db.close()
    return rows
    
  except Exception as e:
    print(e)
    db.rollback()
    db.close()
    return False

def get_db_row(db_name, id_to_search):

    db, cursor = get_db_cursor()

    select = f"SELECT * from {db_name} WHERE ID={id_to_search};"

    try:
      cursor.execute(select)
      row = cursor.fetchone()
      db.close()
      return row
      
    except Exception as e:
      print(e)
      db.rollback()
      db.close()
      return False

def get_all_rows(db_name):
    db, cursor = get_db_cursor()

    select = f"SELECT * from {db_name}"

    try:
      cursor.execute(select)
      rows = cursor.fetchall()
      db.close()
      return rows
      
    except Exception as e:
      print(e)
      db.rollback()
      db.close()
      return False

def generate_text(word_size=10, text_size=10):
  text = ' '.join([''.join(random.choices(string.ascii_uppercase + string.digits, k = word_size)) for _ in range(text_size)])
  return text

async def parse_zettel_json(ctx, data):
  
  if "verses" in data:
    verses = data["verses"]

    title = verses[0]["title"]
    if (not title):
      raise Exception("JSON is empty")

    author = verses[0]["author"]
    if (author == ""):
      head = f"{title}."
    else:
      head = f"{title}. {author}."

    for v in verses:

      data = v["content"]
      remedy = v["remedy"]

      data = "\n\n".join(data.split("\n\n")[1:])
      data = data.replace("  ", " ")
      data = data.strip()

      test_string = f"***{remedy}***\t{data}\n"
      
      size = len(test_string)

      if (size > 2000):
        splits = data.split("\n \n")
        
        if (len(splits) > 1):

          await ctx.send(f"\t\t\t\t***{remedy}***\t{splits[0]}\n")
          # await ctx.send(f"—\n\n*{head}*\n\n\t{splits[0]}\n—")
          for e in splits[1:-1]:
            await ctx.send(f"\n{e}\n")
          
          await ctx.send(f"{splits[-1]}\n\n")

        else:

          data = f"***{remedy}***\t{data}"
          left = 0
          right = 2000
          chunks = []
          while (right - left > 0):
    #        print(f"({left}, {right})")
            while right != size and data[right-1] != " ":
              right -= 1
            curr = data[left:right]
            chunks.append(curr)
            left = right
            if (size - left > 2000):
              right += 2000
            else:
              right = size

          for c in chunks:
            await ctx.send(f"{c}")

        continue 
  
      # await ctx.send(f"—\n\n*{head}*\n\n{data}\n\n—")
      await ctx.send(f"\t\t\t\t***{remedy}***\t{data}\n")

    await ctx.send(f"...")
      
  elif not data["files"]:
    author = data["author"]
    title = data["title"]
    links = data["links"]
    data = data["content"]

    if (not title):
      raise Exception("JSON is empty")
    
    # TODO for meditations I dont need duplicate of title in the data field, Fix on server side. Then just remove empty spaces before new lines and stuff like that. Look out for anoimalies with repr()
    #print(repr(data))

    if (author == ""):
      head = f"{title}."
    else:
      head = f"{title}. {author}."
      
    # TODO Figure out one system to parse all the text files
    # Possibly fix new lines in meditations, and maybe scan all md files together to clean off weird spaces and
    # tabs

    #print(repr(data))
      
    data = "\n\n".join(data.split("\n\n")[1:])
    data = data.replace("  ", " ")
    data = data.strip()

    if len(links) > 0:
      ls = "\n".join(links)
      data += f"\n\n{ls}"

    size = len(data)
    if (size > 2000):
      # For now there is a limit on number of characters that the bot can send on server. 
      # Manually make sure that paragraphs are less than 2000 chars and send them seperately
      splits = data.split("\n \n")
      if (len(splits) > 1):
        await ctx.send(f"—\n\n*{head}*\n\n\t{splits[0]}\n—")
        for e in splits[1:-1]:
          await ctx.send(f"\n{e}\n—")
        
        await ctx.send(f"{splits[-1]}\n\n—")

      else:
        
        left = 0
        right = 2000
        chunks = []
        while (right - left > 0):
  #        print(f"({left}, {right})")
          while right != size and data[right-1] != " ":
            right -= 1
          curr = data[left:right]
          chunks.append(curr)
          left = right
          if (size - left > 2000):
            right += 2000
          else:
            right = size

        for c in chunks:
          await ctx.send(f"{c}")
      return

    #data = data.replace("\\n", "\n")
 
    await ctx.send(f"—\n\n*{head}*\n\n{data}\n\n—")
    #embed = discord.Embed(title=f"{title}. {author}", description=f"\n\n\t{data}\n\n", color=0xa87f32) #creates embed
    #embed.set_footer(text=f"перевод: Переводчик")
    #await ctx.send(embed=embed)
  
  else:
    content = data["content"]
    # TODO Solve multiple attachments
    imgdata = data["files"][0]
    author = data["author"]
    interpreter = data["interpreter"]
    title = data["title"]
    number= data["number"]

    thumbs = {
      "Конфуций": "https://i.imgur.com/nJFW7SG.png",
      "Омар Хаям": "https://obrazovaka.ru/wp-content/uploads/2021/02/omar-hayyam-e1614119392242.jpg", 
      "Белла Ахмадулина": "https://i.imgur.com/yPiHVTY.png",
      "Евгений Баратынский": "https://i.imgur.com/YwXdyEr.png",
    }

    if (not title):
      raise Exception("JSON is empty")

    imgdata = base64.b64decode(imgdata.encode("ascii"))

    filename = 'temporary_holder'  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
      f.write(imgdata)

      if author and title.lower().strip() != author.lower().strip():
        embed = discord.Embed(title=f"{title}. {author}", description=f"{number}", color=0xa87f32) #creates embed
      else:
        embed = discord.Embed(title=f"{title}", description=f"{number}", color=0xa87f32) #creates embed
      
      if author:
        embed.set_thumbnail(url=thumbs[author])
      
      dfile = discord.File(filename, filename="image.png")
      embed.set_image(url="attachment://image.png")

      if interpreter: 
        embed.set_footer(text=f"перевод: {interpreter}")
      
      await ctx.send(file=dfile, embed=embed)

      f.close()
      os.remove(filename)

def get_money_str(num):
  mod = num % 10
  counter_str = "шекелей"
  
  if mod == 1:
    counter_str = "шекель"

  if mod > 1 and mod < 5:
    counter_str = "шекеля"

  return counter_str

def get_humans_str(num):
  mod = num % 10
  counter_str = "человек"

  if mod > 1 and mod < 5:
    counter_str = "человека"

  return counter_str

def get_times_str(num):
  mod = num % 10

  
  counter_str = "раз"
  
  if mod > 1 and mod < 5:
    counter_str = "раза"

  return counter_str



def get_channel_names(bot, id):
  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM tmg_channels WHERE ID = \"{id}\""
  try:
    cursor.execute(sql)
    row = cursor.fetchone()
    db.close()
    return row

  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()
  return False  

def mention_author(ctx):
  return f"<@!{ctx.author.id}>"

def mention(id):
  return f"<@!{id}>"

def mention_role(id):
  return f"<@&{id}>"

async def check_rights(bot, ctx, acceptable_roles, tell=True):
  #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит']
  super_roles = acceptable_roles

  try:
    res_roles = ctx.author.roles
  except Exception as e:
    res_roles = bot.get_user(ctx.author.id).roles

  for role in list(map(str, res_roles)):
    if (role in super_roles):
      return True
  if tell:
    response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(du_get(bot.emojis, name='peepoClown'))
    await ctx.send(response)
  return False

async def disconnect(bot, ctx):
  for x in bot.voice_clients:
    if(x.guild == ctx.message.guild):
      await x.disconnect()
      return True
  return False

def get_channel_by_name(bot, name, language):
  guild = bot.get_guild(GUILD)
  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM tmg_channels WHERE {language} = \"{name}\""
  try:
    cursor.execute(sql)
    row = cursor.fetchone()
    id_to_search = str(row["ID"])
    for ch in guild.channels:
      if (str(ch.id) == id_to_search):
        db.close()
        return ch
  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()
  return False  

async def get_simple_embed(title, message, thumbnail_url, color_hex_code, footer):
  embed = discord.Embed(title=title) 
  embed.set_thumbnail(url=thumbnail_url)

  # light green, same as СовНарМод
  embed.color = color_hex_code 
  embed.add_field(name="⠀", value=message, inline=False)

  embed.set_footer(text=footer)
  # embed.add_field(name=main_field, value="⠀", inline=False)

  return embed

# simple beacause it has one field, to convey one message regarding a server member
async def get_simple_member_embed(bot, member, title, message, thumbnail_url, color_hex_code):
  embed = discord.Embed(title=title) 
  embed.set_author(name=member.display_name, icon_url=member.avatar_url)
  embed.set_thumbnail(url=thumbnail_url)

  # light green, same as СовНарМод
  embed.color = color_hex_code 
  embed.add_field(name="⠀", value=message, inline=False)

  db, cursor = get_db_cursor()
  guild = bot.get_guild(GUILD)
  try:
    #cursor.execute(sql)
    cursor.execute("SET @row_number = 0;")
    cursor.execute(f"SELECT num, ID, Name, Points FROM (SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC) a WHERE ID = {member.id}")

    res = cursor.fetchone()
    num = res["num"]
    points = res["Points"]
  except Exception as e:
    print(e)
    db.rollback()
    ch = get_channel_by_name(bot, "технический", 'Russian')
    await ch.send(f"Problems displaying \"{title}\" embed for server member \"{member.display_name}\"")
    return 

  embed.set_footer(text="Смотрите как зарабатывать очки в Манифесте")
  main_field = f"⠀\nСоциальный Рейтинг — *{points} ( {num}-е место )*"
  embed.add_field(name=main_field, value="⠀", inline=False)

  return embed

# Досье
def get_file(bot, mem):
  id_to_search = mem.id
  embed = discord.Embed(title=f"Досье №{id_to_search}") 
  embed.set_author(name=mem.display_name, icon_url=mem.avatar_url)

  #description = get_description(id_to_search)
  row = get_db_row("confessions", id_to_search)
  
  mean_str = "⠀\n"

  if row:
    #points = row["Points"]
    description = row["Confession"]

    if (row["Points"] is None):
      data = {}
      
    else:
      data = json.loads(row["Points"])
      #data[f"{id_author}"] = points

    vals = list(data.values())

    if len(vals) == 0:
      curr_mean = False
      mean_str = "⠀\nОписание пока не было оценено\n\n"
    else:
      curr_mean = int(np.mean(vals))
      mean_str = f"⠀\nСредняя оценка описания — *{curr_mean} / 10*\n\n"
      # TODO in the future we can also check the respective entry in the unmarked_confessions to make it clear
      # whether the current mark is final or there are still moderators who have yet to mark it

  else:
    #mean_str = f"Средняя оценка описания — *{curr_mean} / 10*"
    description = False
    print("here")

  if not description:
    description = f"{mem.display_name} пока не предоставил(а) своё описание."

  if (len(description) > 1024):
    description = description[:1019] + "..."

  embed.add_field(name="⠀", value=f"*{description}*", inline=False)

  thumbs = {
    "zek": "https://i.ibb.co/fqsc4TP/image.jpg",
    "shiz": "https://i.ibb.co/Vvsc71q/shiz.jpg",
    "polit_buro": "https://i.ibb.co/JBr8jVj/image.png",
    "sovnarmod": "https://i.ibb.co/mR5ZxHK/zacon.jpg",
    "vchk": "https://i.ibb.co/KXDLLsr/vchk.jpg",
    "truppa": "https://i.ibb.co/2KCYPQZ/hands-hold-a-theater-mask-dot-technique-of-drawing-change-of-role-in-ather-Theater-Actor-tattoo-Hypo.jpg",
    "narod_artist": "https://i.ibb.co/6mbXrJq/narod-artist-tmg.png",
    "blatnoi": "https://i.ibb.co/s1Q7gwc/blatnoi.jpg",
    "onizuka": "https://i.ibb.co/wwJPFYR/onizuka.jpg",
    "chtets": "https://i.ibb.co/5K5hGjH/chtets.jpg",
    "actor_zapasa": "https://i.ibb.co/vPk10R5/actor-zapasa.jpg",
    "proletariat": "https://i.ibb.co/VQtxxPj/proletariat.jpg",
    "apatrid": "https://i.ibb.co/DwsbRGY/apatrid.jpg",
  }
 
  colours = {
    "zek": 0x9b59b6,
    "shiz": 0xe67e22,
    "polit_buro": 0xf30101,
    "sovnarmod": 0x2ecc71,
    "vchk": 0xf1c40f,
    "truppa": 0x1abc9c,
    "narod_artist": 0x3498db,
    "blatnoi": 0xe91e63,
    "onizuka": 0xe67e22,
    "chtets": 0xe67e22,
    "actor_zapasa": 0x1abc9c,
    "proletariat": 0x99aab5,
    "apatrid": 0x2f3136,
  }
  
  #embed = discord.Embed(title=f"Досье", description=f"", color=0xa87f32, url="https://albenz.xyz", footer="Переводчик — модолец!") #creates embed
  #embed.set_author(name=mem.display_name, url="https://twitter.com/RealDrewData", icon_url=mem.avatar_url)

  # thumbnail has an icon for different roles, i.e. Proletari, SovNarMod
  #embed.set_thumbnail(url=thumb)
  
  roles_names_list = [
    "Апатрид",
    "Политзаключённый",
    "Шиз",
    "Политбюро ЦКТМГ",
    "СовНарМод",
    "ВЧК",
    "Драматическая Труппа",
    "Народный Артист ТМГ",
    "Блатной",
    "Востоковед",
    "Чтец",
    "Актёр Запаса",
    "Пролетарий",
  ]
  
  roles_names_to_code = {
    "Политзаключённый": "zek",
    "Шиз": "shiz",
    "Политбюро ЦКТМГ": "polit_buro",
    "СовНарМод": "sovnarmod",
    "ВЧК": "vchk",
    "Драматическая Труппа": "truppa",
    "Народный Артист ТМГ": "narod_artist",
    "Блатной": "blatnoi",
    "Востоковед": "onizuka",
    "Чтец": "chtets",
    "Актёр Запаса": "actor_zapasa",
    "Пролетарий": "proletariat",
    "Апатрид": "apatrid",
  }

  
  day = int(datetime.datetime.now().day)
  start_day = AMNESTY_START_DAY
  end_day = AMNESTY_END_DAY
  is_amnesty = start_day <= day < end_day

  guild = bot.get_guild(GUILD) 
  for member in guild.members:
    if (member.id == id_to_search):
      mem_roles = list(map(str, member.roles))
      for role in roles_names_list:
        if role in mem_roles:
          if is_amnesty and role == "Апатрид":
            continue
          embed.set_thumbnail(url=thumbs[roles_names_to_code[role]])
          embed.color = colours[roles_names_to_code[role]]

          dominating_role = role
          #embed.set_footer(text="СовНарМод ТМГ")
          # embed.set_footer(text=dominating_role)
          embed.set_footer(text="   ||   ".join([dominating_role] + [m for m in mem_roles if m != "@everyone" and m != dominating_role]))
          
          break

  # SET @row_number = 0; 
  # SELECT num, ID, NAME, Points 
  # FROM (SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points 
  # FROM raiting ORDER BY Points DESC) a
  # WHERE ID = '696405991876722718'

  db, cursor = get_db_cursor()
  sql = f"SET @row_number = 0; SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC"

  try:
    #cursor.execute(sql)
    cursor.execute("SET @row_number = 0;")
    cursor.execute(f"SELECT num, ID, Name, Points FROM (SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC) a WHERE ID = {id_to_search}")

    res = cursor.fetchone()
    num = res["num"]
    points = res["Points"]
    #db.commit()
  except Exception as e:
    print(e)
    db.rollback()
  db.close()


	# Counting the number of tellings on the target member
  counter = 0
  
  db, cursor = get_db_cursor()
  try:
    sql = f"SELECT COUNT(*) FROM tellings WHERE Target = {id_to_search}"
    cursor.execute(sql)
    counter = int(cursor.fetchone()['COUNT(*)'])
  except Exception as e:
    print(e)
    db.rollback()
  
  db.close()
  #mod = counter % 10
  #counter_str = "раз"
  #if mod > 1 and mod < 5:
  #  counter_str = "раза"

  # get the number of times a person has been imprisoned
  imprisoned = 0
  row = get_db_row("prisoners", id_to_search)
  if row:
    imprisoned = int(row["Counter"])
    
  nn = ""
  main_field = "" 
  if counter > 0:
    main_field += f"На гражданина донесено *{counter} {get_times_str(counter)}*"
  if imprisoned > 0:
    nn = "\n\n" if main_field else ""
    main_field += f"{nn}Заключён в ГУЛАГ *{imprisoned} {get_times_str(imprisoned)}*"
  
  nn = "\n\n" if main_field else ""
  main_field += f"{nn}Социальный Рейтинг — *{points} ( {num}-е место )*" 

  if description:
    main_field = mean_str + main_field
  else: 
    main_field = "⠀\n" + main_field

  logs = get_logs_compressed(id_to_search)

  if logs[-1]:
    main_field += f"\n\nАктивность:"
    embed.add_field(name=main_field, value=f"⠀\n{logs[0]}", inline=False)
    for l in logs[1:]:
      embed.add_field(name="⠀", value=f"{l}", inline=False)

  else:
    embed.add_field(name=main_field, value="⠀", inline=False)
  
  return embed

def insert_row(table, fields, values):
  
  db, cursor = get_db_cursor()
  fs = ", ".join(fields)
  vs = ", ".join([f"\"{v}\"" for v in values])
  sql = f"INSERT INTO {table}({fs}) VALUES({vs})"
  
  try: 
    cursor.execute(sql)
    db.commit()
    ret = cursor.lastrowid
  except Exception as e:
    ret = None
    print(e)
    db.rollback()

  db.close()

  return ret

def record_purchase(source, target, timestamp, type, item, amount, status):
  # TODO if type in objects like 'waifu', then also record in fn_basket
  # oterhwise if its something like 'Rename' no need to record it, since you cannot trade it really (at least yet)
  return insert_row("fn_purchase", ["Source", "Target", "Timestamp", "Type", "Item", "Amount", "Status"], [source, target, timestamp, type, item, amount, status])

def record_logs(timestamp, source, target, type, sign, amount, description):
  db, cursor = get_db_cursor()
  sql = f"INSERT INTO logs(Timestamp, Source, Target, Type, Sign, Amount, Description) VALUES(\"{timestamp}\",\"{source}\", \"{target}\", \"{type}\", \"{sign}\", \"{amount}\", \'{description}\')"

  try: 
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    entry = "INSERT INTO logs(" + (", ".join([timestamp, source, target, type, sign, amount, description])) + ")"
    print(f"Failed to record logs for this entry: {entry}")

# same as get_logs but compresses weekly activity into months
def get_logs_compressed(id_to_search):

  # id_author = ctx.author.id
  # id_to_search = get_id(mem)
  # mem = bot.get_user(id_to_search)
  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM logs WHERE Target = \"{id_to_search}\" ORDER BY Timestamp ASC"
  field_content_limit = 1020


  try:

    cursor.execute(sql)
    ret = cursor.fetchall()
    res = [""]
    size = 0

    curr_month_activity = []
    curr_month = None
    prev_row = None

    def record_row(r, res):
        nonlocal size      
        sign = "+" if r['Sign'] == "Positive" else "-"
        
        time = r['Timestamp'].strftime('%d-%m-%Y')
        # num = sign + str(r['Amount'])
        to_add = f"` {time} `\t—\t` {sign}{r['Amount']:<2} `\t*{r['Description']}*\n"

        if len(to_add) + size > field_content_limit:
          res.append("") 
          size = 0

        res[-1] += to_add 
        size += len(to_add)

    def is_weekly(r):
      return r and r['Type'] == 'Activity' and r['Description'] == "Недельная активность"

    def record_month_activity(curr_month_activity, res):
      if curr_month_activity:

        if len(curr_month_activity) == 1:
          record_row(curr_month_activity[0], res)
          return

        monthly_row = {key: val for key, val in curr_month_activity[-1].items()}
        monthly_row["Amount"] = sum([sub_r["Amount"] for sub_r in curr_month_activity])
        monthly_row["Description"] = "Недельная активность (за месяц)"
        record_row(monthly_row, res)

    for r in ret:
      # TODO add additional check in the futura addition od descriptions in other languages e.g. english
      curr_month = r['Timestamp'].month
      curr_time = r['Timestamp']
      if is_weekly(r):
        if curr_month_activity and curr_month_activity[-1]['Timestamp'].month == curr_month:
          curr_month_activity.append(r)
        else:
          record_month_activity(curr_month_activity, res)
          curr_month_activity = [r]

      else:        
        if is_weekly(prev_row) and curr_time > curr_month_activity[-1]['Timestamp']:
          record_month_activity(curr_month_activity, res)
          curr_month_activity = []

        record_row(r, res)
      prev_row = r

    record_month_activity(curr_month_activity, res)

    return res

  except Exception as e:

    print(e)
    db.rollback()

  db.close()

  return False

def get_logs(id_to_search):

  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM logs WHERE Target = \"{id_to_search}\" ORDER BY Timestamp ASC"
  field_content_limit = 1020

  try:

    cursor.execute(sql)
    ret = cursor.fetchall()
    res = [""]
    size = 0

    for r in ret:
      sign = "+" if r['Sign'] == "Positive" else "-"
      
      time = r['Timestamp'].strftime('%d-%m-%Y')
      to_add = f"` {time} `\t—\t` {sign}{r['Amount']:<2} `\t*{r['Description']}*\n"

      if len(to_add) + size > field_content_limit:
        res.append("") 
        size = 0

      res[-1] += to_add 
      size += len(to_add)
    
    return res

  except Exception as e:

    print(e)
    db.rollback()

  db.close()

  return False

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))

    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def get_random_element(arr):
  if arr:
    return arr[int(random.random() * len(arr))]
  return False

def get_kanji_info(kanji):
    # open a connection to a URL using urllib
    jisho_url_prefix = "https://jisho.org/search/"
    jisho_url_postfix = "%20%23kanji"

    # kanji = sys.argv[1][0]
    val = urllib.parse.quote(kanji.encode('utf-8'))
    webUrl = urllib.request.urlopen(f'{jisho_url_prefix}{val}{jisho_url_postfix}')

    #get the result code and print it
    code = str(webUrl.getcode())

    # read the data from the URL and print it
    data = (webUrl.read())
    data = data.decode('Utf-8')

    temp = data.split("<div class=\"kanji details\">")[1]
    temp = temp.split("<div class=\"row\">")
    temp = temp[2]

    # Getting meanings
    meaning = temp.split("<div class=\"kanji-details__main-meanings\">")[1].split("</div>")[0]
    meaning = meaning.replace("\\n", "")
    meaning = meaning.replace("\n", "")
    meaning = meaning.replace(" ", "")
    meanings = meaning.split(",")
    meanings = ", ".join(meanings)

    # Get kun yomi
    try:
        kun = temp.split("<dl class=\"dictionary_entry kun_yomi\">")
        mumble_jumble = kun[1].split("</dl>")[0]
        kun = ", ".join([v.split(">")[1].split("</a")[0] for v in mumble_jumble.split("a href")[1:]])
    except IndexError as e:
        print(e)
        kun = ""

    # Get on yomi
    try:
        on = temp.split("<dl class=\"dictionary_entry on_yomi\">")
        mumble_jumble = on[-1].split("</dl>")[0]
        on = ", ".join([v.split(">")[1].split("</a")[0] for v in mumble_jumble.split("a href")[1:]])
    except IndexError as e:
        print(e)
        on = ""

    # with open(f'{kanji}.txt', 'w', encoding='utf-8') as file:
    #     res = f"{meanings}\n{kun}\n{on}"
    #     file.write(res)
    #     file.close()

    return on, kun, meanings

def get_staroe_radio_name_and_link(link):
  try:
    webUrl = urllib.request.urlopen(link)
  except Exception as e:
    print(e)
    return None, None, str(e)

  # read the data from the URL and print it
  data = (webUrl.read())
  data = data.decode('Utf-8')
  soup = BeautifulSoup(data, 'html.parser')
  player = soup.find("audio", {"id": "radio-player"})
  link = player.get('src')
  header = soup.find("h1").get_text().strip()

  return header, link

def get_staroe_radio_info(dir=""):
  try:
    webUrl = urllib.request.urlopen(f'http://www.staroeradio.ru/program/{dir}')
  except Exception as e:
    print(e)
    return None, None, str(e)

  # read the data from the URL and print it
  data = (webUrl.read())
  data = data.decode('Utf-8')
  soup = BeautifulSoup(data, 'html.parser')
  soup = soup.find("div", {"class": "mp3list grid_9"})
  soup = soup.find("a")
  soup = soup.find("td", {"class": "mp3name1"})
  return soup.get_text().strip()

def get_word_info(word):
    # open a connection to a URL using urllib
    print(word)
    jisho_url_prefix = "https://jisho.org/word/"
    val = urllib.parse.quote(word.encode('utf-8'))
    try:
      webUrl = urllib.request.urlopen(f'{jisho_url_prefix}{val}')
    except Exception as e:
      print(e)
      return None, None, str(e)

    # read the data from the URL and print it
    data = (webUrl.read())
    data = data.decode('Utf-8')

    soup = BeautifulSoup(data, 'html.parser')
    soup = soup.find("div", {"class": "concept_light clearfix"})
    japanese = soup.find("div", {"class": "concept_light-representation"})
    furigana = japanese.find("span", {"class": "furigana"})
    furigana_including_spaces = [f.get_text() for f in furigana.findChildren()]
    text = japanese.find("span", {"class": "text"})
    kana_between_kanji = [f.get_text() for f in text.findChildren()]
    
    if kana_between_kanji:
      idx = 0
      for i in range(len(furigana_including_spaces)):
        curr = furigana_including_spaces[i]
        if not curr:
          furigana_including_spaces[i] = kana_between_kanji[idx]
          idx += 1

    proper_furigana = "".join(furigana_including_spaces)
    english = soup.find("span", {"class": "meaning-meaning"})
    english = english.get_text()
    return word, proper_furigana, english

def get_word_info_deprecated(word):
    # open a connection to a URL using urllib
    jisho_url_prefix = "https://jisho.org/word/"
    # jisho_url_postfix = "%20%23kanji"

    # kanji = sys.argv[1][0]
    val = urllib.parse.quote(word.encode('utf-8'))
    try:
      webUrl = urllib.request.urlopen(f'{jisho_url_prefix}{val}')
    except Exception as e:
      print(e)
      return None, None, str(e)

    #get the result code and print it
    code = str(webUrl.getcode())

    # TODO: Get furigana separately; get meanings (first one for now)

    # read the data from the URL and print it
    data = (webUrl.read())
    data = data.decode('Utf-8')
    temp = data.split("<div class=\"concept_light clearfix\">")[1]
    temp = temp.split("<h3>Discussions")[0].split("<div class=\"concept_light-meanings")
    # Now temp is an array of two divs, one with readings and the other with meaning

    # furigana1 = temp[0].split("-up kanji\">")[1].split("</span>")[0]
    furigana1s = temp[0].split("-up kanji\">")
    # subparts = int(furigana1s[0][-1])
    subparts = temp[0].count("-up kanji\">") 
    furigana1 = ""
    for i in range(subparts):
      furigana1 += furigana1s[i+1].split("</span>")[0]

    furigana2 = temp[0].split("<span class=\"text\">")[1].split("</div")[0].replace("<span>", "").replace("</span>", "").strip()
    
    # If kanji present at all (could be just kana)
    if (len(temp[0].split("<span class=\"text\">")[1].split("<span>")[0].strip()) > 0):
      try:
        # furigana3 = temp[0].split("<span class=\"text\">")[1].split("</div")[0].replace("<span>", "").replace("</span>", "").strip()
        furigana3 = "".join(temp[0].split("<span class=\"text\">")[1].split("</div")[0].split("<span>")[1:]).replace("</span>", "").strip()
      except Exception as e:
        furigana3 = ""
    else:
      furigana3 = ""

    meanings = temp[1]
    meaning1 = meanings.split('1. </span><span class="meaning-meaning">')[1].split("</span><span>")[0]
    # print(furigana1)

    # this is normal way of writing mixture of kanji and kana
    mixed = furigana2

    # this is full furigana reading 
    furigana = furigana1 + furigana3

    # TODO meanings now!
    meaning = meaning1

    return mixed, furigana, meaning

def is_apartid_in_amnesty(iid):
  day = int(datetime.datetime.now().day)
  if AMNESTY_START_DAY <= day <= AMNESTY_END_DAY:
      rows = get_all_rows("amnesty")
      print([r['ID'] for r in rows])
      if int(iid) in [r['ID'] for r in rows]:
        return True

  return False

def get_channel_name_languages():
  db, cursor = get_db_cursor()
  sql = "SHOW COLUMNS FROM tmg_channels"
  try:
    cursor.execute(sql)
    res = cursor.fetchall()
    # list of available language options (effectively list of column names from the tmg_channels table minus the first two which is 'ID') and Preifx
    langs = [r['Field'] for r in res][2:]
    return langs
  except Exception as e:
    print(e)
    db.rollback()
    return []

async def check_rights_dm(ctx):
  super_roles = [214320783357378560, 696405991876722718, 384492518043287555, 498264068415553537]
  if ctx.author.id in super_roles:
      return True
  response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(du_get(bot.emojis, name='peepoClown'))
  await ctx.send(response)
  return False
