from discord.ext import commands
import requests
from utils import * 
from env import * 
from googletrans import Translator

class Zettel(commands.Cog):

  def __init__(self, bot):
    self.bot = bot 
    
  @commands.command(name="долг")
  async def duty(self, ctx, issue):
    url = f"http://albenz.xyz:6969/duty?issue={issue}"
    
    #ret = await ctx.send("*Подождите...*")
    response = requests.get(url)
    response = response.json()
    try:
      await parse_zettel_json(ctx, response)
    except Exception as e:
      print(e)
      await ctx.send(f"<@!{ctx.author.id}>, долг для *«{issue}»* не найден! « !долги », чтобы посмотреть все ключевые слова.")

  @commands.command(name='remedy', aliases=['средство'])
  async def remedy(self, ctx, *, args=None):
    translator = Translator()
    issue = args.strip()

    response_options = { 
      "en": {
        "404": f"{mention_author(ctx)}, remedy for *«{issue}»* was not found! « !remedies » to view all available keywords.",
      },
      "ru": {
        "404": f"{mention_author(ctx)}, средство для *«{issue}»* не найдено! « !средства », чтобы посмотреть все ключевые слова.",
      }
    }

    invoked = ctx.invoked_with
    lang = GLD[invoked]

    url = f"http://albenz.xyz:6969/remedy?issue={issue}"

    response = requests.get(url)
    data = response.json()

    rus_version = data["content"]
    if lang == "en":
      eng_version = translator.translate(rus_version).text
      data["content"] = eng_version

    try:
      await parse_zettel_json(ctx, data)
    except Exception as e:
      await ctx.send(response_options[lang]["404"])

  @commands.command(name='prayer', aliases=['молитва'])
  async def prayer(self, ctx):

    translator = Translator()
    response_options = { 
      "en": {
        "hold": "*Generating your unique prayer...*", 
        "ready": "Done! I recommend printing it.",
      },
      "ru": {
        "hold": "*Генерирую вашу уникальную молитву...*",
        "ready": "Готово! Советую распечатать.",
      }
    }

    invoked = ctx.invoked_with
    lang = GLD[invoked]

    await ctx.channel.send(response_options[lang]["hold"])

    url = f"http://albenz.xyz:6969/prayer"

    response = requests.get(url)
    data = response.json()
    verses = data["verses"] 
    
    if lang == "en":
      for v in verses:
        original = v["content"]
        eng_version = translator.translate(original).text
        v["content"] = eng_version
        v["remedy"] = v["remedy"].split(" - ")[1]
    else:
      for v in verses:
        v["remedy"] = v["remedy"].split(" - ")[0]

    tex = """\documentclass[10pt]{article}
  \\usepackage[russian]{babel}
  \\usepackage{tgpagella}
  \\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.7in]{geometry}
  \\usepackage{multicol}
  %\\pagenumbering{gobble}
  \\setlength{\columnsep}{1cm}

  \\begin{document}

  \\begin{multicols}{2}""" + "".join(["\\section{" + v["remedy"] + "}" + "\n\n".join(v["content"].split("\n\n")[1:]).replace("  ", " ").strip().replace("\n\n", "\\\\\n\n") for v in verses]) + """

  \\end{multicols}

  \\end{document}
    """

    filename = "Stoic_prayer_for_" + "_".join(ctx.author.display_name.split())
    with open(f"./{filename}.tex", "w") as f:
      f.write(tex)

    # Necessary set up to install pdf latex  
    # sudo apt-get install texlive-latex-base
    # sudo apt-get install texlive-fonts-recommended
    # sudo apt-get install texlive-fonts-extra
    # sudo apt-get install texlive-latex-extra

    # pdflatex latex_source_name.tex

    # sudo apt-cache search texlive russian
    # sudo apt-get install texlive-lang-cyrillic

    os.system(f"pdflatex {filename}.tex")
    # await ret.delete()
    await ctx.channel.send(response_options[lang]["ready"])
    await ctx.channel.send(file=discord.File(f"{filename}.pdf"))

    os.remove(f"./{filename}.tex")
    os.remove(f"./{filename}.pdf")
    os.remove(f"./{filename}.log")
    os.remove(f"./{filename}.aux")

  @commands.command(name="стих")
  async def poem(self, ctx, issue):

    if str(ctx.author.id) == "423476785959665671" and str(issue) == "Глупость":

      embed = discord.Embed(title="Рубаи. Омар Хаям", description="450", color=0xa87f32) #creates embed
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      embed.set_thumbnail(url="https://obrazovaka.ru/wp-content/uploads/2021/02/omar-hayyam-e1614119392242.jpg")
      embed.set_image(url="https://i.imgur.com/aqfPdkJ.gif")
      embed.set_footer(text="Дураки мудрецом почитают меня...")
      await ctx.send(embed=embed)
      return 

    url = f"http://albenz.xyz:6969/poem?issue={issue}"

    response = requests.get(url)
    data = response.json()
    
    try:
      await parse_zettel_json(ctx, data)
    except Exception as e:
      await ctx.send(f"<@!{ctx.author.id}>, стих для *«{issue}»* не найдено! « !стихи », чтобы посмотреть все ключевые слова.")

  @commands.command(name="стихи")
  async def poems(self, ctx):
    url = f"http://albenz.xyz:6969/poems"

    response = requests.get(url)
    data = response.json()["poems"]

    if not data:
      await ctx.send(f"<@!{ctx.author.id}>, стихи не найдены!")

    ret_str = ", ".join(data)
    await ctx.send(f"*<@!{ctx.author.id}>, вот список ключевых слов: \n\n\t{ret_str}.*")

  @commands.command(name="remedies", aliases=['средства'])
  async def remedies(self, ctx):
    response_options = { 
      "en": {
        "404": f"*{mention_author(ctx)}, remedies not found!*",
        "success": f"*{mention_author(ctx)}, here's the list of keywords: "
      },
      "ru": {
        "404": f"*{mention_author(ctx)}, средства не найдены!",
        "success": f"*{mention_author(ctx)}, вот список ключевых слов: "
      }
    }
    invoked = ctx.invoked_with
    lang = GLD[invoked]

    url = f"http://albenz.xyz:6969/remedies"
    response = requests.get(url)

    data = response.json()["remedies"][lang]
    
    if not data:
      await ctx.send(response_options[lang]["404"])
    
    ret_str = ", ".join(data)
    await ctx.send(response_options[lang]["success"] + f"\n\n\t{ret_str}.*")

  @commands.command(name="долги")
  async def duties(self, ctx):
    url = f"http://albenz.xyz:6969/duties"

    response = requests.get(url)
    data = response.json()["duties"]

    if not data:
      await ctx.send(f"<@!{ctx.author.id}>, долги не найдены!")

    ret_str = ", ".join(data)
    await ctx.send(f"*<@!{ctx.author.id}>, вот список ключевых слов: \n\n\t{ret_str}.*")

def setup(bot):
  bot.add_cog(Zettel(bot))