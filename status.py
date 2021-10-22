# Thiis file holds the functionality of the bot in regards to the status of the server

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get

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
    apatrid = discord.utils.get(member.guild.roles, name='Апатрид')
    await member.add_roles(apatrid)

    ch = self.get_channel(member.guild, "погран")
    manifesto = self.get_channel(member.guild, "manifesto")
    await ch.send(f"<@!{member.id}>, добро пожаловать в ТМГ!\n\nЭто пограничная застава, охраняющая суверенитет Мошны.\n В канале {manifesto.mention} ты найдёшь Трактат о Мошне — основополагающий документ сего сообщества.\nЧтобы получить доступ ко всем остальным каналам сервера и стать полноценным гражданином, достаточно ввести команду « !пропуск ». \n\nДа прибудет с тобой Мошна!")

    ch = self.get_channel(member.guild, "карандаш")
    await ch.send(f"<@!{member.id}> ({member.name}) вступил в ТМГ!")

  @commands.Cog.listener()
  async def on_member_remove(self, member):
    ch = self.get_channel(member.guild, "карандаш")
    await ch.send(f"<@!{member.id}> ({member.name}) **покинул** ТМГ!")

def setup(bot):
  bot.add_cog(Status(bot))
