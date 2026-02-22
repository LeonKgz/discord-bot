from discord.ext import commands
import pymysql.cursors
import requests
from utils import *
from env import *

import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

import os
import shutil
import json
import urllib.request
from elevenlabs import generate, voices, set_api_key
set_api_key('c173cd93acabc779a73edbb2755573de')


import random
from googletrans import Translator

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

  # create webdriver object
  def process_word(self, phrase, timerr, default_filename=False, custom_filename=None, add_particle=False):

    png_dir = f"./pngs/{phrase}.png" if not default_filename else ("./pngs/png.png" if not custom_filename else "./pngs/{custom_filename}.png")
    wav_dir = f"./wavs/{phrase}.wav" if not default_filename else ("./wavs/wav.wav" if not custom_filename else "./wavs/{custom_filename}.wav")

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

    options = webdriver.FirefoxOptions()
    options.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=options,
    desired_capabilities={
        "unhandledPromptBehavior": "accept"  # or "accept"
    })
    try:
      # get google.co.in
      driver.get("https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index")

      element = driver.find_element(By.ID,"PhrasingText")
      submit_wrapper = driver.find_element(By.ID,"phrasing_submit_wrapper")
      submit_button = submit_wrapper.find_element(By.CLASS_NAME, "submit")
      element.send_keys((phrase + "は") if add_particle else phrase)

      action = ActionChains(driver)
      driver.execute_script("window.scrollTo(0,200)")
      action.move_to_element(submit_button)
      action.click()
      action.perform()

      WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "phrasing_main")))
      driver.execute_script("window.scrollTo(0,700)")

      phrase = driver.find_element(By.ID, "phrasing_main")

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
    # alert = Alert(driver)
    # alert.accept()

    # driver.quit()
    driver.close()

    # if not default_filename:
    #   os.remove(png_dir)
    #   os.remove(wav_dir)

  # create webdriver object
  def process_words(self, phrases, timerr, default_filename=False, add_particle=False): 
    try:
      [os.remove(f"./pngs/{f}") for f in os.listdir("./pngs/")]
      [os.remove(f"./wavs/{f}") for f in os.listdir("./wavs/")]
    except Exception as e:
      print(e)
      pass


    # driver = webdriver.Firefox()


    options = webdriver.FirefoxOptions()
    options.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=options,
    desired_capabilities={
        "unhandledPromptBehavior": "accept"  # or "accept"
    })



    driver.get("https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index")

    i = 0
    for phrase in phrases:
      i += 1

      png_dir = f"./pngs/{i}.png"
      wav_dir = f"./wavs/{i}.wav" 
      # png_dir = f"./pngs/{self.get_hash_filename(phrase)}.png"
      # wav_dir = f"./wavs/{self.get_hash_filename(phrase)}.wav" 

      try:

        element = driver.find_element(By.ID,"PhrasingText")
        submit_wrapper = driver.find_element(By.ID,"phrasing_submit_wrapper")
        submit_button = submit_wrapper.find_element(By.CLASS_NAME, "submit")

        element.send_keys(Keys.CONTROL, 'a')
        element.send_keys(Keys.BACKSPACE)
        element.send_keys((phrase + "は") if add_particle else phrase)

        action = ActionChains(driver)
        driver.execute_script("window.scrollTo(0,200)")
        action.move_to_element(submit_button)
        action.click()
        action.perform()

        WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID, "phrasing_main")))
        driver.execute_script("window.scrollTo(0,700)")

        phrase = driver.find_element(By.ID, "phrasing_main")

        phrase.screenshot(png_dir)
        driver.implicitly_wait(1)

        phrasing_main = driver.find_element(By.ID,"phrasing_main")
        driver.execute_script("window.scrollTo(0,700)")
        
        WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.XPATH, "//input[@value='作成']")))
        generate_button = phrasing_main.find_element(By.XPATH, "//input[@value='作成']")
        action = ActionChains(driver)

        time.sleep(3.0)
        action.move_to_element(generate_button).click().perform()

        driver.implicitly_wait(1)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='保存']")))
        save_audio_button = phrasing_main.find_element(By.XPATH, "//input[@value='保存']")
        action = ActionChains(driver)
        action.move_to_element(save_audio_button)
        action.click()
        action.perform()

        driver.implicitly_wait(1)
        time.sleep(3.0)

        # move all wavs from downloads int othe wavs directory
        for file in os.listdir(down):
          if ".wav" in file:
            shutil.move(f"{down}{file}", wav_dir)

        # time.sleep(3.0)
        # driver.execute_script("window.scrollTo(0,0)")
        time.sleep(3)   
        driver.refresh()

      except Exception as e:
        print(e)
        raise Exception(f"Timeout on phrase: {phrase} {e}")

    driver.implicitly_wait(10)
    alert = Alert(driver)
    alert.accept()

    driver.quit()

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

  @commands.command(name="wordsdeprec")
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
                  "вопрос": f"{original} ({furigana})" if kanjiless else original,
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

  @commands.command(name="ngrammar")
  async def ngrammar(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        full = all[0].strip()
        to_replace = all[1].strip()
        back_text = full.replace(to_replace, f"<u>{to_replace}</u>")
        hint = all[2].strip()
        front = full.replace(to_replace, "＿＿＿")

        # original = s.split("(")[0].strip()
        # interpret = s.split("(")[1].split(")")[0].strip()

        ####################################

        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(full, curr_timer, default_filename=True)
            succ = True
          except Exception as e:
            print(e)
            curr_timer += 3
        ####################################

        # self.get_voice_from_eleven(interpret, 'en_')
        random_code = random.randrange(1000000000000)
        note = {
              # "deckName": "__________Bunpou",
              "deckName": "Nihon::Grammar",
              "modelName": "Основная",
              # "modelName": "Основная (+ обратные карточки)" if not single else "Основная",
              "fields": {
                "вопрос": f"{front}<br>\t({hint})",
                # "ответ": interpret,
                # "ответ": f"{full}<br><br>[sound:{self.get_legit_file_name(full)}.wav]",
                "ответ": f"{back_text}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
              }],
              "picture": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
                  "fields": [
                      "ответ"
                  ]
              }],
          }

        note_pronounce = {
              "deckName": "Nihon::Sentences (Say)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{full}<br>",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
          }

        note_listen = {
              "deckName": "Nihon::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>",

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
          invoke('addNotes', notes=[note, note_pronounce, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="nphrase")
  async def nphrase(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        front = all[0].strip()
        back = all[1].strip()
        full = back

        ####################################


        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(full, curr_timer, default_filename=True)
            succ = True
          except Exception as e:
            print(e)
            curr_timer += 3
        ####################################

        # self.get_voice_from_eleven(interpret, 'en_')
        random_code = random.randrange(1000000000000)
        note = {
              # "deckName": "__________Bunpou",
              "deckName": "Nihon::Phrases",
              "modelName": "Основная",
              # "modelName": "Основная (+ обратные карточки)" if not single else "Основная",
              "fields": {
                "вопрос": f"{front}",
                "ответ": f"{back}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
              }],
              "picture": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
                  "fields": [
                      "ответ"
                  ]
              }],
          }

        note_pronounce = {
              "deckName": "Nihon::Sentences (Say)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{full}<br>",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
          }

        note_listen = {
              "deckName": "Nihon::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\">",
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
          invoke('addNotes', notes=[note, note_pronounce, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="ngrammara")
  async def ngrammara(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        front = all[0].strip()
        back = all[1].strip()

        ####################################

        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(back, curr_timer, default_filename=True, custom_filename="back")
            self.process_word(front, curr_timer, default_filename=True, custom_filename="front")
            succ = True
          except Exception as e:
            print(e)
            curr_timer += 3
        ####################################

        # self.get_voice_from_eleven(interpret, 'en_')
        random_code = random.randrange(1000000000000)
        note = {
              "deckName": "Nihon::Grammar (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"[sound:{self.get_legit_file_name(front)}_{random_code}_IN_JAPANESE.wav]",
                "ответ": f"{back}<br><img src=\"{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
                },
                {
                  "filename": f"{self.get_legit_file_name(front)}_{random_code}_IN_JAPANESE.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
                },
              ],
              "picture": [{
                  "filename": f"{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.png",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
                  "fields": [
                      "ответ"
                  ]
              }],
          }

        note_pronounce = {
              "deckName": "Nihon::Sentences (Say)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{full}<br>",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.wav]",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
          }

        note_listen = {
              "deckName": "Nihon::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"[sound:{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.wav]",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(back)}_{random_code}_IN_JAPANESE.png\">",
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
          invoke('addNotes', notes=[note, note_pronounce, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")


  def get_img_src(self, word):
    try:
      query = f"\"deck:Nihon::Words (Listen)\" w:{word}"
      notes = invoke('findNotes', query=query)

      notesInfo = invoke('notesInfo', notes=notes)

      answer = notesInfo[0]['fields']['Ответ']['value']
      image = answer.split("<img src=")[1].split(">")[0]
      return f"<img src={image}>"

    except Exception as e:
      print(e)
      return "image_source_not_found"

  @commands.command(name="nwords")
  async def nwords(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        single_word = all[0].strip()
        full = all[1].strip()
        to_replace = all[2].strip()
        back_text = full.replace(to_replace, f"<u>{to_replace}</u>")

        # hint = all[2]
        # hint = "<img src=\"5ad982870b7504e7d6733b120bebaa93_t.jpeg\">"
        hint = self.get_img_src(single_word)

        front = full.replace(to_replace, "＿＿＿")

        # original = s.split("(")[0].strip()
        # interpret = s.split("(")[1].split(")")[0].strip()

        ####################################


        succ = False
        curr_timer = 5
        while not succ:
          try:
            self.process_word(full, curr_timer, default_filename=True)
            succ = True
          except Exception as e:
            print(e)
            curr_timer += 3
        ####################################

        # self.get_voice_from_eleven(interpret, 'en_')
        random_code = random.randrange(1000000000000)
        note = {
              # "deckName": "__________Bunpou",
              "deckName": "Nihon::Words (Enter)",
              "modelName": "Основная",
              # "modelName": "Основная (+ обратные карточки)" if not single else "Основная",
              "fields": {
                "вопрос": f"{front}<br><br><details><summary></summary><p>{hint}</p></details>",
                # "ответ": interpret,
                # "ответ": f"{full}<br><br>[sound:{self.get_legit_file_name(full)}.wav]",
                "ответ": f"{back_text}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
                  "fields": [
                      "ответ"
                  ]
              }],
              "picture": [{
                  "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
                  "fields": [
                      "ответ"
                  ]
              }],
          }
        
        note_pronounce = {
              # "deckName": "__________Bunpou",
              "deckName": "Nihon::Sentences (Say)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{full}<br>",
                # "ответ": interpret,
                # "ответ": f"{full}<br><br>[sound:{self.get_legit_file_name(full)}.wav]",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
          }

        note_listen = {
              # "deckName": "__________Bunpou",
              "deckName": "Nihon::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",
                "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\">",

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
          invoke('addNotes', notes=[note, note_pronounce, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="ewords")
  async def ewords(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        full = all[0].strip()
        to_replace = all[1].strip()
        hint = all[2].strip()

        front = full.replace(to_replace, "_____")
        back = full.replace(to_replace, f"<u>{to_replace}</u>")

        note = {
              "deckName": "English::Words (Enter)",
              "modelName": "Основная",
             
              "fields": {
                "вопрос": f"{front}<br><br><details><summary></summary><p>{hint}</p></details>",
                "ответ": f"{back}",

              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
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

  @commands.command(name="ephrase")
  async def ephrase(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        original = s.split("\\")[1].strip()
        question = s.split("\\")[0].strip()

        ####################################

        self.get_voice_from_eleven(original, 'en_')
        
        ####################################
        note = {
              "deckName": "English::Phrases",
              "modelName": "Основная",
              "fields": {
                "ответ": f"{original}<br><br>[sound:{self.get_legit_file_name(original)}.wav]",
                "вопрос": f"{question}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(original)}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                }
              ],
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

  def get_legit_file_name(self, original):
    ret = original.replace(".", "_dot_").replace("?", "_question_").replace("!", "_exclamation_").replace(",", "_comma_").replace("\"", "_quotation_").replace("'", "_apostrophe_")
    ret = ret.replace("。", "_dot_").replace("？", "_question_").replace("！", "_exclamation_").replace("、", "_comma_").replace("「", "_quotation_").replace("」", "_quotation_")
    return ret.strip().replace(" ", "_")[:15]

  def get_voice_from_eleven(self, phrase, prefix):

    f_voices = [v.name for v in voices() if v.labels['gender'] == 'female']

    # f_voices = ['Nephilia']
    random_voice_name = random.choice(f_voices)
    voice_settings = {
        "stability": 0.75,  # Optional: adjust the stability of the voice
        "similarity": 0.75,  # Optional: adjust how similar to the model voice
        "rate": 0.8  # Speed rate (1.0 is normal speed, higher values increase speed)
    }
    audio = generate(text=phrase, voice=random_voice_name, model="eleven_multilingual_v2")

    try:
      os.remove(f"./wavs/{prefix}wav.wav")
    except Exception as e:
      print(e)

    with open(f"./wavs/{prefix}wav.wav", 'bx') as f:
      print("WRITIN!")
      f.write(audio)

  @commands.command(name="gphrase")
  async def gphrase(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        original = s.split("\\")[1].strip()
        question = s.split("\\")[0].strip()

        ####################################

        self.get_voice_from_eleven(original, 'de_')
        
        ####################################
        note = {
              # "deckName": "__________Bunpou",
              "deckName": "German::Phrases",
              "modelName": "Основная",
              "fields": {
                "ответ": f"{original}<br><br>[sound:{self.get_legit_file_name(original)}.wav]",
                "вопрос": f"{question}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(original)}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                }
              ],
          }

        note_listen = {
              # "deckName": "__________Bunpou",
              "deckName": "German::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "ответ": f"{original}",
                "вопрос": f"[sound:{self.get_legit_file_name(original)}.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(original)}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                }
              ],
          }


        success = False
        errmsg = ""
        try:
          invoke('addNotes', notes=[note, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="ggrammar")
  async def ggrammar(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        original = s.split("\\")[0].strip()
        to_replace = s.split("\\")[1].strip()
        mnemonic = s.split("\\")[2].strip()
        question = original.replace(to_replace, "____")
        # interpret = s.split("(")[1].split(")")[0].strip()

        ####################################

        self.get_voice_from_eleven(original, 'de_')
        # self.get_voice_from_eleven(interpret, 'en_')
        
        ####################################
        mnemonic = f"<br><br>{mnemonic}" if mnemonic else ""
        note = {
              # "deckName": "__________Bunpou",
              "deckName": "German::Grammar",
              "modelName": "Основная",
              "fields": {
                "ответ": f"{original}<br><br>[sound:{self.get_legit_file_name(original)}.wav]",
                "вопрос": f"{question}{mnemonic}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(original)}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                }
                # {
                #   "filename": f"{self.get_legit_file_name(interpret)}.wav",
                #   "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\en_wav.wav",
                #   "fields": [
                #       "ответ"
                #   ]
                # },
              ],
          }

        note_listen = {
              # "deckName": "__________Bunpou",
              "deckName": "German::Sentences (Listen)",
              "modelName": "Основная",
              "fields": {
                "ответ": f"{original}",
                "вопрос": f"[sound:{self.get_legit_file_name(original)}.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{self.get_legit_file_name(original)}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                }
                # {
                #   "filename": f"{self.get_legit_file_name(interpret)}.wav",
                #   "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\en_wav.wav",
                #   "fields": [
                #       "ответ"
                #   ]
                # },
              ],
        }

        success = False
        errmsg = ""
        try:
          invoke('addNotes', notes=[note, note_listen])
          success = True
        except Exception as e:
          errmsg = f"{e}"

        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="gwords")
  async def ggwords(self, ctx: commands.Context, *, args=None):

      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      words = confession.split("\n")

      for word in words: 
        if ("(" in word):
          translation = word.split("(")[1].split(")")[0].strip()
        else:
          tr = Translator()
          # By default translate german to english (russian if explicitly specified with a 'ru_' prefix)
          translation = tr.translate(word, dest=LANGUAGE_CODES['russian' if word[:3] == 'ru_' else 'english']).text

        # Clear the prefix
        if (word[:3] == 'ru_'):
          word = word[3:]

        ####################################

        self.get_voice_from_eleven(word, 'de_')
        self.get_voice_from_eleven(translation, 'en_')
        
        ####################################

        note = {
              # "deckName": "__________Bunpou",
              "deckName": "German Vocab",
              "modelName": "Основная (+ обратные карточки)",
              "fields": {
                "вопрос": f"{word}<br><br>[sound:{word}.wav]",
                "ответ": f"{translation}<br><br>[sound:{translation}.wav]",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": [],
              "audio": [
                {
                  "filename": f"{word}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\de_wav.wav",
                  "fields": [
                      "вопрос"
                  ]
                },
                {
                  "filename": f"{translation}.wav",
                  "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\en_wav.wav",
                  "fields": [
                      "ответ"
                  ]
                },
              ],
          }

        success = False
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

  @commands.command(name="knewwords")
  async def knewwords(self, ctx: commands.Context, *, args=None):
      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        word = all[0].strip()
        audio = all[1].strip()
        image = all[2].strip()
        translation = all[3].strip()

        notes = [
          {
              "deckName": "Кыргызча::Words (Image)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{image}",
                "ответ": f"{audio}<br><br>{word}<br><br><details><summary></summary><p>{translation}</p></details>",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
          },
          {
              "deckName": "Кыргызча::Words (Listen)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{audio}",
                "ответ": f"{image}<br><br>{word}<br><br><details><summary></summary><p>{translation}</p></details>",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
          },
          {
              "deckName": "Кыргызча::Words (Read)",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{word}",
                "ответ": f"{audio}<br><br>{image}<br><br><details><summary></summary><p>{translation}</p></details>",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
          },
        ]
        
        success = False
        errmsg = ""

        try:
          invoke('addNotes', note=notes)
          success = True
        except Exception as e:
          errmsg = f"{e}"


        if not success:
          ret = f"There was an error with {s}! ` {errmsg} `"
          await ctx.send(ret)

      await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

  @commands.command(name="kgrammar")
  async def kgrammar(self, ctx: commands.Context, *, args=None):
      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        sentence = all[0].strip().replace("-", "<br><br>-")
        sentence_modified = all[1].strip().replace("-", "<br><br>-")

        note = {
              "deckName": "Кыргызча::Grammar",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{sentence_modified}",
                "ответ": f"{sentence}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
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

  @commands.command(name="kpronounce")
  async def kpronounce(self, ctx: commands.Context, *, args=None):
      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        sentence = all[0].strip().replace("-", "<br><br>-")
        audio = all[1].strip()

        note = {
              "deckName": "Кыргызча::Grammar",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{sentence}",
                "ответ": f"{audio}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
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

  @commands.command(name="kphrases")
  async def kphrases(self, ctx: commands.Context, *, args=None):
      if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
        return

      confession = str(args)
      confession = confession.strip()
      ss = [s.strip() for s in confession.split("\n")]
      single = ss[0] == 's'

      for s in ss:
        all = s.split("\\")

        translation = all[0].strip()
        phrase = all[1].strip()

        note = {
              "deckName": "Кыргызча::Phrases",
              "modelName": "Основная",
              "fields": {
                "вопрос": f"{translation}",
                "ответ": f"{phrase}",
              },
              "options": {
                  "allowDuplicate": False,
                  "duplicateScope": "deck",
              },
              "tags": []
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




  # @commands.command(name="nwordsdeprec")
  # async def grammarwords_improved(self, ctx: commands.Context, *, args=None):

  #     if (not await self.check_rights(ctx, ['Политбюро ЦКТМГ'])):
  #       return

  #     confession = str(args)
  #     confession = confession.strip()
  #     ss = [s.strip() for s in confession.split("\n")]
  #     single = ss[0] == 's'

  #     phrases_to_process = []

  #     for s in ss:
  #       all = s.split("\\")
  #       single_word = all[0].strip()
  #       full = all[1].strip()
  #       phrases_to_process.append(full)

  #     ####################################

  #     succ = False
  #     curr_timer = 5
  #     while not succ:
  #       try:
  #         self.process_words(phrases_to_process, curr_timer, default_filename=True)
  #         succ = True
  #       except Exception as e:
  #         print(e)
  #         curr_timer += 3
  #     ####################################
          
  #     i = 0
  #     for s in ss:

  #       i += 1

  #       all = s.split("\\")
  #       single_word = all[0].strip()
  #       full = all[1].strip()

  #       to_replace = all[2].strip()
  #       back_text = full.replace(to_replace, f"<u>{to_replace}</u>")
  #       hint = self.get_img_src(single_word)
  #       front = full.replace(to_replace, "＿＿＿")
            
  #       random_code = random.randrange(1000000000000)
  #       note = {
  #             "deckName": "Nihon::Words (Enter)",
  #             "modelName": "Основная",
  #             "fields": {
  #               "вопрос": f"{front}<br><br><br>{hint}",
  #               "ответ": f"{back_text}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

  #             },
  #             "options": {
  #                 "allowDuplicate": False,
  #                 "duplicateScope": "deck",
  #             },
  #             "tags": [],
  #             "audio": [{
  #                 "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav",
  #                 "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\{i}.wav",
  #                 # "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\wavs\\wav.wav",
  #                 "fields": [
  #                     "ответ"
  #                 ]
  #             }],
  #             "picture": [{
  #                 "filename": f"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png",
  #                 "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\{i}.png",
  #                 # "path": f"C:\\Users\\alben\\vscode\\bot\\bot\\pngs\\png.png",
  #                 "fields": [
  #                     "ответ"
  #                 ]
  #             }],
  #         }
        
  #       note_pronounce = {
  #             "deckName": "Nihon::Sentences (Say)",
  #             "modelName": "Основная",
  #             "fields": {
  #               "вопрос": f"{full}<br>",
  #               "ответ": f"{full}<br><img src=\"{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.png\"><br><br>[sound:{self.get_legit_file_name(full)}_{random_code}_IN_JAPANESE.wav]",

  #             },
  #             "options": {
  #                 "allowDuplicate": False,
  #                 "duplicateScope": "deck",
  #             },
  #             "tags": [],
  #         }

  #       success = False
  #       errmsg = ""

  #       try:
  #         invoke('addNote', note=note)
  #         success = True
  #       except Exception as e:
  #         errmsg = f"{e}"

  #       try:
  #         invoke('addNote', note=note_pronounce)
  #         success = True
  #       except Exception as e:
  #         errmsg = f"{e}"


  #       if not success:
  #         ret = f"There was an error with {s}! ` {errmsg} `"
  #         await ctx.send(ret)

  #     await ctx.send("Processsing of new grammar is finished! Anki updated. Don't forget to synchronize!")

