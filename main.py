#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import asyncio
from http.client import REQUEST_URI_TOO_LONG
import os
import discord
from discord.ext import commands
from discord.utils import get as du_get
import json
import requests
import secrets
import datetime
from requests import get
from utils import *
import numpy as np
# test comment

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))
ME = int(os.getenv('ME'))
MANASCHI = int(os.getenv('MANASCHI'))

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
QUOTES = str(os.getenv('QUOTES_KEY'))
FOOD_KEY = str(os.getenv('FOOD_KEY'))

seneca_api = str(os.getenv('SENECA_API_TOKEN'))

global_languages_dictionary = {
  "remedies": "en",
  "remedy": "en",
  "средства": "ru",
  "средство": "ru",
  "prayer": "en",
  "молитва": "ru",
}

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix=["!", "！"])
#bot.timer_manager = timers.TimerManager(bot)

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="st")
async def st(ctx, status):
  user = bot.get_user(249503118885257216)
  activity = discord.Game(name="Netflix", type=3)

  proletariat = discord.utils.get(ctx.guild.roles, name='Апатрид')
  for m in proletariat.members:
    if (str(m.id) == str(249503118885257216)):
      await m.change_presence(status=discord.Status.dle, activity=activity)

  await ctx.send("Done!")

@bot.command(name="bible")
async def bible(ctx, *, args=None):
  args = str(args)  
  args = args.split(" ")
  passage = args[1]
  version = args[0]
  #numbers = ",%20".join(args[1:])
  numbers = ";".join(args[2:])

  url = f"https://getbible.net/json?passage={passage}%20{numbers}&version={version}"

  response = requests.get(url)
  try: #try parsing to dict
    dataform = str(response.text).strip("'<>() ").replace('\'', '\"')
  #  print(dataform[:-2])
    dataform = dataform[:-2]
    struct = json.loads(dataform)
    
    if (struct["type"] == "verse"):
      name = struct["book"][0]["book_name"]

      ret = f"{name}"
      curr_chapter = "None"

      for b in struct["book"]:
        chapter = b["chapter_nr"]
        if (curr_chapter != chapter):
          ret += "\n"
        curr_chapter = chapter
        
        for key in list(b["chapter"].keys()):
          verse = key
          content = b["chapter"][key]["verse"]
          ret += f"\t{chapter}:{verse}\t{content}"

      await ctx.channel.send(f"{ret}")
    elif struct["type"] == "chapter":
      name = struct["book_name"]

      rets = [f"{name}"]
      total_size = len(rets[0])

      chapter = struct["chapter_nr"]
      for key in list(struct["chapter"].keys()):
        verse = key
        content = struct["chapter"][key]["verse"]

        size = len(f"\t{chapter}:{verse}\t{content}")

        if total_size + size >= 2000:
          total_size = 0
          rets.append("") 

        total_size += size

        rets[-1] += f"\t{chapter}:{verse}\t{content}"
      
      for r in rets: 
        print(len(r))
        await ctx.channel.send(f"{r}")

  except Exception as e:
    print(e)

# Command to connect a telegram account
@bot.command(name="telegram")
async def ebmed(ctx):
  if ctx.guild:
    try:
      msg_id = ctx.message.id
      await ctx.message.delete()
      await ctx.send(f"<@!{ctx.author.id}>, эту команду можно написать только в личку боту!")
      return
    except Exception as e: 
      print(e)
  
  iid = ctx.author.id

  # First check if an account is already registered
  row = get_db_row("telegram_integration", iid)
  if row:
    await ctx.send(f"<@!{ctx.author.id}>, к вашему дискорду уже привязан телеграм аккаунт!")
    return

  # mem = bot.get_user(id_to_search)
  # iid = mem.id
  
  auth_code = str(secrets.token_hex(16))

  db, cursor = get_db_cursor()
  # For now it's okay if an entry already exists in the cache. 
  # This means that the previous code was redeemed yet.
  # Potentially this accomodates for users who got a new telegram account.
  replace = f"REPLACE INTO telegram_registration(ID, Discord_User_ID) VALUES(\"{auth_code}\", \"{iid}\")"

  try:
    cursor.execute(replace)
    db.commit()
  except Exception as e:
    print(e)
    db.rollback()
    await ctx.send(f"Произошла ошибка! ` {e} `")
    return

  await ctx.send(f"Ваш токен: ` {auth_code} `\nОтправьте его боту в телеграме (https://t.me/seneca69_bot) в личном сообщении таким образом: \n\n\t\t\t` !discord {auth_code} `\n\nТокеном можно воспользоваться только один раз!")

@bot.command(name="file")
async def ebmed(ctx, user):

  if ctx.guild:
    try:
      holder = int(user)
      msg_id = ctx.message.id
      await ctx.message.delete()
      return
    except Exception as e: 
      print(e)
  
  id_to_search = get_id(user)
  mem = bot.get_user(id_to_search)
  embed = get_file(bot, mem)
  await ctx.send(embed=embed)

