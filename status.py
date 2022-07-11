# Thiis file holds the functionality of the bot in regards to the status of the server

import discord
from discord.ext import commands
import pymysql.cursors
from env import *
from utils import *

class Status(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
  
  def get_channel(self, guild, name):
    for ch in guild.channels:
      if name in ch.name:
        return ch
    return False

  @commands.Cog.listener()
  async def on_member_join(self, member):
    
    if ("ТМГ" not in member.guild.name and "TMG Zanshin" not in member.guild.name):
      return

    db, cursor = get_db_cursor()

    apatrid = discord.utils.get(member.guild.roles, name='Апатрид')
    await member.add_roles(apatrid)

    # ch = self.get_channel(member.guild, "погран")
    ch = get_channel_by_name(self.bot, "погран-застава", 'Russian')
    # manifesto = self.get_channel(member.guild, "manifesto")
    manifesto = get_channel_by_name(self.bot, "манифест", 'Russian')
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

