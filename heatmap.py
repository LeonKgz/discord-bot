from discord.ext import commands
import requests
from utils import * 
from env import * 

class Heatmap(commands.Cog):

  def __init__(self, bot):
    self.bot = bot 
    
  def get_db_cursor(self):
    db = pymysql.connect(host=HOST,
												 user=USER,
												 password=PASSWORD,
												 db=DB,
												 charset='utf8mb4',
												 cursorclass=pymysql.cursors.DictCursor)
    return db, db.cursor()

  @commands.command(name="bookread")
  async def duty(self, ctx, book_name, date=None, value=1):
    schema = "books_read"
    title = "Books Read"
    table = "heatmap"

    db, cursor = self.get_db_cursor()

    if not date:
      date=str(datetime.datetime.now().strftime('%-Y-%-m-%-d'))
    
    rows = get_rows_custom(f"SELECT * FROM {table} WHERE my_schema = \'{schema}\' AND my_date = \'{date}\'")
    entry_exists = len(rows) > 0
    if entry_exists:
      row = rows[0]
      items = row['items'].split(", ")
      value = int(row['value']) + 1
      items = ", ".join(sorted((items + [book_name])))
      
      book_name = items

    if not entry_exists:
      ret = insert_row(
        table=table, 
        fields=["my_schema", "title", "my_date", "items", "value"], 
        values=[schema, title, str(date), str(book_name), str(value)])
    else:
      ret = execute_custom(f"UPDATE {table} SET items = \'{book_name}\', value = \'{value}\' WHERE my_schema = \'{schema}\' AND my_date = \'{date}\'")

    failed = ret != 0 and (ret == None or ret == False)

    if not failed:

      url = f"http://albenz.xyz:6969/heatmap"
      response = str(requests.get(url))
      if response != "<Response [200]>":
        await respond(ctx, "problems calling the heatmap flask API!") 
      await respond(ctx, f"*\" {book_name} \"* is registered for {date}.") 
    else:
      await respond(ctx, RESPONSES["mistake"])

def setup(bot):
  bot.add_cog(Heatmap(bot))