async def weekly_activity_notification(id_to_search):
  # print(bot.get_user(id_to_search.bot))
  if str(id_to_search) == str(ME) or str(id_to_search) == str(MANASCHI) or bot.get_user(id_to_search).bot:
    print("Tis the owner or the music bot!")
    return

  mem = bot.get_user(id_to_search)
  embed = discord.Embed(title=f"+15 Кремлебот") 
  embed.set_author(name=mem.display_name, icon_url=mem.avatar_url)
  embed.set_thumbnail(url="https://thumbs.gfycat.com/CoordinatedBareAgouti-max-1mb.gif")
  # light green, same as СовНарМод
  embed.color = 0x2ecc71
  embed.add_field(name="⠀", value=f"{mem.display_name} зарабатывает очко оставаясь активным!", inline=False)

  db, cursor = get_db_cursor()
  sql = f"SET @row_number = 0; SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC"

  guild = bot.get_guild(GUILD)
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
    
    ch = get_channel_by_name(bot, "технический", 'Russian')
    # for ch in guild.channels:
    #   if ("технический" in ch.name):
    await ch.send(f"Cant display activity log for **{mem.display_name}** !")
    return 

  db.close()

  embed.set_footer(text="Смотрите как зарабатывать очки в Манифесте")
  main_field = f"⠀\nСоциальный Рейтинг — *{points} ( {num}-е место )*"
  embed.add_field(name=main_field, value="⠀", inline=False)

  ch = get_channel_by_name(bot, "гласность", 'Russian')
  await ch.send(embed=embed)

async def telegram_registration_notification(id_to_search):
  # if str(id_to_search) == str(ME) or str(id_to_search) == str(MANASCHI):
  #   print("Tis the owner or the music bot!")
  #   return

  mem = bot.get_user(int(id_to_search))
  embed = discord.Embed(title=f"Роскомнадзор хочет знать ваше местоположение") 
  embed.set_author(name=mem.display_name, icon_url=mem.avatar_url)
  embed.set_thumbnail(url="https://sun9-19.userapi.com/s/v1/if1/dFyFjrD1QetbjHomAaHQvt_SxGIOuuykqptAyKBFVIzyZ8p07QXbB2Lp22_1-JkFm2Xcj_7A.jpg?size=200x200&quality=96&crop=47,0,764,764&ava=1")
  # light green, same as СовНарМод
  embed.color = 0x039be5
  embed.add_field(name="⠀", value=f"{mem.display_name} зарабатывает очки подключив телеграм!\n(Удобная альтернатива рассылке в дискорде)", inline=False)

  db, cursor = get_db_cursor()
  sql = f"SET @row_number = 0; SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC"

  guild = bot.get_guild(GUILD)
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

    ch = get_channel_by_name(bot, "технический", 'Russian')
    await ch.send(f"Cant display activity log for **{mem.display_name}** !")
    return 

  db.close()

  embed.set_footer(text="Смотрите как зарабатывать очки в Манифесте")
  main_field = f"⠀\nСоциальный Рейтинг — *{points} ( {num}-е место )*"
  embed.add_field(name=main_field, value="⠀", inline=False)

  ch = get_channel_by_name(bot, "гласность", 'Russian')
  await ch.send(embed=embed)

@bot.command(name="манифест")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz/files/tractatus.pdf")

@bot.command(name="сайт")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz")

@bot.command(name="пьесы")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz/plays/allplays/")

@bot.command(name="песни")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.albenz.xyz/songs/allartists/")

@bot.command(name="plays")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.youtube.com/channel/UCdVx_oiTYB8fQdkbYmUPRQQ")

@bot.command(name="songs")
async def website(ctx):
  await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.youtube.com/channel/UCVRzrqkQxWawb-cKz1zXBZQ")

@bot.command(name="долг")
async def duty(ctx, issue):
  url = f"http://albenz.xyz:6969/duty?issue={issue}"
  
  #ret = await ctx.send("*Подождите...*")
  response = requests.get(url)
  response = response.json()
  try:
    await parse_zettel_json(ctx, response)
  except Exception as e:
    print(e)
    await ctx.send(f"<@!{ctx.author.id}>, долг для *«{issue}»* не найден! « !долги », чтобы посмотреть все ключевые слова.")
    
from googletrans import Translator

@bot.command(name='remedy', aliases=['средство'])
async def remedy(ctx, *, args=None):
  translator = Translator()
  issue = args.strip()

  global global_languages_dictionary
  response_options = { 
    "en": {
      "404": f"{mention_author(ctx)}, remedy for *«{issue}»* was not found! « !remedies » to view all available keywords.",
    },
    "ru": {
      "404": f"*{mention_author(ctx)}, средство для *«{issue}»* не найдено! « !средства », чтобы посмотреть все ключевые слова.",
    }
  }

  invoked = ctx.invoked_with
  lang = global_languages_dictionary[invoked]

  url = f"http://albenz.xyz:6969/remedy?issue={issue}"

  response = requests.get(url)
  data = response.json()

  rus_version = data["content"]
  if lang == "en":
    eng_version = translator.translate(rus_version).text
    data["content"] = eng_version

  try:
    await parse_zettel_json(ctx, data)
  except Exception as e:
    await ctx.send(response_options[lang]["404"])

import os 

