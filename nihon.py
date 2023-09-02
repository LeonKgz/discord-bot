from discord.ext import commands
import pymysql.cursors
import requests
from utils import *
from env import *

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import json
import urllib.request

# down= "/mnt/c/Users/Халметов Юрий/Downloads/"

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

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return
      name = ctx.author.name
      iid = ctx.author.id
      confession = str(args)
      confession = confession.strip()
      kanjis = confession.split()
      for kanji in kanjis:
        on, kun, meanings = get_kanji_info(kanji)
        note = {
              # "deckName": "__________Kanji",
              "deckName": "N5 Kanji",
              "modelName": "Основная",
              # "modelName": "Основная (+ обратные карточки)",
              "fields": {
                "вопрос": f"{kanji}",
                "ответ": f"{on}<br><br>{kun}<br><br>{meanings}"
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
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

  #####################################################################################################################################

  # create webdriver object
  def process_word(self, phrase, timerr, default_filename=False, add_particle=False):

    png_dir = f"./pngs/{phrase}.png" if not default_filename else "./pngs/png.png"
    wav_dir = f"./wavs/{phrase}.wav" if not default_filename else "./wavs/wav.wav"

    # remove all sound files in download directory first
    for file in os.listdir(down):
      if ".wav" in file:
        os.remove(f"{down}{file}")

    pngfile = f"./pngs/{phrase}.png"   
    wavfile = f"./wavs/{phrase}.wav"
    allpngfile = f"./pngs/*.png"   
    allwavfile = f"./wavs/*.wav"

    try:
      [os.remove(f"./pngs/{f}") for f in os.listdir("./pngs/")]
      [os.remove(f"./wavs/{f}") for f in os.listdir("./wavs/")]
    except Exception as e:
      print(e)
      pass

    driver = webdriver.Firefox()
    try:
      # get google.co.in
      driver.get("https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index")

      element = driver.find_element(By.ID,"PhrasingText")
      submit_wrapper = driver.find_element(By.ID,"phrasing_submit_wrapper")
      submit_button = submit_wrapper.find_element(By.CLASS_NAME, "submit")
      element.send_keys((phrase + "は") if add_particle else phrase)

      #print(submit_button.rect)

      action = ActionChains(driver)
      driver.execute_script("window.scrollTo(0,200)")
      action.move_to_element(submit_button)
      action.click()
      action.perform()

      WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "phrasing_main")))
      driver.execute_script("window.scrollTo(0,700)")

      phrase = driver.find_element(By.CLASS_NAME,"phrasing_phrase_wrapper")

      phrase.screenshot(png_dir)
      driver.implicitly_wait(1)

      phrasing_main = driver.find_element(By.ID,"phrasing_main")
      driver.execute_script("window.scrollTo(0,700)")
      
      generate_button = phrasing_main.find_element(By.XPATH, "//input[@value='作成']")
      action = ActionChains(driver)
      time.sleep(1)
      action.move_to_element(generate_button).click().perform()

      driver.implicitly_wait(1)
      WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='保存']")))
      save_audio_button = phrasing_main.find_element(By.XPATH, "//input[@value='保存']")
      action = ActionChains(driver)
      action.move_to_element(save_audio_button)
      action.click()
      action.perform()
      driver.implicitly_wait(1)
      time.sleep(5)

      # move all wavs from downloads int othe wavs directory
      for file in os.listdir(down):
        if ".wav" in file:
          shutil.move(f"{down}{file}", wav_dir)

      # remove all wavs from downloads

    except Exception as e:
      print(e)
      driver.close()
      raise Exception("Timeout")
      # raise Exception("Timeout probably lol")

    driver.implicitly_wait(10)
    driver.close()

    # if not default_filename:
    #   os.remove(png_dir)
    #   os.remove(wav_dir)
  
  def request(action, **params):
      return {'action': action, 'params': params, 'version': 6}

  def invoke(action, **params):
      requestJson = json.dumps(request(action, **params)).encode('utf-8')
      response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))

      if len(response) != 2:
          raise Exception('response has an unexpected number of fields')
      if 'error' not in response:
          raise Exception('response is missing required error field')
      if 'result' not in response:
          raise Exception('response is missing required result field')
      if response['error'] is not None:
          raise Exception(response['error'])
      return response['result']

  #####################################################################################################################################

  @commands.command(name="words")
  async def words(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return
      name = ctx.author.name
      iid = ctx.author.id
      confession = str(args)
      confession = confession.strip()
      words = confession.split()

      for word in words:
        
        kanjiless = word[0] == 's'
        if kanjiless:
          word = word[1:]

        success = False
        original, furigana, meaning = get_word_info(word)
        print(original, furigana, meaning)
        errmsg = meaning
        
        if original:
          
          # brackets = f" ({furigana})" if furigana else ""
          tags = ["simple"] if kanjiless else []
          note = {
                # "deckName": "__________Kotoba",
                "deckName": "N5 Kotoba",
                # "modelName": "Основная",
                "modelName": "Основная (+ обратные карточки)",
                "fields": {
                  "вопрос": f"{original} {furigana}" if kanjiless else original,
                  # "вопрос": original + brackets,
                  "ответ": meaning
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                },
                "tags": tags,
            }

          errmsg = ""
          try:
            invoke('addNote', note=note)
            success = True
          except Exception as e:
            errmsg = f"{e}"

          if furigana:

            succ = False
            curr_timer = 5
            while not succ:
              try:
                self.process_word(original, curr_timer, add_particle=True)
                succ = True
              except Exception as e:
                # print(e)
                curr_timer += 3

            reading_question = original

            if kanjiless:
              reading_question = f"{original} ({furigana})"

            note = {
                # "deckName": "__________Reading",
                "deckName": "N5 Reading",
                # "modelName": "Основная (+ обратные карточки)",
                "modelName": "Основная",
                "fields": {
                  "вопрос": reading_question,
                  "ответ": f"{furigana}<br><img src=\"{original}_n5.png\"><br><br>[sound:{original}_n5.wav]"
                },
                "options": {
                    "allowDuplicate": True,
                    "duplicateScope": "deck",
                },
                "audio": [{
                    "filename": f"{original}_n5.wav",
                    # "path": f"C:\\Users\\Халметов Юрий\\Downloads\\selenium\\wavs\\{original}.wav",
                    "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\{original}.wav",
                    "fields": [
                        "ответ"
                    ]
                }],
                "picture": [{
                    "filename": f"{original}_n5.png",
                    # "path": f"C:\\Users\\Халметов Юрий\\Downloads\\selenium\\pngs\\{original}.png",
                    "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\{original}.png",
                    "fields": [
                        "ответ"
                    ]
                }],
            }

            # note = {
            #       "deckName": "1 Reading",
            #       "modelName": "Основная",
            #       "fields": {
            #         "вопрос": original,
            #         "ответ": furigana,
            #       },
            #       "options": {
            #           "allowDuplicate": False,
            #           "duplicateScope": "deck",
            #       },
            #       "tags": [],
            #   }

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

  @commands.command(name="names")
  async def names(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return
      confession = str(args)
      confession = confession.strip()
      words = confession.split()

      for word in words:
        original = word.strip()
        success = False
        errmsg = ""
        try:
          invoke('addNote', note=note)
          success = True
        except Exception as e:
          errmsg = f"{e}"

        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(original, curr_timer)
            succ = True
          except Exception as e:
            # print(e)
            curr_timer += 3

        note = {
            "deckName": "__________Names",
            # "modelName": "Основная (+ обратные карточки)",
            "modelName": "Основная",
            "fields": {
              "вопрос": original,
              "ответ": f"<br><img src=\"{original}.png\"><br><br>[sound:{original}.wav]"
            },
            "options": {
                "allowDuplicate": True,
                "duplicateScope": "deck",
            },
            "audio": [{
                "filename": f"{original}.wav",
                "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\{original}.wav",
                "fields": [
                    "ответ"
                ]
            }],
            "picture": [{
                "filename": f"{original}.png",
                "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\{original}.png",
                "fields": [
                    "ответ"
                ]
            }],
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

      await ctx.send("Processsing of new names is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="grammar")
  async def grammar(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]

      for s in ss:
        original = s.split("(")[0].strip()
        interpret = s.split("(")[1].split(")")[0].strip()



        ####################################


        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(original, curr_timer, default_filename=True)
            succ = True
          except Exception as e:
            print(e)
            curr_timer += 3
        ####################################

        note = {
              # "deckName": "__________Bunpou",
              "deckName": "N5 Bunpou",
              "modelName": "Основная (+ обратные карточки)",
              "fields": {
                "вопрос": f"{original}<br><img src=\"{original}.png\"><br><br>[sound:{original}.wav]",
                "ответ": interpret,
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [{
                  "filename": f"{original}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
              }],
              "picture": [{
                  "filename": f"{original}.png",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
                  "fields": [
                      "ответ"
                  ]
              }],
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

  @commands.command(name='get')
  async def download_link(self, ctx: commands.Context, *, args=None):
    if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
      return
    
    links = str(args)
    links = links.strip()
    links= links.split()

    for link in links:
      try:
        name, dl = get_staroe_radio_name_and_link(link)
        msg = await ctx.send(f"*Сохраняю* файл => *\"{name}\"*")
        response = requests.get(dl)
        open(f"{DOWN}/{name}.mp3", "wb").write(response.content)
        await msg.edit(content=f"Сохранён файл => *\"{name}\"*")
      except Exception as e:
        print(e)
        await ctx.send(f"Проблема с сохранением файла => *\"{name}\"*")

    await ctx.send(f"{mention_author(ctx)}　はい　終わりました。")

  async def check_rights(self, ctx, acceptable_roles, tell=True):
    #super_roles = ['Политбюро ЦКТМГ', 'ВЧК', 'СовНарМод', 'Главлит']
    super_roles = acceptable_roles

    try:
      res_roles = ctx.author.roles
    except Exception as e:
      res_roles = self.bot.get_user(ctx.author.id).roles

    for role in list(map(str, res_roles)):
      if (role in super_roles):
        return True
    if tell:
      response = "**" + str(ctx.author.name) + "**, у тебя нет доступа к этой команде " + str(du_get(bot.emojis, name='peepoClown'))
      await ctx.send(response)
    return False

def setup(bot):
  bot.add_cog(Nihon(bot))
