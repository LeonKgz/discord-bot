from discord.ext import commands
from utils import *

class Static(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name="манифест")
  async def manifest(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz/files/tractatus.pdf")

  @commands.command(name="сайт")
  async def website(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz")

  @commands.command(name="пьесы")
  async def plays(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://albenz.xyz/plays/allplays/")

  @commands.command(name="песни")
  async def songs(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.albenz.xyz/songs/allartists/")

  @commands.command(name="plays")
  async def plays_yt(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.youtube.com/channel/UCdVx_oiTYB8fQdkbYmUPRQQ")

  @commands.command(name="songs")
  async def songs_yt(self, ctx):
    await ctx.send(f"<@!{ctx.author.id}>, тебе сюда => https://www.youtube.com/channel/UCVRzrqkQxWawb-cKz1zXBZQ")

  @commands.command(name="статьи")
  async def statji(self, ctx):
    if (not await check_rights_dm(ctx)):
        return

    if (ctx.guild):
      await ctx.message.delete()
      return

    res = "1) Ненормативная лексика\n2) Прескриптивная лингвистика\n3) Спам\n4) Необоснованное оскорбление\n5) низкая Мошна"

    await ctx.send(res)