@bot.command(name='prayer', aliases=['молитва'])
async def prayer(ctx):

  translator = Translator()
  global global_languages_dictionary
  response_options = { 
    "en": {
      "hold": "*Generating your unique prayer...*", 
      "ready": "Done! I recommend printing it.",
    },
    "ru": {
      "hold": "*Генерирую вашу уникальную молитву...*",
      "ready": "Готово! Советую распечатать.",
    }
  }

  invoked = ctx.invoked_with
  lang = global_languages_dictionary[invoked]

  await ctx.channel.send(response_options[lang]["hold"])

  url = f"http://albenz.xyz:6969/prayer"

  response = requests.get(url)
  data = response.json()
  verses = data["verses"] 
  
  if lang == "en":
    for v in verses:
      original = v["content"]
      eng_version = translator.translate(original).text
      v["content"] = eng_version
      v["remedy"] = v["remedy"].split(" - ")[1]
  else:
    for v in verses:
      v["remedy"] = v["remedy"].split(" - ")[0]

  tex = """\documentclass[10pt]{article}
\\usepackage[russian]{babel}
\\usepackage{tgpagella}
\\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.7in]{geometry}
\\usepackage{multicol}
%\\pagenumbering{gobble}
\\setlength{\columnsep}{1cm}

\\begin{document}

\\begin{multicols}{2}""" + "".join(["\\section{" + v["remedy"] + "}" + "\n\n".join(v["content"].split("\n\n")[1:]).replace("  ", " ").strip().replace("\n\n", "\\\\\n\n") for v in verses]) + """

\\end{multicols}

\\end{document}
  """

  filename = "Stoic_prayer_for_" + "_".join(ctx.author.display_name.split())
  with open(f"./{filename}.tex", "w") as f:
    f.write(tex)

  # Necessary set up to install pdf latex  
  # sudo apt-get install texlive-latex-base
  # sudo apt-get install texlive-fonts-recommended
  # sudo apt-get install texlive-fonts-extra
  # sudo apt-get install texlive-latex-extra

  # pdflatex latex_source_name.tex

  # sudo apt-cache search texlive russian
  # sudo apt-get install texlive-lang-cyrillic

  os.system(f"pdflatex {filename}.tex")
  # await ret.delete()
  await ctx.channel.send(response_options[lang]["ready"])
  await ctx.channel.send(file=discord.File(f"{filename}.pdf"))

  os.remove(f"./{filename}.tex")
  os.remove(f"./{filename}.pdf")
  os.remove(f"./{filename}.log")
  os.remove(f"./{filename}.aux")

@bot.command(name="стих")
async def poem(ctx, issue):

  url = f"http://albenz.xyz:6969/poem?issue={issue}"

  response = requests.get(url)
  data = response.json()
  
  try:
    await parse_zettel_json(ctx, data)
  except Exception as e:
    await ctx.send(f"<@!{ctx.author.id}>, стих для *«{issue}»* не найдено! « !стихи », чтобы посмотреть все ключевые слова.")

@bot.command(name="стихи")
async def poems(ctx):
  url = f"http://albenz.xyz:6969/poems"

  response = requests.get(url)
  data = response.json()["poems"]

  if not data:
    await ctx.send(f"<@!{ctx.author.id}>, стихи не найдены!")

  ret_str = ", ".join(data)
  await ctx.send(f"*<@!{ctx.author.id}>, вот список ключевых слов: \n\n\t{ret_str}.*")

@bot.command(name="remedies", aliases=['средства'])
async def remedies(ctx):
  global global_languages_dictionary
  response_options = { 
    "en": {
      "404": f"*{mention_author(ctx)}, remedies not found!*",
      "success": f"*{mention_author(ctx)}, here's the list of keywords: "
    },
    "ru": {
      "404": f"*{mention_author(ctx)}, средства не найдены!",
      "success": f"*{mention_author(ctx)}, вот список ключевых слов: "
    }
  }
  invoked = ctx.invoked_with
  lang = global_languages_dictionary[invoked]

  url = f"http://albenz.xyz:6969/remedies"
  response = requests.get(url)

  data = response.json()["remedies"][lang]
  
  if not data:
    await ctx.send(response_options[lang]["404"])
  
  ret_str = ", ".join(data)
  await ctx.send(response_options[lang]["success"] + f"\n\n\t{ret_str}.*")

@bot.command(name="долги")
async def duties(ctx):
  url = f"http://albenz.xyz:6969/duties"

  response = requests.get(url)
  data = response.json()["duties"]

  if not data:
    await ctx.send(f"<@!{ctx.author.id}>, долги не найдены!")

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

  for mem in ctx.guild.members:
    if (mem.id in actor_ids):
      truppa = discord.utils.get(ctx.guild.roles, name='Драматическая Труппа')
      actor_zapasa = discord.utils.get(ctx.guild.roles, name='Актёр Запаса')
      await mem.add_roles(truppa)
      await mem.remove_roles(actor_zapasa)
      await ctx.send(f"{mem.name} благополучно включён в Драматическую Труппу")
  
import datetime as d
class Actor:
  def __init__(self, name, id, times, descs):
    self.book = {
      "times": [d.datetime(t[0], t[1], t[2], 18) for t in times],
      "id": id,
      "descs": [f"За участив в пьесе {d}" for d in descs]
    }

