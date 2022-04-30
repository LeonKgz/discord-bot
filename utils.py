#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import asyncio
import base64
import discord
import json
import numpy as np
import os
import pymysql.cursors
import urllib.request
import urllib.request

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))
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

async def parse_zettel_json(ctx, data):
  if not data["files"]:
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

      await ctx.send(f"—\n\n*{head}*\n\n\t{splits[0]}\n—")
      for e in splits[1:-1]:
        await ctx.send(f"\n{e}\n—")
      
      await ctx.send(f"{splits[-1]}\n\n—")
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

# depending on the number returns the currect russian analogue of «times» i.e. раза/раза
def get_times_str(num):
  mod = num % 10
  counter_str = "раз"
  
  if mod > 1 and mod < 5:
    counter_str = "раза"

  return counter_str

# simple beacause it has one field, to convey one message
async def get_simple_embed(bot, member, title, message, thumbnail_url, color_hex_code):
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
    for ch in guild.channels:
      if ("технический" in ch.name):
        await ch.send(f"Problems displaying \"{title}\" embed for server member \"{member.display_name}\"")
        return 

  embed.set_footer(text="Смотрите как зарабатывать очки в Манифесте")
  main_field = f"⠀\nСоциальный Рейтинг — *{points} ( {num}-е место )*"
  embed.add_field(name=main_field, value="⠀", inline=False)

  return embed

# Досье
def get_file(bot, mem):
  id_to_search = mem.id
  embed = discord.Embed(title=f"Досье") 
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

  guild = bot.get_guild(GUILD) 
  for member in guild.members:
    if (member.id == id_to_search):
      mem_roles = list(map(str, member.roles))
      for role in roles_names_list:
        if role in mem_roles:
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
    main_field += f"{nn} Заключён в ГУЛАГ *{imprisoned} {get_times_str(imprisoned)}*"
  
  nn = "\n\n" if main_field else ""
  main_field += f"{nn}Социальный Рейтинг — *{points} ( {num}-е место )*" 

  if description:
    main_field = mean_str + main_field
  else: 
    main_field = "⠀\n" + main_field


  logs = get_logs(id_to_search)
  if logs[-1]:
    main_field += f"\n\nАктивность:"
    embed.add_field(name=main_field, value=f"⠀\n{logs[0]}\n⠀", inline=False)
    print(len(logs[0]))
    for l in logs[1:]:
      embed.add_field(name="⠀", value=f"⠀\n{l}\n⠀", inline=False)

  else:
    embed.add_field(name=main_field, value="⠀", inline=False)
  
  # if logs:
  # embed.add_field(name=main_field, value="⠀", inline=False)
    # main_field += f"⠀\n{logs}"
    # embed.add_field(name="Logs", value=logs, inline=False)
  # embed.add_field(name=main_field, value="⠀", inline=False)

  # attach moshna печать
#  embed.add_field(name="Валюта", value="Шанырак - 12", inline=True)
  return embed

def record_logs(timestamp, source, target, type, sign, amount, description):
  db, cursor = get_db_cursor()
  sql = f"INSERT INTO logs(Timestamp, Source, Target, Type, Sign, Amount, Description) VALUES(\"{timestamp}\",\"{source}\", \"{target}\", \"{type}\", \"{sign}\", \"{amount}\", \"{description}\")"

  try: 
    cursor.execute(sql)
    db.commit()
  except Exception as e:
    print(e)
    entry = "INSERT INTO logs(" + (", ".join([timestamp, source, target, type, sign, amount, description])) + ")"
    print(f"Failed to record logs for this entry: {entry}")

def get_logs(id_to_search):

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

    for r in ret:
      sign = "+" if r['Sign'] == "Positive" else "-"
      
      time = r['Timestamp'].strftime('%d-%m-%Y')
      # num = sign + str(r['Amount'])
      to_add = f"` {time} `\t—\t` {sign}{r['Amount']:<2} `\t*{r['Description']}*\n"

      if len(to_add) + size > field_content_limit:
        res.append("") 
        size = 0

      res[-1] += to_add 
      size += len(to_add)
    
    # if len(res) == 0:
    #   await ctx.send(f"<@!{id_author}>, no logs found for ***{mem.name}*** !")
    # else:
    #   await ctx.send(res)
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

def get_word_info(word):
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
    