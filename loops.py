import discord
import os
from discord.ext import commands, tasks
import pymysql.cursors
import datetime
import wikipediaapi
import random
import requests
from utils import *

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))

SECOND = 1.0
HOUR = 3600.0
DAY = 86400.0

class Loops(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    # self.news_alert.start()
    # self.scan.start()
    # self.important_info.start()
    self.change_channel_name.start()
    ## self.deaths.start()
    ## self.births.start()
    # self.meditations.start()
  
  # def get_db_cursor(self):

  #   HOST = "45.32.178.186"
  #   USER = "root"
  #   PASSWORD = "chechera7220"
  #   db = pymysql.connect(host=HOST,
	# 											 user=USER,
	# 											 password=PASSWORD,
	# 											 db=DB,
	# 											 charset='utf8mb4',
	# 											 cursorclass=pymysql.cursors.DictCursor)
  #   return db, db.cursor()

  def get_channel(self, guild, name):
    for ch in guild.channels:
      if name in ch.name:
        return ch
    return False
  
  def get_channel_by_id(self, guild, id):
    for ch in guild.channels:
      if id == str(ch.id):
        return ch
    return False

  @tasks.loop(seconds=10.0)
  async def change_channel_name(self):

    # db, cursor = get_db_cursor()
    # sql = "SHOW COLUMNS FROM tmg_channels"
    # try:
    #   cursor.execute(sql)
    #   res = cursor.fetchall()
    #   # list of available language options (effectively list of column names from the tbg_channels table minus the first one which is 'ID')
    #   langs = [r['Field'] for r in res][1:]
    # except Exception as e:
    #   print(e)
    #   db.rollback()

    guild = self.bot.get_guild(GUILD)

    if guild:

      for ch in guild.channels:
        # change name to russian version
        row = get_db_row("tmg_channels", str(ch.id))
        if not row:
          print(f"{ch.name} was not found!")
          continue
        russian = row["Russian"]
        prefix = row['Prefix']
        res = prefix + russian 
        await ch.edit(name=res)
        print(f"{ch.name} successfully renamed!")

      print("DOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONE")
      # colnames = ", ".join(langs)
      # for ch in guild.channels:
      #   if str(ch.id) == "858331607398875156":
      #     name = ch.name[:-1].encode('utf-8')
      #     pre = ch.name[-1]
      #     sql = f"INSERT INTO tmg_channels(ID, {colnames}) VALUES(\"{ch.id}\", \"{pre}\", \"n\", \"{name}\", \"n\")"
      #     # sql = f"UPDATE tmg_channels SET Prefix = \"{pre}\" WHERE ID = \"{ch.id}\""
      #     try:
      #       cursor.execute(sql)
      #       db.commit()
      #     except Exception as e:
      #       db.rollback()

      # db.close()
      # print("DONE")
      # return 

      # db, cursor = get_db_cursor()
      # the next line only makes sense when first executed 
      # (if executed after the channel is renamed, pointless, TODO account for that later in the actual implementation)
      # ch = self.get_channel_by_id(guild, "974068379356913724")
      # a list of languages get from the database potentially once in a while and keep as a pickle?
      

      # implement the counter via the database as usual i.e. verses

      # with open("counter.txt", 'r') as f:
      #   data = f.read()
      #   if not data:
      #     counter = 0
      #   else:
      #     counter = int(data)

      #   # this implementation is for a particular test channel, thats where the magic number comes from
      #   # newname = langs[languages[counter]]
      #   newname = get_db_row("tmg_channels", "974068379356913724")[languages[counter]]
      # with open("counter.txt", 'w') as f:
      #   towrite = (counter + 1) % len(languages)
      #   f.write(str(towrite))

      # await ch.edit(name=newname)
      # await ch.send(f"Renamed to {newname}!")


  @tasks.loop(seconds=HOUR)
  async def news_alert(self):
    guild = self.bot.get_guild(GUILD) 
    db, cursor = self.get_db_cursor()

    hour = int(datetime.datetime.now().hour)

    if (guild and hour == 12):

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

      limit = counter

      try:
        sql = f"SELECT * FROM counters WHERE ID = \"timers\""
        cursor.execute(sql)
        counter = int(cursor.fetchone()['Value'])
        current_offset = counter
        counter += 1
        if (counter > limit - 1):
          counter = 0
      except Exception as e:
        print(e)
        db.rollback()
        return

      db, cursor = self.get_db_cursor()
      try:
        sql = f"REPLACE INTO counters(ID, Value) VALUES(\"timers\", {counter})"
        cursor.execute(sql)
        db.commit()

      except Exception as e:
        print(e)
        db.rollback()
        return

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

      ch = self.get_channel(guild, "погран-застава")
      await ch.send(f"{content}")     

  @tasks.loop(seconds=DAY)
  async def scan(self):

    db, cursor = self.get_db_cursor()
    guild = self.bot.get_guild(GUILD) 
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
        sovok = self.bot.get_user(int(sovok))
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
    #      await m.add_roles(politzek)
    #      await m.remove_roles(proletariat)

      except Exception as e:
        db.rollback()
        print(e)

      try:      
        db.close()
      except:
        print("Already closed")

      print("DONE NOW")

  @tasks.loop(seconds=HOUR)
  async def important_info(self):

    guild = self.bot.get_guild(GUILD) 
    
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
      
      ch = self.get_channel(guild, "погран")
      row = get_db_row("confessions", m.id)

      if row:
        confession = row["Confession"]
        res = f"Товарищи! А знали ли вы что-нибудь о {m.name}? Вот что {m.name} говорит о себе: \n\n\t*{confession}*\n\nНе забывайте, что можно обновить своё описание (« **!рассказать** ») максимум один раз в 7 дней."
        await ch.send(res)
 
  @tasks.loop(seconds=HOUR)
  async def deaths(self):

    hour = int(datetime.datetime.now().hour)
    guild = self.bot.get_guild(GUILD)

    if hour == 9 and guild:

      wiki_wiki = wikipediaapi.Wikipedia('en')

      today = datetime.datetime.now()
      month = today.strftime("%B")
      day = today.day

      page = wiki_wiki.page(f'{day} {month}')
      deaths = page.text.split("Deaths")[1].split("Holidays")[0].split("\n")
      found_valid_page = False
      
      while not found_valid_page:
        case = deaths[random.randint(0, len(deaths) - 1)]
        
        try:
          case = case.split("–")[1].split(",")[0]
        except Exception as e:
          continue
        
        page = wiki_wiki.page(f'{case}')
        #print([str(s.title) for s in page.sections])
        found_valid_page = "Death" in [str(s.title) for s in page.sections]


        if (found_valid_page):
          ss = [s.title for s in page.sections]
          idx = ss.index('Death')
          section = page.sections[idx]
          content = f"**— {day} {month} —**\n\n\t**{page.title}**\n\n\t - {page.summary}\n\n\t - *{section.text}*\n\n**—**"
          found_valid_page = len(content) <= 2000
        
      guild = self.bot.get_guild(GUILD)
      if (guild):
        for ch in guild.channels:
          if ("өлүм" in ch.name):
            await ch.send(f"**— {day} {month} —**\n\n\t**{page.title}**\n\n\t - {page.summary}\n\n\t - *{section.text}*\n\n**—**")

  @tasks.loop(seconds=HOUR)
  async def births(self):

    hour = int(datetime.datetime.now().hour)
    guild = self.bot.get_guild(GUILD)

    if hour == 9 and guild:

      wiki_wiki = wikipediaapi.Wikipedia('en')

      today = datetime.datetime.now()
      month = today.strftime("%B")
      day = today.day

      page = wiki_wiki.page(f'{day} {month}')
      deaths = page.text.split("Births")[1].split("Holidays")[0].split("\n")
      found_valid_page = False
      
      while not found_valid_page:
        case = deaths[random.randint(0, len(deaths) - 1)]
        
        try:
          case = case.split("–")[1].split(",")[0]
        except Exception as e:
          continue
        
        page = wiki_wiki.page(f'{case}')
        #print([str(s.title) for s in page.sections])
        # TODO some pages have 'Early life and education' or something similar. Add an extension to accomodate these

        if ("Early life" in [str(s.title) for s in page.sections]):
          ss = [s.title for s in page.sections]
          idx = ss.index('Early life')
          section = page.sections[idx]
          content = f"**— {day} {month} —**\n\n\t**{page.title}**\n\n\t - {page.summary}\n\n\t - *{section.text}*\n\n**—**"
          found_valid_page = len(content) <= 2000
          
      guild = self.bot.get_guild(GUILD)
      if (guild):
        for ch in guild.channels:
          if ("туулган" in ch.name):
            await ch.send(f"**— {day} {month} —**\n\n\t**{page.title}**\n\n\t - {page.summary}\n\n\t - *{section.text}*\n\n**—**")

  @tasks.loop(seconds=HOUR)
  async def meditations(self):

    hour = int(datetime.datetime.now().hour)
    guild = self.bot.get_guild(GUILD)
    if hour == 9 and guild:

      channel = self.get_channel(guild, "meditations")
      url = f"http://albenz.xyz:6969/remedy?issue=Random"

      response = requests.get(url)

      data = response.json()
    
      try:
        await parse_zettel_json(channel, data)

      except Exception as e:
        await channel.send(f"Произошла ошибка вызова API")

def setup(bot):
  bot.add_cog(Loops(bot))















####################### MISC #############################


# @tasks.loop(seconds=5.0)
# async def looop():
#     guild = bot.get_guild(GUILD) 
#     if (guild):
#         for ch in guild.channels:
#             if ("технический" in ch.name):
                       
#                 url = 'https://quotes.rest/quote/random.json?maxlength=150'
#                 api_token = QUOTES
#                 headers = {'content-type': 'application/json',
#                                'X-TheySaidSo-Api-Secret': format(api_token)}

#                 response = requests.get(url, headers=headers)
#                 response = response.json()['contents']['quotes'][0]

#                 quote = response['quote']
#                 author = response['author']
#                 text = quote + " — " + author
#                 await ch.send(text)

# def linkFetch():
#     key = FOOD_KEY
#     url = f"https://api.unsplash.com/photos/random/?query=meal&client_id={key}"

#     response = requests.get(url)
#     data = response.json()["urls"]["raw"]
#     return data

# @tasks.loop(seconds=3600.0)
# async def breakfast():

#   guild = bot.get_guild(GUILD) 
  
#   hour = int(datetime.datetime.now().hour)
#   if (guild and hour == 5):

#     proletariat = discord.utils.get(guild.roles, name='Пролетарий')
#     politzek= discord.utils.get(guild.roles, name='Политзаключённый')

#     for ch in guild.channels:
#       if ("колхоз" in ch.name):
#         url = linkFetch()
#         res = f"{politzek.mention}! Завтрак! \n\n {url}"
#         res = f"Завтрак! \n\n {url}"
#         await ch.send(res)

# @tasks.loop(seconds=3600.0)
# async def dinner():

#   guild = bot.get_guild(GUILD) 
  
#   hour = int(datetime.datetime.now().hour)
  
#   if (guild and hour == 15):

#     proletariat = discord.utils.get(guild.roles, name='Пролетарий')
#     politzek= discord.utils.get(guild.roles, name='Политзаключённый')

#     for ch in guild.channels:
#       if ("колхоз" in ch.name):
#         url = linkFetch()
#         res = f"{politzek.mention}! Ужин! \n\n {url}"
#         res = f"Ужин! \n\n {url}"
#         await ch.send(res)

# @tasks.loop(seconds=3600.0)
# async def lunch():

#   guild = bot.get_guild(GUILD) 
  
#   hour = int(datetime.datetime.now().hour)
#   if (guild and hour == 10):

#     proletariat = discord.utils.get(guild.roles, name='Пролетарий')
#     politzek= discord.utils.get(guild.roles, name='Политзаключённый')

#     for ch in guild.channels:
#       if ("колхоз" in ch.name):
#         url = linkFetch()
#         res = f"{politzek.mention}! Обед! \n\n {url}"
#         res = f"Обед! \n\n {url}"
#         await ch.send(res)