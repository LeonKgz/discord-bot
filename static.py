from discord.ext import commands

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
