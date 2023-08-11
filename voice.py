#! /usr/bin/python
# vim: set fileencoding=utf-8:
# coding=utf-8

import asyncio
import requests
from discord import FFmpegPCMAudio
from utils import disconnect, get_staroe_radio_info, get_staroe_radio_name_and_link, mention_author
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
from discord.ext import commands

class Voice(commands.Cog):

  def __init__(self, bot):
    self.bot = bot  
    self.staroe_stations = [
      ("Старое Радио (Музыка)", "http://server.audiopedia.su:8000/music128", None),
      ("Старое Радио (Стихи, Пьесы, Рассказы, Программы)", "http://server.audiopedia.su:8000/ices128", ""),
      ("Детское Радио", "http://server.audiopedia.su:8000/detskoe128", "detskoe"),
    ]

  @commands.command(name='radio')
  async def radio(self, ctx: commands.Context):
    ss = [f"`  {i} => {self.staroe_stations[i][0]}`" for i in range(len(self.staroe_stations))]
    joiner = "\n"
    stations = joiner.join(ss)
    await ctx.send(f"Вот список доступных радиостанций:\n{joiner}{stations}")

  @commands.command(name='on')
  async def on(self, ctx: commands.Context, number):
      await disconnect(self.bot, ctx)
      channel = ctx.message.author.voice.channel
      print(channel)
      player = await channel.connect()
      print(player)
      number = int(number)
      print(number)
      if number < len(self.staroe_stations):
        await ctx.send(f"Включаю `{self.staroe_stations[number][0]}`")
        dir = self.staroe_stations[number][2]
        if dir != None:
          await ctx.send(f"Сейчас играет *\"{get_staroe_radio_info(dir)}\"*")
        player.play(FFmpegPCMAudio(self.staroe_stations[number][1]))
      else:
        await ctx.send(f"Такой радиостанции не существует.")
        return 

  @commands.command(name='rec')
  async def rec(self, ctx: commands.Context):
        channel = ctx.message.author.voice.channel
        channel.start_recording()
        print("Recording...")

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
      # for x in self.bot.voice_clients:
      #     if(x.guild == ctx.message.guild):
      #         return await x.disconnect()
      res = await disconnect(self.bot, ctx)
      if not res:
        return await ctx.send("I am not connected to any voice channel on this server!")

def setup(bot):
  bot.add_cog(Voice(bot))