# async def record_log(ctx, source_id, target_id, type, sign, amount, desc):
@bot.command(name="ab213123213123123213c")
async def record_log(ctx):
  return
  if (not await check_rights(ctx, ['Политбюро ЦКТМГ'])):
    return

  db, cursor = get_db_cursor()
  sql = "SELECT * from confessions"
  try:
    cursor.execute(sql)
    ret = cursor.fetchall()
    for r in ret:
      time = r['Timestamp']
      source_id = ME
      target_id = r['ID']
      type = 'Description'
      sign = 'Positive'
      name = r['Name']
      data = json.loads(r["Points"])
      if (len(data) == 0):
        mean = 0
      else:
        mean = int(np.mean(list(data.values())))

      amount = mean

      disc = "Обновление описания"

      dbb, cursorr = get_db_cursor()
      sql = f"INSERT INTO logs(Timestamp, Source, Target, Type, Sign, Amount, Description) VALUES(\"{time}\", \"{source_id}\", \"{target_id}\", \"{type}\", \"{sign}\", \"{amount}\", \'{disc}\')"

      try:
        cursorr.execute(sql)
        dbb.commit()
      except Exception as e:
        print(e)
        print(f"problem with {name}")
        dbb.rollback()
      dbb.close()

  except Exception as e:
    print(e)
    print('Larger problem')
    db.rollback()
  db.close()

  return

  # time = d.datetime.now()
  # time = d.datetime(2021, 11, 5, 2, 34)
  # time =  d.datetime(2021, 11, 5, 2, 34)
  actor = discord.utils.get(ctx.guild.roles, name="Актёр Запаса")

  source_id = ***REMOVED***
  type = "Play"
  sign = "Positive"
  amount = "10"

  gamlet_date = (2020, 8, 21)
  gamlet_actors = [
    "ellanta", 
    "SlowLadin",
    "Albanec69",
    "kucher",
    "MadDudeUnstoppable"
  ]

  bottom_date = (2020, 9, 5)
  bottom_actors = [
    "Albanec",
    "mrkimster",
    "Ellanta",
    "hitary",
    "kaleeida",
    "kucher",
    "SlowLadin",
    "olya",
    "MadDudeUnstoppable",
    # "nimferna",
  ]

  gore_date = (2020, 9, 22)
  gore_actors = [
    "hitary",
    "MadDudeUnstoppable",
    "SlowLadin",
    "krabick",
    # "nimferna",
    "ellanta",
    "ramona",
    "kalaboque",
    "Albanec",
    "vccttu"
  ]

  maskarad_date = (2020, 10, 2)
  maskarad_actors = [
    "SlowLadin",
    "Albanec",
    "MadDudeUnstoppable",
    "Ellanta",
    "Фролов",
    "1Torba",
    "NickSEX",
    "kaleeida",
    "Unuasha",
    "KoItsy",
    # "Nimferna",
    "MrHarper",
  ]

  sisters_date = (2020, 10, 18)
  sisters_actors = [
    "NickSEX",
    "hitary",
    "Cockenz",
    "Albanec69",
    "sosaaaaaaaad",
    "Фролов",
    "kaleeida",
    "SlowLadin",
    "MrHarper",
    "Dude",
    "Kalaboque",
  ]

  dom_date = (2020, 11, 8)
  dom_actors = [
    "Unuasha",
    "SleXy",
    "Albanec69",
    "1Torba",
    "Dude",
    "NickSEX",
    "Shizov",
    "Hyomushka",
    "SlowLadin",
    "sosaaaaaaaad",
    "Фролов",
  ]
  
  eugene_date = (2020, 11, 20)
  eugene_actors = [
    "Alice_Nespit",
    "Albanec69",
    "1Torba",
    "SlowLadin",
    "Hitary",
    "MrHarper",
    "NickSEX",
    "Ramona",
    "Ellanta",
  ]
  
  podolsk_date = (2021, 7, 26)
  podolsk_actors = [
    "NickSEX",
    "Psijicus",
    "Albanec69",
    "Фролов",
    "Ellanta",
    "MrKimster",
  ]
  
  rnj_date = (2021, 2, 3)
  rnj_actors = [
    "Ellanta",
    "Funnybone",
    "Albanec69",
  ]
  
  piter_date = (2021, 8, 1)
  piter_actors = [
    "Albanec",
    "Hitary",
    "Ellanta",
    "SleXy",
    "sosaaaaaaaad",
    "мякушка",
    "SlowLadin",
  ]
  
  kaligula_date = (2021, 9, 21)
  kaligula_actors = [
    "Nightingale",
    "Hitary",
    "MrHarper",
    "Фролов",
    "Albanec69",
    "WELOVEWELOVEGAMES",
    "sosaaaaaaaad",
  ]
  
  cherry_date = (2021, 9, 11)
  cherry_actors = [
    "WELOVEWELOVEGAMES",
    "MrHarper",
    "Ellanta",
    "Sekyshka",
    "Kucher",
    "Alice_Nespit",
    "Albanec69",
  ]
  
  bog_date = (2021, 10, 31)
  bog_actors = [
    "Alice_Nespit",
    "WELOVEWELOVEGAMES",
    "Фролов",
    "Unuasha",
    "Albanec69", 
  ]

  godot_date = (2021, 12, 18)
  godot_actors = [
    "Nightingale",
    "Albanec69",
    "Unuasha",
    "TomasX",
    "NickSEX",
    "Фролов",
  ]

  theatre = [
    (gamlet_date, gamlet_actors, "Гамлет"),
    (bottom_date, bottom_actors, "На дне"),
    (gore_date, gore_actors, "Горе от ума"),
    (maskarad_date, maskarad_actors, "Маскарад"),
    (sisters_date, sisters_actors, "Три сестры"),
    (dom_date, dom_actors, "Дом, где разбиваются сердца"),
    (eugene_date, eugene_actors, "Евгений Онегин"),
    (podolsk_date, podolsk_actors, "Человек из Подольска"),
    (rnj_date, rnj_actors, "Ромео и Джульетта"),
    (piter_date, piter_actors, "Жиды города Питера"),
    (kaligula_date, kaligula_actors, "Калигула"),
    (cherry_date, cherry_actors, "Вишнёвый сад"),
    (bog_date, bog_actors, "Бог резни"),
    (godot_date, godot_actors, "В ожидании Годо"),
  ]

  actor_names = []
  actor_ids = {}

  for m in actor.members:
    actor_names.append(m.name)
    actor_ids[m.name] = m.id
    # print(m.name)

  for date, actors, desc in theatre:
    for a in actors:
      for j in actor_names:
        if (a.lower() in j.lower()):
          target_id = actor_ids[j]
          time = d.datetime(date[0], date[1], date[2], 22)
          db, cursor = get_db_cursor()
          # target_id = m.id
          disc = f'Участие в пьесе \"{desc}\"'
          sql = f"INSERT INTO logs(Timestamp, Source, Target, Type, Sign, Amount, Description) VALUES(\"{time}\", \"{source_id}\", \"{target_id}\", \"{type}\", \"{sign}\", \"{amount}\", \'{disc}\')"
          # print(sql)
          try:
            cursor.execute(sql)
            db.commit()
          except Exception as e:
            print(e)
            db.rollback()
          db.close()
          break

    print(f"{disc} is done!")
    print("------------------------------")
