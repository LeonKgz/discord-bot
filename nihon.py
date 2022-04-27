import discord
import os
from discord.ext import commands, tasks
import pymysql.cursors
import datetime
import wikipediaapi
import random
import requests
from utils import *

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE'))
GUILD = int(str(os.getenv('DISCORD_GUILD')))

class Nihon(commands.Cog):

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

  # @commands.command(name='on')
  # async def on(self, ctx: commands.Context, number):

  @commands.command(name="kanji")
  async def kanji(self, ctx: commands.Context, *, args=None):

      if (not await check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return
      name = ctx.author.name
      iid = ctx.author.id
      confession = str(args)
      confession = confession.strip()
      kanjis = confession.split()
      for kanji in kanjis:
        on, kun, meanings = get_kanji_info(kanji)
        note = {
              "deckName": "__________Kanji",
              "modelName": "Основная",
              # "modelName": "Основная (+ обратные карточки)",
              "fields": {
                "вопрос": f"{kanji}",
                "ответ": f"{on}<br><br>{kun}<br><br>{meanings}"
              },
              "options": {
                  "allowDuplicate": True,
              },
              "tags": [],
          }

        success = False
        errmsg = ""
        try:
          invoke('addNote', note=note)
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {kanji}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new kanji is finished! Anki updated. Don't forget to synchronize!")

  @bot.command(name="words")
  async def words(self, ctx: commands.Context, *, args=None):

      if (not await check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return
      name = ctx.author.name
      iid = ctx.author.id
      confession = str(args)
      confession = confession.strip()
      words = confession.split()

      for word in words:
        success = False
        original, furigana, meaning = get_word_info(word)
        errmsg = meaning

        if original:

          # brackets = f" ({furigana})" if furigana else ""
          note = {
                "deckName": "__________Kotoba",
                # "modelName": "Основная",
                "modelName": "Основная (+ обратные карточки)",
                "fields": {
                  "вопрос": original,
                  # "вопрос": original + brackets,
                  "ответ": meaning
                },
                "options": {
                    "allowDuplicate": True,
                },
                "tags": [],
            }

          errmsg = ""
          try:
            invoke('addNote', note=note)
            success = True
          except Exception as e:
            errmsg = f"{e}"

          if furigana:
            note = {
                  "deckName": "__________Reading",
                  "modelName": "Основная",
                  # "modelName": "Основная (+ обратные карточки)",
                  "fields": {
                    "вопрос": original,
                    # "вопрос": original + brackets,
                    "ответ": furigana,
                  },
                  "options": {
                      "allowDuplicate": True,
                  },
                  "tags": [],
              }

            errmsg = ""
            try:
              invoke('addNote', note=note)
              success = True
            except Exception as e:
              errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {word}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new words is finished! Anki updated. Don't forget to synchronize!")

  @bot.command(name="grammar")
  async def grammar(self, ctx: commands.Context, *, args=None):

      if (not await check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]

      for s in ss:
        original = s.split("(")[0]
        interpret = s.split("(")[1].split(")")[0].strip()

        note = {
              "deckName": "__________Bunpou",
              "modelName": "Основная",
              "modelName": "Основная (+ обратные карточки)",
              "fields": {
                "вопрос": original,
                "ответ": interpret,
              },
              "options": {
                  "allowDuplicate": True,
              },
              "tags": [],
          }

        success = False
        errmsg = ""
        try:
          invoke('addNote', note=note)
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

def setup(bot):
  bot.add_cog(Nihon(bot))
