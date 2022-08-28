from discord.ext import commands, tasks
from loops import HOUR
from datetime import datetime, timedelta
import asyncio
from utils import *
from env import *
from russian_names import RussianNames

class Business(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.rename_purchase_queue.start()
  

  @tasks.loop(seconds=HOUR)
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
  async def check_money(self, ctx):
      
    amount = get_money(ctx.author.id)  
    
    if not amount:
      await respond(ctx, RESPONSES["mistake"])

    await ctx.send(f"{mention_author(ctx)}, на вашем счету {amount} {get_money_str(amount)}!")

  # TODO add option to list channel IDS that you want to rename 
  @commands.command(name="rename")
  async def rename(self, ctx, lang):
     
    # Check that language is valid 
    if lang.lower() not in LANGUAGE_CODES and lang.lower() != "random":
      await respond(ctx, f"языка под названием *\"{lang}\"* не существует в базе сервиса Google translate! \n\n` !langs ` чтобы посмотреть все доступные варианты.")
      return

    res = await pay_up(self.bot, ctx, "rename")
    if not res:
      return
    
    now = datetime.datetime.now()
    rows = get_rows_custom("SELECT * from fn_effects_queue WHERE Type=\"Rename\"")
    
    chid, aid, adn, avu = str(ctx.channel.id), str(ctx.author.id), str(ctx.author.display_name), str(ctx.author.avatar_url)
    pklctx = PickleContext(chid, aid, adn, avu)

    if not rows:
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

      await respond(ctx, f"придётся подождать, перед вами {len(rows)} {get_humans_str(len(rows))}! Ваш запрос будет удовлетворён через {due_str}.")
      purchase_id = record_purchase(ctx.author.id, GUILD, now, "Rename", lang, PRICES["rename"], "Hanging")
      insert_row("fn_effects_queue", fields=["Purchase", "Type", "Due"], values=[purchase_id, "Rename", curr_due])

    # Saving necessary context data for the row when it will be executed in the future (channel id, original author information etc.)
    purchase_to_context = load_pickle("purchase_to_context.pkl")
    purchase_to_context[int(purchase_id)] = (chid, aid, adn, avu)
    save_pickle(purchase_to_context, "purchase_to_context.pkl")
 
  @commands.command(name="waifu")
  async def random_waifu(self, ctx):

    # check waifu limit

    res = await pay_up(self.bot, ctx, "waifu")
    if not res:
      return

    # await respond(ctx, "")

    url = f"http://albenz.xyz:6969/waifu_file"
    response = requests.get(url)
    response = response.json()
    if "file" not in response:
      await respond(ctx, RESPONSES["mistake"])
    
    filename = response["file"]
    url = f"http://albenz.xyz:6969/waifu_jpg?file={filename}"
    name = str(RussianNames(count=1, transliterate=False, patronymic=False, surname=False, gender=0.0).get_batch()[0])
    now = datetime.datetime.now()
    item_id = ctx.message.id
    purchase_id = record_purchase(ctx.author.id, GUILD, now, "Waifu", item_id, PRICES["waifu"], "Finished")
    update_basket(ctx.author.id, item_id, 'Waifu', {"image-url": url, "name": name})
    embed = get_waifu_embed(name, url, item_id)
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Business(bot))

class PickleContext:
  def __init__(self, channel_id, author_id, display_name, avatar_url):
    self.channel_id = channel_id
    self.author_id = author_id
    self.display_name = display_name
    self.avatar_url = avatar_url