34578379852793
@bot.command(name="logs")
async def logs(ctx, mem):

  if ctx.guild:
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
  db, cursor = get_db_cursor()
  sql = f"SELECT * FROM logs WHERE Target = \"{id_to_search}\" ORDER BY Timestamp ASC"
  
  try:

    cursor.execute(sql)
    ret = cursor.fetchall()
    res = ""
    for r in ret:
      sign = "+" if r['Sign'] == "Positive" else "-"
      
      time = r['Timestamp'].strftime('%d-%m-%Y')
      # num = sign + str(r['Amount'])

      res += f"` {time} `\t—\t` {sign}{r['Amount']:<2} `\t*{r['Description']}*\n"
      # res += f"` {time} `\t—\t` {sign}{r['Amount']:<2} `\tпо причине:\t*{r['Description']}*\n"
    
    if len(res) == 0:
      await ctx.send(f"<@!{id_author}>, no logs found for ***{mem.name}*** !")
    else:
      await ctx.send(res)

  except Exception as e:

    print(e)
    db.rollback()

  db.close()




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
      
      row = get_db_row("prisoners", mem_id)
      
      if row:

        # New value to update the entry row 
        imprisonment_cnt = row['Counter'] + 1

        res = row['Status']
        newidx = statuses.index(res) + 1
        if (newidx == len(statuses)):
          newidx = 0
        status = statuses[newidx]
      else:
        status = statuses[0]
        imprisonment_cnt = 1 

      #sql = f"SELECT * from prisoners WHERE ID={mem_id};"

      #try:
      #  cursor.execute(sql)
      #  res = cursor.fetchone()['Status']
      #  newidx = statuses.index(res) + 1
      #  if (newidx == len(statuses)):
      #    newidx = 0
      #  status = statuses[newidx]
      #  
      #except Exception as e:
      #  status = statuses[0]
      
      length = lengths[status]

      guild = bot.get_guild(GUILD) 
      for ch in guild.channels:
        if ("гулаг" in ch.name):
          res = f"Заключённый <@!{mem_id}>! Ваше заключение составит {words[status]}. \nУзнать свой протокол можно с помощью команды « !начальник »"
          await ch.send(res)

      sql = f"REPLACE INTO prisoners(ID, Protocol, Status, Counter) VALUES(\"{mem.id}\", \"{protocol}\", \"{status}\", \"{imprisonment_cnt}\")"
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
            msg = "--------------------------------------------------------------------------\nСообщение от " + str(ctx.author.name) + "!\n\n\t" + text + "\n\n--------------------------------------------------------------------------"
            print(member.id)
            row = get_db_row("telegram_integration", str(member.id))
            if row:
              chat_id = row["Telegram_Chat_ID"]
              msg = msg.replace("*", "")
              msg = msg.replace("`", "")
              request = f"https://api.telegram.org/bot{seneca_api}/sendMessage?chat_id={chat_id}&text={msg}"
              print(request)
              ret = requests.get(request)
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
  russian_name = get_channel_names(bot, str(message.channel.id))["Russian"] if message.guild else ""

  if message.author == bot.user:
  #if message.author == bot.user and "!кто" not in str(message.content):
    return

  me = bot.get_user(ME)
  if (message.author.bot):
    if ('!confirmed_telegram' in message.content):
      iid = message.content.split(" ")[1].strip()
      await add_points_quick(source=me.id, target=iid, amount=5, type='Telegram Integration', description='Подключение телеграм аккаунта')
      await telegram_registration_notification(iid)
    return

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
  elif 'погран' not in russian_name:
  # elif 'погран' not in message.channel.name:
    name = message.author.name
    iid = message.author.id
    time = message.created_at

    db, cursor = get_db_cursor()
    row = get_db_row("cache", iid)
    # Check if this is the first message of the week for someone who wasnt sent to pogran-zastava on that monday; then +1 point
    if not row and (not iid == ME):
      status = await add_points_quick(source=ME, target=iid, type="Activity", amount=1, description="Недельная активность")
      await weekly_activity_notification(iid)
      if not status:
        await message.channel.send(f"<@!{ME}>, произошла ошибка корректировки социального рейтинга для {message.author.name}!")

    sql = f"REPLACE INTO cache(ID, Name, Timestamp) VALUES(\"{iid}\", \"{name}\", \"{time}\")"

    try:
      cursor.execute(sql)
      db.commit()
    except Exception as e:
      print(e)
      db.rollback()

    db.close()
  elif 'технический' in russian_name and message.author.id == 116275390695079945:
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
      await message.channel.send("The guy is free!")

  await bot.process_commands(message)

