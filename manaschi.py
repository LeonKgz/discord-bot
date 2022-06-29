#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import os
import discord
from discord.ext import commands
from voice import Voice

# retrieving Discord credentials
TOKEN = str(os.getenv('DISCORD_TOKEN_MANASCHI'))

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')

bot.add_cog(Voice(bot))
bot.run(TOKEN)
