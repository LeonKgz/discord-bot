from discord.ext import commands
import requests
from utils import * 
from env import * 

class Heatmap(commands.Cog):

  def __init__(self, bot):
    self.bot = bot 
    self.command_map = {
      "food": {
        "schema": "no_food",
        "title": "No food after 7pm",
        "table": "heatmap",
        "items_allowed": False,
      },
      "kendo": {
        "schema": "kendo",
        "title": "Kendo",
        "table": "heatmap",
        "items_allowed": False,
      },
      "sleep": {
        "schema": "8_hours",
        "title": "8 hours of sleep",
        "table": "heatmap",
        "items_allowed": False,
      },
      "read": {
        "schema": "books_read",
        "title": "Books Read",
        "table": "heatmap",
        "items_allowed": True,
      },
      "finished": {
        "schema": "books_finished",
        "title": "Books finished",
        "table": "heatmap",
        "items_allowed": True,
      },
      "code": {
        "schema": "coding",
        "title": "Coding Questions",
        "table": "heatmap",
        "items_allowed": False,
      },
      "go": {
        "schema": "tsumego",
        "title": "Tsumego Study",
        "table": "heatmap",
        "items_allowed": False,
      },
      "nippon": {
        "schema": "japanese",
        "title": "Japanese",
        "table": "heatmap",
        "items_allowed": False,
      },
    }

    
  def get_db_cursor(self):
    db = pymysql.connect(host=HOST,
												 user=USER,
												 password=PASSWORD,
												 db=DB,
												 charset='utf8mb4',
												 cursorclass=pymysql.cursors.DictCursor)
    return db, db.cursor()

  @commands.command(name="food", aliases=["kendo", "sleep", "read", "finished", "code", "go", "nippon"])
  async def heatmap_command(self, ctx, *, args=None):
  # async def heatmap_command(self, ctx, item_name=None, date=None, value=1):

    if int(ctx.author.id) != ME:
      return

    invoked = str(ctx.invoked_with)

    schema = self.command_map[invoked]["schema"]
    title = self.command_map[invoked]["title"]
    table = self.command_map[invoked]["table"]
    items_allowed = self.command_map[invoked]["items_allowed"]
    value = 1
    if not items_allowed:
      value = 5

    items = ""
    date=str(datetime.datetime.now().strftime('%-Y-%-m-%-d'))

    args = str(args).strip()
    args_split_by_double_quote = args.split("\"")
    args_split_by_space = args.split()
    items_present = "\"" in args

    if items_allowed and items_present:
      item_name = args_split_by_double_quote[1].strip()
      date_present = args_split_by_double_quote[2].strip()
      if date_present:
        date = date_present
    elif not items_allowed and items_present:
      await respond(ctx, "для данной каманды не нужны итемы")
      return 
    else:
      date_present = args_split_by_space[0]
      if date_present != "None":
        date = date_present.strip()

    # db, cursor = self.get_db_cursor()
    
    rows = get_rows_custom(f"SELECT * FROM {table} WHERE my_schema = \'{schema}\' AND my_date = \'{date}\'")
    entry_exists = len(rows) > 0
    if entry_exists:
      row = rows[0]
      value = int(row['value']) + len(item_name.split(", "))
      
      if items_allowed:
        if row['items']:
          items = row['items'].split(", ")
        items = ", ".join(sorted((items + [item_name])))
      
      # item_name = items
    
    if not entry_exists:
      if items_present:
        items = item_name
        value = len(item_name.split(", "))

      ret = insert_row(
        table=table, 
        fields=["my_schema", "title", "my_date", "items", "value"], 
        values=[schema, title, str(date), str(items), str(value)])
    else:
      ret = execute_custom(f"UPDATE {table} SET items = \'{items}\', value = \'{value}\' WHERE my_schema = \'{schema}\' AND my_date = \'{date}\'")

    failed = ret != 0 and (ret == None or ret == False)

    if not failed:

      url = f"http://albenz.xyz:6969/heatmap"
      response = str(requests.get(url))
      if response != "<Response [200]>":
        await respond(ctx, "problems calling the heatmap flask API!") 
      await respond(ctx, f"*\" {items} \"* is registered for {date}.") 
    else:
      await respond(ctx, RESPONSES["mistake"])



def setup(bot):
  bot.add_cog(Heatmap(bot))