def get_guild():
  for guild in bot.guilds:
    print(guild.name)
    if (guild.name == GUILD):
      return guild

async def check_rights(ctx, acceptable_roles, tell=True):
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

async def check_rights_dm(ctx):
  super_roles = [214320783357378560, 696405991876722718, ***REMOVED***, 498264068415553537]
  if ctx.author.id in super_roles:
      return True
  response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(du_get(bot.emojis, name='peepoClown'))
  await ctx.send(response)
  return False

def convert_brief(message):
  # REPLACE BAD PRACTISE
  total = 61
  desired_indent = 5
  actual_indent = 0

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
      # 1 point for activity
      await add_points_quick(source=ME, target=iid, type="Activity", amount=1, description="Недельная активность")
      await weekly_activity_notification(iid)
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

# @bot.command(name='19273468236482734627846798326486')
# async def vse(ctx):
#   guild = bot.get_guild(GUILD) 
#   db, cursor = get_db_cursor()
#   proletariat = discord.utils.get(guild.roles, name='Пролетарий')
#   politzek= discord.utils.get(guild.roles, name='Апатрид')
#   npc = discord.utils.get(guild.roles, name='NPC can\'t meme')
#   #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит', 'NPC can\'t meme']
#   ms = []
#   for m in proletariat.members:
    
#     if (npc in m.roles):
#       continue

#     iid = m.id
#     sql = f"SELECT * from confessions WHERE `ID` = \"{iid}\""
#     try:
#      cursor.execute(sql)
#      res = cursor.fetchone()
    
#      if (res is None):
#        ms.append(m)
#        await m.add_roles(politzek)
#        await m.remove_roles(proletariat)       

#     except Exception as e:
#       print(e)

#   ch =    
#   for ch in guild.channels:
#     if ("погранnnn" in ch.name):
#       mentions = ""
#       for m in ms:
#         mentions += f"<@!{m.id}> "
      
#       res = f"Граждане {mentions}! \n\nМы не можем установить вашу личность! Вам нужно зарекомендовать себя! \n\n\t\tЭто можно сделать с помощью команды **« !рассказать »**\n\n\t\t Например: !рассказать \"Привет, я Албанец. Мне 22 года, по образованию программист. Устраиваю читки пьес в дискорде, пытаюсь собрать народ на групповые чтения поэзии и просмотры японских мультиков. В свободное время люблю почитать что-то по философии или религии. Могу сыграть на гитаре твой реквест. В видео-игры не играю. Играю в Го. Энтузиаст Высокой Мошны.\"\n\n\t Не забудьте про **кавычки**! Боту можно написать и в личку. Соответственно рекомендации пользователя можно узнать с помощью команды **« !кто »**, например: !кто @Albanec69 . Учтите, что **записи о себе можно править только один раз в 7 дней!**"
#       await ch.send(res)
#       break

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


      # not adding points yet until all moderators have marked it

      # status1 = await remove_points_quick(id_to_search, prev_mean)
      # status2 = await add_points_quick(source=ME, target=id_to_search, type="Description", amount=curr_mean, description="Обновление описания")
      # status2 = await add_points_quick(id_to_search, curr_mean)

      # if (not(status1 and status2)):
      #   await ctx.send(f"<@!{id_author}>, произошла ошибка корректировки социального рейтинга!")
      #   return
      
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

    ############################################################################################################ 
    embed = discord.Embed(title=f"Модераторы рассмотрели новое описание") 
    embed.set_author(name=mem.display_name, icon_url=mem.avatar_url)

    pepes = [
      "https://cdn.betterttv.net/emote/5d324913ff6ed36801311fd2/3x",
      "https://cdn.betterttv.net/emote/57850b9df1bf2c1003a88644/3x",
      "https://cdn.betterttv.net/emote/59f27b3f4ebd8047f54dee29/3x",
      "https://cdn.betterttv.net/emote/5ec39a9db289582eef76f733/3x",
      "https://cdn.betterttv.net/emote/5aa16eb65d4a424654d7e3e5/3x",
      "https://cdn.betterttv.net/emote/5c0e1a3c6c146e7be4ff5c0c/3x",
      "https://cdn.betterttv.net/emote/5baa5b59f17b9f6ab0f3e84f/3x",
      "https://cdn.betterttv.net/emote/5590b223b344e2c42a9e28e3/3x",
      "https://cdn.betterttv.net/emote/5ec059009af1ea16863b2dec/3x",
      "https://cdn.betterttv.net/emote/58ae8407ff7b7276f8e594f2/2x",
      "https://cdn.betterttv.net/emote/5aea37908f767c42ce1e0293/3x",
    ]

    amount = int(curr_mean)
    
    embed.set_thumbnail(url=pepes[amount])

    if amount == 0 or (amount >= 5 and amount <= 10):
      points_word = "очков"
    elif amount == 1:
      points_word = "очко"
    else:
      points_word = "очка"

    # light green, same as СовНарМод
    embed.color = 0xff0000 
    embed.add_field(name="⠀", value=f"{mem.display_name} зарабатывает **{amount} {points_word}** обновив описание!", inline=False)

    db, cursor = get_db_cursor()
    sql = f"SET @row_number = 0; SELECT (@row_number:=@row_number + 1) AS num, ID, Name, Points FROM raiting ORDER BY Points DESC"

    guild = bot.get_guild(GUILD)
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

      ch = get_channel_by_name(bot, "технический", 'Russian')
      await ch.send(f"Cant display activity log for **{mem.display_name}** !")
      return 

    embed.set_footer(text="Смотрите как зарабатывать очки в Манифесте")
    main_field = f"⠀\nСоциальный Рейтинг — *{points} ( {num}-е место )*"
    embed.add_field(name=main_field, value="⠀", inline=False)
    ############################################################################################################ 
    # If all the mods have marked this user, remove from unmarked_confessions table
    if (len(mods) == 0):
      sql = f"DELETE FROM unmarked_confessions WHERE ID=\"{id_to_search}\""
      ch = get_channel_by_name(bot, "гласность", 'Russian')
      # await ch.send(f"Все Модераторы оценили описание гражданина <@!{mem.id}>!\n\n\t\t Окончательная оценка — **{int(curr_mean)}**\n\n----------------------------------------------------------------------")
      await ch.send(embed=embed)

      # Once all mods marked the description. record the result into logs table and add the points 

      # await remove_points_quick(id_to_search, prev_mean)
      await remove_points_quick(source=ME, target=mem.id, type="Description", amount=prev_mean, description="Корректировка оценки описания")
      await add_points_quick(source=ME, target=mem.id, type="Description", amount=curr_mean, description="Обновление описания")
    
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

