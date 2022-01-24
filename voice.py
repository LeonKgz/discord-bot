#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import asyncio
import requests
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from utils import *
from discord import FFmpegPCMAudio
from discord.ext import commands
# test comment

class Voice(commands.Cog):

  def __init__(self, bot):
    self.bot = bot  

  @commands.command(name='on')
  async def on(self, ctx: commands.Context, number):
      channel = ctx.message.author.voice.channel
      player = await channel.connect()
      number = int(number)
      if (number == 0):
        # Музыка
        player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/music128'))
      elif number == 1:  
        # Старое радио
        player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/ices128'))
      elif number == 2:  
        # Детское радио
        player.play(FFmpegPCMAudio('http://server.audiopedia.su:8000/detskoe128'))

  #Get videos from links or from youtube search
  def search(self, arg):
      with YoutubeDL({'format': 'bestaudio', 'noplaylist':'False', 'ignoreerrors': 'True'}) as ydl:
          try: requests.get(arg)
          except: info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries']
          else: info = ydl.extract_info(arg, download=False)

      es = [dict(i) for i in info["entries"]]
      ret = []
      for i in es:
        url = i["formats"][0]['url']
        ret.append((i, url))
      return ret
      #return (info, info['formats'][0]['url'])

  @commands.command(name='yt')
  async def yt(self, ctx, *, query):
      #Solves a problem I'll explain later
      FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
      
      # query should be a link to the playlist (not ay video within the playlist!)
  #    video, source = search(query)
      video_sources = self.search(query)
      channel = ctx.author.voice.channel
      voice = await channel.connect() 

      curr = 0
      while True:

        video, source = video_sources[curr]
        curr += 1
        
        if (curr >= len(video_sources)):
          curr = 0
        
        title = video['title']
        await ctx.send(f"Now playing {title}.")

        voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))
        while(voice.is_playing()):
          await asyncio.sleep(10)
          continue

  # @bot.command(name='31')
  # async def kaligula1(ctx):
  #     channel = ctx.message.author.voice.channel
  #     player = await channel.connect()
  #
  #     for x in bot.voice_clients:
  #
  #        if (x.is_connected()):
  #            x.stop()
  #            while (True):
  #                x.play(FFmpegPCMAudio('files/gong.mp3'))
  #        else:
  #
  #            channel = ctx.message.author.voice.channel
  #            player = await channel.connect()
  #            while (True):
  #                player.play(FFmpegPCMAudio('files/gong.mp3'))

  @commands.command(name='one')
  async def one(self, ctx):
      channel = ctx.message.author.voice.channel
      player = await channel.connect()

      for x in self.bot.voice_clients:
        if (x.is_connected()):
            x.stop()
            x.play(FFmpegPCMAudio('files/lakki1.mp3'))
            while(player.is_playing()):
                await asyncio.sleep(1)
                continue
            await x.disconnect()

        else:
            channel = ctx.message.author.voice.channel
            player = await channel.connect()
            player.play(FFmpegPCMAudio('files/lakki1.mp3'))

            while(player.is_playing()):
                await asyncio.sleep(1)
                continue
            await x.disconnect()

  @commands.command(name='two')
  async def two(self, ctx):
      channel = ctx.message.author.voice.channel
      player = await channel.connect()

      for x in self.bot.voice_clients:
        if (x.is_connected()):
            x.stop()
            x.play(FFmpegPCMAudio('files/lakki2.mp3'))
            while(player.is_playing()):
                await asyncio.sleep(1)
                continue

            await x.disconnect()

        else:
            channel = ctx.message.author.voice.channel
            player = await channel.connect()
            player.play(FFmpegPCMAudio('files/lakki2.mp3'))
            while(player.is_playing()):
                await asyncio.sleep(1)
                continue
            await x.disconnect()

  @commands.command(name='three')
  async def three(self, ctx):
      channel = ctx.message.author.voice.channel
      player = await channel.connect()

      for x in self.bot.voice_clients:
        if (x.is_connected()):
            x.stop()
            x.play(FFmpegPCMAudio('files/nicksex.mp3'))
            while(player.is_playing()):
                await asyncio.sleep(1)
                continue
            await x.disconnect()

        else:
            channel = ctx.message.author.voice.channel
            player = await channel.connect()
            player.play(FFmpegPCMAudio('files/nicksex.mp3'))
            while(player.is_playing()):
                await asyncio.sleep(1)
                continue
            await x.disconnect()

  @commands.command(name='off', pass_context = True)
  async def off(self, ctx):
      for x in self.bot.voice_clients:
          if(x.guild == ctx.message.guild):
              return await x.disconnect()

      return await ctx.send("I am not connected to any voice channel on this server!")

def setup(bot):
  bot.add_cog(Voice(bot))
