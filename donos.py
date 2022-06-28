from discord.ext import commands
import datetime
from utils import *

GUILD = int(str(os.getenv('DISCORD_GUILD'))) if sys.argv[1] == "prod" else int(str(os.getenv('TEST_DISCORD_GUILD')))

class Donos(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
  
  # @commands.command(name="манифест")
  # async def manifest(self, ctx):
  #   await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz/files/tractatus.pdf")

  @commands.command(name="донести")
  async def donos(self, ctx, *, args=None):
      
      # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
      if (ctx.guild):
        await ctx.message.delete()
        return

      source_id = ctx.author.id
      user = self.bot.get_user(source_id)
      db, cursor = get_db_cursor()
      guild = self.bot.get_guild(GUILD)

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
        
  @commands.command(name="approve")
  async def approve_donos(self, ctx, donos_id, priority, evidence):

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
    guild = self.bot.get_guild(GUILD)

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
        user = self.bot.get_user(row["Target"])
        await ch.send(f"Модераторы рассмотрели донос на гражданина <@!{user.id}>!\n\n\t\t Дело рассмотрено по статье: *{wording1[priority]} — {wording2[priority]}*\n\n\t\t*Материалы дела* — {evidence}\n\n----------------------------------------------------------------------")

      else:
        await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
        return

    else:
      await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
      return

  @commands.command(name="dismiss")
  async def dismiss_donos(self, ctx, donos_id):

    # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
    if (ctx.guild):
      await ctx.message.delete()
      return

    donos_id = int(donos_id)

    db, cursor = get_db_cursor()
    guild = self.bot.get_guild(GUILD)

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

        user = self.bot.get_user(row["Source"])
        await user.create_dm()
        iid = row["ID"]
        await user.dm_channel.send(f"Ваш донос под номером {iid} был отклонён за недостатком улик!")

        # await ch.send(f"Модераторы рассмотрели донос на гражданина **{user.display_name}**!\n\n\t\t Дело рассмотрено по статье: *{wording1[priority]} — {wording2[priority]}*\n\n----------------------------------------------------------------------")

      else:
        await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
        return
    else:
      await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
      return

  @commands.command(name="blacklist")
  async def blacklist_donos(self, ctx, donos_id):
    # If somebody tries to supply ID instead of mentioning a user on one of the server's channels, delete the message
    if (ctx.guild):
      await ctx.message.delete()
      return

    db, cursor = get_db_cursor()
    guild = self.bot.get_guild(GUILD)

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
        user = self.bot.get_user(row["Source"])

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

        user = self.bot.get_user(row["Source"])
        await user.create_dm()
        iid = row["ID"]
        await user.dm_channel.send(f"Ваш донос под номером {iid} был забракован модератором! Вы получаете бан на данную функцию на {7 + strikes} дней. Если вы считаете, что донос был забракован по ошибке, напишите Албанцу в личку.")


      else:
        await ctx.send(f"<@!{ctx.author.id}>, донос уже обработан! Вердикт — {status}")
        return
    else:
      await ctx.send(f"<@!{ctx.author.id}>, такого доноса нет!")
      return
