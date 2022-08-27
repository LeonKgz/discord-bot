from discord.ext import commands, tasks
from loops import HOUR
from datetime import datetime, timedelta
import asyncio
from utils import *
from env import *

class Business(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.rename_purchase_queue.start()
  

  @tasks.loop(seconds=60.0)
  async def rename_purchase_queue(self):
    period, units, unitstr = EFFECTS["rename"]
    now = datetime.datetime.now()
    nowstr = "\'" + now.strftime('%Y-%m-%d %H:%M:%S') + "\'"
    expiring_row = get_rows_custom(f"SELECT * from fn_effects_queue WHERE Type=\"Rename\" AND DATE_ADD(Due, INTERVAL {period-1} {unitstr}) < {nowstr};")
    # expiring_row = get_rows_custom(f"SELECT * from fn_effects_queue WHERE Type=\"Rename\" AND DATE_ADD(Due, INTERVAL {period-1} MINUTE) < {nowstr};")
    interval = period * units

    if expiring_row:
      expires_at = expiring_row[0]['Due'] + timedelta(seconds=interval)
    
    incoming_row = get_rows_custom(f"SELECT * from fn_effects_queue WHERE Type=\"Rename\" AND Due > {nowstr} AND Due < DATE_ADD({nowstr}, INTERVAL 1 {unitstr});")
    # incoming_row = get_rows_custom(f"SELECT * from fn_effects_queue WHERE Type=\"Rename\" AND Due > {nowstr} AND Due < DATE_ADD({nowstr}, INTERVAL 1 MINUTE);")
    if incoming_row:
      incomes_at = incoming_row[0]['Due']

    if expiring_row and incoming_row:
      await asyncio.sleep((expires_at - now).seconds)
    elif incoming_row:
      await asyncio.sleep((incomes_at - now).seconds)

    filename = "purchase_to_context.pkl"
    if expiring_row:
      execute_custom(f"DELETE FROM fn_effects_queue WHERE ID={expiring_row[0]['ID']}")

      row = get_db_row("fn_purchase", expiring_row[0]['Purchase'])
      if not row:
        return 

      purchase_to_context = load_pickle(filename)
      del purchase_to_context[int(expiring_row[0]['Purchase'])] 
      save_pickle(purchase_to_context, filename)

    if incoming_row:

      # No need to save pickle afterwards since we did not write to it
      purchase_to_context = load_pickle(filename)
      chid, aid, adn, avu = purchase_to_context[incoming_row[0]['Purchase']]
      
      # Retrieving necessary context data after the period of time has passed
      pklctx = PickleContext(chid, aid, adn, avu)

      row = get_db_row("fn_purchase", incoming_row[0]['Purchase'])
      if not row:
        return 

      await rename_all_channels(self.bot, pklctx, row['Item'])
      update_db_entry("fn_purchase", "Status", "Finished", incoming_row[0]['Purchase'])

  @commands.command(name="langs")
  async def get_all_languages(self, ctx):

    ret = ", ".join([s.title() for s in LANGUAGE_CODES.keys()])
    await respond(ctx, "вот все доступные языки: " + ret + ", Random.")
    pass

  @commands.command(name="баланс")
  async def check_money(ctx):
    row = get_db_row("raiting", str(ctx.author.id))
    
    if not row:
      await ctx.send(f"{mention_author(ctx)}, произошла ошибка! Обратитесь к Албанцу.")
      return

    amount = row["Money"]   
    await ctx.send(f"{mention_author(ctx)}, на вашем счету {amount} {get_money_str(amount)}!")

  # TODO add option to list channel IDS that you want to rename 
  @commands.command(name="rename")
  async def rename(self, ctx, lang):
    msg = await respond(ctx, "секунду...")
    # Check if user has money
    row = get_db_row("raiting", ctx.author.id)
    if not row:
      await respond(ctx, "произошла ошибка! Обратитесь к Албанцу.")
      return
    
    balance = row["Money"]
    price = PRICES["rename"]
    manifesto = get_channel_by_name(self.bot, "манифест", 'Russian')
    if balance < price:
      await msg.delete()
      await respond(ctx, f"у вас недостаточно средств! Стоимость услуги — ` {price} `; на вашем счету — ` {balance} `.\nСмотрите, как зарабатывать очки в {manifesto.mention}")
      return

    # Check that language is valid 
    if lang.lower() not in LANGUAGE_CODES and lang.lower() != "random":
      await msg.delete()
      await respond(ctx, f"языка под названием *\"{lang}\"* не существует в базе сервиса Google translate! \n\n` !langs ` чтобы посмотреть все доступные варианты.")
      return
    
    # Check in the queue of purchased server effects with the 6 hour period if no others, then simply rename, otherwise, submit in the queue
    # SCHEMA
    # list all rows with the same type (all Renames would have Period '6' and Units 'HOURS')
    # order rows in the order of ID (AUTOINCREMENT) earliest would come FIRST
    
    # need to tell user when his request will be executed
    # need to get the last row get its timetstamp and just add the effect length

    remove_balance(ctx.author.id, PRICES["rename"])

    now = datetime.datetime.now()
    rows = get_rows_custom("SELECT * from fn_effects_queue WHERE Type=\"Rename\"")
    
    chid, aid, adn, avu = str(ctx.channel.id), str(ctx.author.id), str(ctx.author.display_name), str(ctx.author.avatar_url)
    pklctx = PickleContext(chid, aid, adn, avu)

    if not rows:
      await msg.delete()
      purchase_id = record_purchase(ctx.author.id, GUILD, now, "Rename", lang, PRICES["rename"], "Finished")
      insert_row("fn_effects_queue", fields=["Purchase", "Type", "Due"], values=[purchase_id, "Rename", now])
      await respond(ctx, "вы первый в очереди! Ваш запрос будет удовлетворён незамедлительно!")
      await rename_all_channels(self.bot, pklctx, lang)

    else:
      last_due = rows[-1]["Due"]
      period, unit, unitstr = EFFECTS["rename"]
      period = period * unit

      # Conersion to and from datetime and timestamp in mysql
      curr_due = last_due + timedelta(seconds=period)
      difference = curr_due - now
      hour = int(difference.seconds // HOUR)
      minute = int((difference.seconds % HOUR) // MINUTE)

      due_str = ""
      if hour:
        due_str += str(hour) + " " + get_str_hour(hour)
        
      if minute:
        due_str += (" " if hour else "") + str(minute) + " " + get_str_minute(minute)

      await msg.delete()
      await respond(ctx, f"придётся подождать, перед вами {len(rows)} {get_humans_str(len(rows))}! Ваш запрос будет удовлетворён через {due_str}.")
      purchase_id = record_purchase(ctx.author.id, GUILD, now, "Rename", lang, PRICES["rename"], "Hanging")
      insert_row("fn_effects_queue", fields=["Purchase", "Type", "Due"], values=[purchase_id, "Rename", curr_due])

    # Saving necessary context data for the row when it will be executed in the future (channel id, original author information etc.)
    purchase_to_context = load_pickle("purchase_to_context.pkl")
    purchase_to_context[int(purchase_id)] = (chid, aid, adn, avu)
    save_pickle(purchase_to_context, "purchase_to_context.pkl")

def setup(bot):
  bot.add_cog(Business(bot))

class PickleContext:
  def __init__(self, channel_id, author_id, display_name, avatar_url):
    self.channel_id = channel_id
    self.author_id = author_id
    self.display_name = display_name
    self.avatar_url = avatar_url