@bot.command(name="ppppoppppulpappte")
async def populate_raiting(ctx):
  return
  db, cursor = get_db_cursor()
  sql = "SELECT * FROM confessions"
  try:
    cursor.execute(sql)
    res = [e["ID"] for e in cursor.fetchall()]
  except Exception as e:
    print(e)
    db.rollback()
    return

  for m in ctx.guild.members:
    
    curr= get_db_row("raiting", m.id)
    
    if (curr):
      curr = curr["Points"]
    else:
      print(curr["Name"] + " is missing")
      curr = 0
    bol = "Yes" if m.id in res else "No"
    sql = f"REPLACE INTO raiting(ID, Name, Points, Confession) VALUES(\"{m.id}\", \"{m.name}\", \"{curr}\", \"{bol}\")"

    try:
      cursor.execute(sql)
      db.commit()
    except Exception as e:
      print(e)
      db.rollback()

  db.close()

async def remove_points_quick(source, target, type, amount, description):

  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sign = "Negative"

  try:
      amount = int(amount)

      db, cursor = get_db_cursor()
      row = get_db_row("raiting", target)
      if (not row):
        #return False
        curr = 0
      else:
        curr = row["Points"]

      end = curr - amount
      if (end < 0):
        end = 0

      db, cursor = get_db_cursor()
      sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target}\""

      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return False

      record_logs(timestamp, source, target, type, sign, amount, description)     

      db.close()
  
  except Exception as e:
    print(e)
    return False

  return True

async def add_points_quick(source, target, type, amount, description):
  
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  sign = "Positive"

  try:
      amount = int(amount)

      db, cursor = get_db_cursor()
      row = get_db_row("raiting", target)

      if (not row):
        #return False
        curr = 0
      else:
        curr = row["Points"]

      end = curr + amount

      if (end < 0):
        end = 0

      db, cursor = get_db_cursor()
      sql = f"UPDATE raiting SET Points = \"{end}\" WHERE ID=\"{target}\""

      try:
        cursor.execute(sql)
        db.commit()
      except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return False
      
      record_logs(timestamp, source, target, type, sign, amount, description)     

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

#async def add_points(ctx, target_id, points):
@bot.command(name="add")
async def add_points(ctx, target, type, amount, description):

  source = ctx.author.id

  #if (not await check_rights_dm(ctx)):
  #  return

  #if (ctx.guild):
      #msg_id = ctx.message.id
      #await ctx.message.delete()
      # await ctx.send(f"<@!{ctx.message.author.id}>, ваше сообщение было удалено!")
  #else:

  if (not await check_rights(ctx, ['СовНарМод'])):
    return

  if True:

      try:
        amount = int(amount)
      except Exception as e:
          await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
          return

      if (amount < 1 or amount > 1500):
          await ctx.send(f"<@!{ctx.message.author.id}>, второй аргумент должен быть положительным количеством очков от 0 до 15 включительно!")
          return

      db, cursor = get_db_cursor()
      
      # Check if a group role is mentioned
      if ("<@&" in target):
        send_to = get_id(target)
        for r in ctx.guild.roles:
          if (r.id == send_to):
            every = ", ".join([f"<@!{m.id}>" for m in r.members])
            
            for m in r.members:
              await add_points_quick(source, m.id, type, amount, description)
            
            if amount == 0 or (amount >= 5 and amount <= 10):
              points_word = "очков"
            elif amount == 1:
              points_word = "очко"
            else:
              points_word = "очка"
            
            res = f"Модераторы начисляют **[ {amount} ] {points_word}** социального рейтинга гражданам {every}!\n\n\t\t Причина — *{description}*\n\n----------------------------------------------------------------------"

            guild = bot.get_guild(GUILD)
            ch = get_channel_by_name(bot, "гласность", 'Russian')
            await ch.send(res)
            return

      # Otherwise it's one person
      else:
        row = get_db_row("raiting", target)
        if (not row):
          await ctx.send(f"<@!{ctx.message.author.id}>, произошла ошибка соединения! Попробуйте ещё раз.")

        curr = row["Points"]
        end = curr + amount

        await add_points_quick(source, target, type, amount, description)

        db.close()
        await ctx.send(f"<@!{ctx.message.author.id}>, очки успешно добавлены! Текущий рейтинг - {end}")

        if amount == 0 or (amount >= 5 and amount <= 10):
          points_word = "очков"
        elif amount == 1:
          points_word = "очко"
        else:
          points_word = "очка"

        guild = bot.get_guild(GUILD)
        ch = get_channel_by_name(bot, "гласность", 'Russian')
        member = bot.get_user(get_id(target))
        embed = await get_simple_member_embed(bot=bot, 
                                member=member, 
                                title="За заслуги перед Мошной", 
                                message=f"Модераторы начисляют **{amount} {points_word}** социального рейтинга гражданину {member.display_name} за *{description}*.", 
                                thumbnail_url="", 
                                color_hex_code=0x7621b8)
        await ch.send(embed=embed)

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
      
      # For now dont add points for tellings as they are too easy to write and not serious at this point
      # await add_points_quick(row["Source"], priority)
      # TODO For now don't remove points from the target. 
      #await remove_points_quick(row["Target"], priority)

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


      ch = get_channel_by_name(bot, "гласность", 'Russian')
      user = bot.get_user(row["Target"])
      await ch.send(f"Модераторы рассмотрели донос на гражданина <@!{user.id}>!\n\n\t\t Дело рассмотрено по статье: *{wording1[priority]} — {wording2[priority]}*\n\n\t\t*Материалы дела* — {evidence}\n\n----------------------------------------------------------------------")


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

