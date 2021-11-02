# Thiis file holds the functionality of the bot in regards to the status of the server

import discord
import os
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get
import pymysql.cursors

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))

class Status(commands.Cog):

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

  def get_channel(self, guild, name):
    for ch in guild.channels:
      if name in ch.name:
        return ch
    return False

  @commands.Cog.listener()
  async def on_member_join(self, member):
    
    if (member.guild.name != "ТМГ"):
      return

    db, cursor = self.get_db_cursor()

    apatrid = discord.utils.get(member.guild.roles, name='Апатрид')
    await member.add_roles(apatrid)

    ch = self.get_channel(member.guild, "погран")
    manifesto = self.get_channel(member.guild, "manifesto")
    await ch.send(f"<@!{member.id}>, добро пожаловать в ТМГ!\n\nЭто пограничная застава, охраняющая суверенитет Мошны.\n В канале {manifesto.mention} ты найдёшь Трактат о Мошне — основополагающий документ сего сообщества.\nЧтобы получить доступ ко всем остальным каналам сервера и стать полноценным гражданином, вам нужно рассказать о себе. Для полных инструкций, введите команду « **!пропуск** ». \n\nДа прибудет с тобой Мошна!")

    ch = self.get_channel(member.guild, "карандаш")
    await ch.send(f"<@!{member.id}> ({member.name}) вступил в ТМГ!")

    # TODO consider the case when a user with a confessino leave sand rejoins server, for now default Confession field to False
    
    try:
      sql = f"INSERT INTO raiting(ID, Name, Points, Confession) VALUES (\"{member.id}\", \"{member.name}\", \"{0}\", \"No\")"
      cursor.execute(sql)
      db.commit()
      res_id = cursor.lastrowid

    except Exception as e:
      print(e)
      db.rollback()
      await ctx.send(f"<@!{source_id}>, ошибка обновления базы данных! Убедитесь, что в вашей припи     ске нет кавычек!")
      return

  @commands.Cog.listener()
  async def on_member_remove(self, member):
    ch = self.get_channel(member.guild, "карандаш")
    await ch.send(f"<@!{member.id}> ({member.name}) **покинул** ТМГ!")

def setup(bot):
  bot.add_cog(Status(bot))

