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

  source_id = 384492518043287555
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

  ch =    
  for ch in guild.channels:
    if ("погранnnn" in ch.name):
      mentions = ""
      for m in ms:
        mentions += f"<@!{m.id}> "
    
      res = f"Граждане {mentions}! \n\nМы не можем установить вашу личность! Вам нужно зарекомендовать себя! \n\n\t\tЭто можно сделать с помощью команды **« !рассказать »**\n\n\t\t Например: !рассказать \"Привет, я Албанец. Мне 22 года, по образованию программист. Устраиваю читки пьес в дискорде, пытаюсь собрать народ на групповые чтения поэзии и просмотры японских мультиков. В свободное время люблю почитать что-то по философии или религии. Могу сыграть на гитаре твой реквест. В видео-игры не играю. Играю в Го. Энтузиаст Высокой Мошны.\"\n\n\t Не забудьте про **кавычки**! Боту можно написать и в личку. Соответственно рекомендации пользователя можно узнать с помощью команды **« !кто »**, например: !кто @Albanec69 . Учтите, что **записи о себе можно править только один раз в 7 дней!**"
      await ch.send(res)
      break

async def populate_raiting(ctx):
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