def get_description(id_to_search):

    db, cursor = get_db_cursor()
    select = f"SELECT * from confessions WHERE ID={id_to_search};"

    try:
      cursor.execute(select)
      confession = cursor.fetchone()['Confession']
      return confession
    except Exception as e:
      print(e)
      db.rollback()
    db.close()

    return False

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

    if (mem.lower() == "я"):

      embed = discord.Embed(title="Я знаю, кто ты...") 
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      embed.color = 0x64B82E
      embed.set_image(url="https://i.imgur.com/aqfPdkJ.gif")
      embed.set_footer(text="Манифест открой...")
      # embed.set_image(url="https://media.discordapp.net/attachments/703737790848040974/969896172149932042/unknown.png")
      await ctx.send(embed=embed)
      return 

    id_author = ctx.author.id
    id_to_search = get_id(mem)
    mem = bot.get_user(id_to_search)
    
    #if (mem is None):
    #  await ctx.send(f"<@!{id_author}>, к сожалению эта команда не работает в мобильном приложении. \nВсе вопросы к дикорду!")
    #  return

    confession = get_description(id_to_search)
    if (confession):
      await ctx.send(f"<@!{id_author}>, вот что {mem.name} говорит о себе: \n\n\t*{confession}*")
    else:
      await ctx.send(f"<@!{id_author}>, пока нам ничего не известно о {mem.name}.")

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

# before starting local bot disconnect remote one
@bot.command(name='jpoff')
async def disconnect_japanese(ctx):
  bot.remove_cog(Nihon(bot))

@bot.command(name='jpon')
async def disconnect_japanese(ctx):
  bot.add_cog(Nihon(bot))

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
    

    #if row:
    #  #points = row["Points"]

    #  if (row["Points"] is None):
    #    data = {}
    #    
    #  else:
    #    data = json.loads(row["Points"])
    #    #data[f"{id_author}"] = points

    #  data = json.dumps(data)
    #  data = data.replace("\"", "\\\"")

    #else:
    #  data = {}
    
    # Not doing the above method anymore when old marks for the older confession are preserved
    # Resetting the marks now so that they are consisten with entries in the unmarked_confession table
    data = {}

    db, cursor = get_db_cursor()

    select = f"SELECT * from confessions WHERE ID={iid};"
    replace = f"REPLACE INTO confessions(ID, Name, Confession, Timestamp, Points) VALUES(\"{iid}\", \"{name}\", \"{confession}\", \"{time}\", \"{data}\")"

    try:
      cursor.execute(select)
      ret = cursor.fetchone()

      # we are getting current mean to save it for the update section of the code below; we are going to subtract curr mean from rating score.
      data = json.loads(ret["Points"])
      vals = list(data.values())

      if len(vals) == 0:
        curr_mean = 0
      else:
        curr_mean = int(np.mean(vals))

      timestamp = ret['Timestamp']
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
					
					
          # add 1 point for activity (can only update descriptio once a week already so cant spam)
          # doesnt matter how bad the descriptino is, this is still activity on sever
          
          if (await check_rights(ctx, ['Апатрид'], tell=False)):
            await add_points_quick(source=ME, target=ctx.author.id, type="Activity", amount=1, description="Недельная активность")
            await weekly_activity_notification(ctx.author.id)

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

    # If description was updated successfully need to reinsert user into the unmarked_confessions table and update Confession status in raiting databse

    if updated:

      # if there are no entries unmarked tables i.e. points for the previous description were already added to the overall score, we need to subtract them now
      row = get_db_row("unmarked_confessions", iid)
      if not row:
        await remove_points_quick(iid, curr_mean)

      update = f"UPDATE raiting SET Confession = \"Yes\" WHERE ID =\"{iid}\""

      try:
        cursor.execute(update)
        db.commit()
      except Exception as e:
        print(e)
        await ctx.send(f"Проблема обновления статуса в raiting!")
        db.rollback()

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
from loops import Loops
from voice import Voice 
from nihon import Nihon

bot.add_cog(Status(bot))
bot.add_cog(Loops(bot))
bot.add_cog(Nihon(bot))
# bot.add_cog(Voice(bot))

bot.run(TOKEN)
