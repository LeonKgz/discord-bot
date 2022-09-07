from re import I
from discord.ext import commands, tasks
from loops import HOUR
from datetime import date, datetime, timedelta
import asyncio
from utils import *
from env import *
from russian_names import RussianNames

class Business(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.rename_purchase_queue.start()
    self.check_expired_deals.start()
  
  @tasks.loop(seconds=EFFECTS["rename"][1])
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

      purchase_to_delete = int(expiring_row[0]['Purchase'])
      execute_custom(f"DELETE FROM fn_rename_context WHERE Purchase = \'{purchase_to_delete}\'")
      # purchase_to_context = load_pickle(filename)
      # del purchase_to_context[int(expiring_row[0]['Purchase'])] 
      # save_pickle(purchase_to_context, filename)

    if incoming_row:

      purchase = incoming_row[0]['Purchase']
      row = get_db_row("fn_rename_context", purchase, "Purchase")
      if not row:
        print(f"ERROR: purchase {purchase} not found in fn_rename_context!")
        return

      # purchase_to_context = load_pickle(filename)
      # chid, aid, adn, avu = purchase_to_context[incoming_row[0]['Purchase']]
      chid, aid, adn, avu =  row["Channel"], row["Author"], row["Display_Name"], row["Avatar_Url"]
      
      # Retrieving necessary context data after the period of time has passed
      pklctx = PickleContext(chid, aid, adn, avu)

      row = get_db_row("fn_purchase", incoming_row[0]['Purchase'])
      if not row:
        return 

      await rename_all_channels(self.bot, pklctx, row['Item'])
      update_db_entry("fn_purchase", "Status", "Finished", incoming_row[0]['Purchase'])

  @tasks.loop(seconds=HOUR)
  async def check_expired_deals(self):
    now = datetime.datetime.now()
    rows = get_rows_custom(f"SELECT * FROM fn_market WHERE Status = \'Hanging\'")
    if rows:
      for r in rows:
        if r["Timestamp"] + timedelta(seconds=DAY) < now:
          update_db_entry("fn_market", "Status", "Expired", str(r['ID']))

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

    await ctx.send(f"{mention_author(ctx)}, на вашем счету ` {amount} ` {get_money_str(amount)}!")

  # TODO add option to list channel IDS that you want to rename 
  @commands.command(name="rename")
  async def rename(self, ctx, lang):
     
    # Check that language is valid 
    if lang.lower() not in LANGUAGE_CODES and lang.lower() != "random":
      await respond(ctx, f"языка под названием *\"{lang}\"* не существует в базе сервиса Google translate! \n\n` !langs ` чтобы посмотреть все доступные варианты.")
      return

    res = await pay_up(self.bot, ctx, GUILD, "rename")
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
    # purchase_to_context = load_pickle("purchase_to_context.pkl")
    # purchase_to_context[int(purchase_id)] = (chid, aid, adn, avu)
    # save_pickle(purchase_to_context, "purchase_to_context.pkl")
    insert_row("fn_rename_context", fields=["Purchase", "Channel", "Author", "Display_Name", "Avatar_Url"], values=[int(purchase_id), int(chid), int(aid), adn, avu])
 
  @commands.command(name="sell")
  async def sell(self, ctx, item, price, target):
    # returns embed with the summary of the deal and contract ID. (also display expiry date of the deal (now + timedelta(days=1
    # all deal proposals are posted in glasnost 
    # only the person who initiated the contract can cancel it oif he wishes so
    # the contract is valid for one day only so if the target trie sto acccept the deal and the time passed is over one day, 
    # will not go through, set status to expired! for that also need a loop that updates all statusesof contracts to see them expire
    # price must be within the range 1 <= price <= orinal item price (based on type)

    # first check item is in posession
    source = str(ctx.author.id)
    if not item_in_posession(source, item):
      await respond(ctx, "такого итема нет в вашем инвентаре!")
      return

    rows = get_rows_custom(f"SELECT * FROM fn_market WHERE Item = \'{item}\'")
    if rows:
      old_deal = rows[0]["ID"]
      await respond(ctx, f"итем номер ` {item} ` уже фигурирует в договоре номер ` {old_deal} `. Сначала нужно отменить его (` !cancel {old_deal} `)")
      return

    # second check the price range is valid
    row = get_db_row("fn_basket", item, "Item_ID")
    item_type = row["Item_Type"].lower()
    valid_price = PRICES[item_type]

    # DEPRECATED: i.e. must be: 1 <= price <= valid_price
    # if int(price) < 1 or int(price) > valid_price:
    #   await respond(ctx, f"цена должна быть между ` 1 ` и ` {valid_price} ` (включительно).")
    #   return

    # must be >= 1
    if int(price) < 1 :
      await respond(ctx, f"цена должна быть положительным числом!")
      return

    # extract target
    try:
      target = get_id(target)
    except Exception as e:
      await respond(ctx, f"вы должны либо указать человека, которому хотите продать итем через ` @ `, либо указать ` 0 ` чтобы купить итем мог любой.")
      return

    if target != 0 and not self.bot.get_user(target):
      await respond(ctx, f"вы должны либо указать человека, которому хотите продать итем через ` @ `, либо указать ` 0 ` чтобы купить итем мог любой.")
      return

    if source == str(target):
      await respond(ctx, "вы не можете заключить договор с самим собой!")
      return

    now = datetime.datetime.now()
    deal_id = insert_row("fn_market", ["Timestamp", "Source", "Target", "Item", "Price", 'Status'], [now, source, target, item, price, "Hanging"])
    glasnost = get_channel_by_name(self.bot, "гласность", "Russian")
    await respond(ctx, f"конракт номер ` {deal_id} ` готов! Детали можно посмотреть в {glasnost.mention} и по команде ` !deal {deal_id} `.")
    embed = get_deal_embed(self.bot, deal_id)
    await glasnost.send(embed=embed)

  @commands.command(name="deal")
  async def deal(self, ctx, deal):
    embed = get_deal_embed(self.bot, int(deal))
    if not embed:
      await respond(ctx, "сделки под таким номером нет!")
      return
    await ctx.send(embed=embed)

  @commands.command(name="cancel")
  async def cancel(self, ctx, deal_id):
    deal = get_db_row("fn_market", str(deal_id))

    if not deal:
      await respond(ctx, "контракта под таким номером не существует!")
      return 

    if str(deal["Source"]) != str(ctx.author.id):
      await respond(ctx, "вы не являетесь инициатором данного договора!")
      return

    if deal["Status"] != "Hanging":
      await respond(ctx, "данный контракт нельзя разорвать, так как он уже истёк или приведён в исполнение.")
      return

    delete_row("fn_market", str(deal_id))
    await respond(ctx, f"контракт ` {deal_id} ` успешно разорван!")

  @commands.command(name="accept")
  async def accept(self, ctx, deal_id):
    deal = get_db_row("fn_market", deal_id)
    if not deal:
      await respond(ctx, f"договора под номером ` {deal_id} ` не существует!")
      return
    
    if str(deal["Target"]) != str(ctx.author.id) and deal["Target"] != 0:
      await respond(ctx, f"договор номер ` {deal_id} ` не затрагивает вас, как покупателя!")
      return 

    if str(deal["Source"]) == str(ctx.author.id):
      await respond(ctx, f"вы не можете заключать договор с самим собой!")
      return 

    # check if already expired
    if deal["Status"] == "Expired":
      await respond(ctx, f"срок годности договора под номером ` {deal_id} ` уже истёк! Нужно заключать новый.")
      return 

    if deal["Status"] == "Done":
      await respond(ctx, f"договор номер ` {deal_id} ` уже заключён!")
      return 

    now = datetime.datetime.now()
    timestamp = deal["Timestamp"]
    diff = (now - timestamp).total_seconds()
    if diff > DAY:
      await respond(ctx, f"срок годности договора под номером ` {deal_id} ` уже истёк! Нужно заключать новый.")
      update_db_entry("fn_market", "Status", "Expired", str(deal_id))
      return 

    # check limit for the number of items of that type
    item = deal["Item"]
    item_row = get_db_row("fn_basket", str(item), "Item_ID")
    if not item_row:
      await respond(ctx, RESPONSES["mistake"])
      return 

    item_type = item_row["Item_Type"]

    rows = get_rows_custom(f"SELECT * FROM fn_basket WHERE ID = \'{str(ctx.author.id)}\' AND Item_Type = \'{item_type}\'")
    item_limit = LIMITS[item_type.lower()]
    try:
      full = len(rows) == item_limit
    except Exception as e:
      await respond(ctx, RESPONSES["mistake"])
      return 

    if full:
      await respond(ctx, f"У вас уже есть {item_limit} {get_item_str(item_limit)} типа ` {item_type} ` в инвентаре!\nИзбавтесь от одного из них с помощью команды ` !drop <item-number> `.")
      return 

    res = await pay_up(self.bot, ctx, deal["Source"], "waifu", int(deal["Price"]))
    if not res:
      return

    # update status to 'Done'
    update_db_entry("fn_market", "Status", "Done", deal_id)

    # hit accept, the in fn_basket update ID value (as in owner of the item in question) for the row with respective Item_ID 
    update_db_entry("fn_basket", "ID", str(ctx.author.id), str(item), "Item_ID")

    # post result in glasnost
    await respond(ctx, f"сделка успешно заключена, деньги переведены! Итем ` {item} ` уже в вашем инвентаре.")
    pass

  @commands.command(name="drop")
  async def drop(self, ctx, item):
    if not item_in_posession(ctx.author.id, item):
      await respond(ctx, "такого итема нет в вашем инвентаре!")
      return

    res = execute_custom(f"DELETE FROM fn_basket WHERE Item_ID = \'{item}\'")
    if res:
      await respond(ctx, f"Итем ` {item} ` успешно удалён из инвентаря!")
    else:
      await respond(ctx, RESPONSES["mistake"])

  @commands.command(name="item")
  async def item(self, ctx, item):
    row = get_db_row("fn_basket", item, "Item_ID")

    if not row:
      await respond(ctx, "такого итема не существует!")
      return
    
    if str(ctx.author.id) != str(row["ID"]):
      await respond(ctx, "этот итем не в вашем инвентаре! Если хотите увидеть его — попросите владельца.")
      return

    embed = get_item_embed(row) 
    await ctx.send(embed=embed)

  @commands.command(name="мошна")
  async def inventory(self, ctx):

    embed = get_inventory_embed(ctx) 
    if not embed:
      await respond(ctx, "ваш инвентарь пуст!")
      return 

    await ctx.send(embed=embed)

  @commands.command(name="waifu")
  async def random_waifu(self, ctx):

    # check if currently owns 6 wives already
    rows = get_rows_custom(f"SELECT * FROM fn_basket WHERE ID = \'{ctx.author.id}\' AND Item_Type = \'Waifu\'")
    limit = LIMITS["waifu"]
    if rows and len(rows) == limit:
      await respond(ctx, f"в вашем ивентаре уже {limit} кошкожён!")
      return

    # check waifu limit
    res = await pay_up(self.bot, ctx, GUILD, "waifu")
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
    # name = str(RussianNames(count=1, transliterate=False, gender=0.0).get_batch()[0])
    now = datetime.datetime.now()
    # item_id = ctx.message.id
    item_id = update_basket(ctx.author.id, name, 'Waifu', {"image-url": url, "name": name})
    purchase_id = record_purchase(ctx.author.id, GUILD, now, "Waifu", item_id, PRICES["waifu"], "Finished")
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

