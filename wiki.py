import wikipediaapi
import datetime
import random

def print_langlinks(page):
    langlinks = page.langlinks
    for k in sorted(langlinks.keys()):
        v = langlinks[k]
        print("%s: %s - %s: %s" % (k, v.language, v.title, v.fullurl))

wiki_wiki = wikipediaapi.Wikipedia('en')

today = datetime.datetime.now()
month = today.strftime("%B")
day = today.day

page = wiki_wiki.page(f'{day} {month}')
#s = page.sections[2]

deaths = page.text.split("Births")[1].split("Holidays")[0].split("\n")

found_valid_page = False

while not found_valid_page:  

  case = deaths[random.randint(0, len(deaths) - 1)]
  try:
    case = case.split("–")[1].split(",")[0]
  except Exception as e:
    continue

  page = wiki_wiki.page(f'{case}')
  #print([str(s.title) for s in page.sections])
  found_valid_page = "Early life" in [str(s.title) for s in page.sections]

ss = [s.title for s in page.sections]
idx = ss.index('Early life')
section = page.sections[idx]
print("----------------------------------")
print_langlinks(page)
print()
print(page.title)
print()
print(page.summary)
print()
print(section.text)
print("----------------------------------")

page = wiki_wiki.page(f'{day} {month}')
deaths = page.text.split("Deaths")[1].split("Holidays")[0].split("\n")

found_valid_page = False

while not found_valid_page:  

  case = deaths[random.randint(0, len(deaths) - 1)]
  try:
    case = case.split("–")[1].split(",")[0]
  except Exception as e:
    continue

  page = wiki_wiki.page(f'{case}')
  #print([str(s.title) for s in page.sections])
  found_valid_page = "Death" in [str(s.title) for s in page.sections]

ss = [s.title for s in page.sections]
idx = ss.index('Death')
section = page.sections[idx]
print("----------------------------------")
print_langlinks(page)
print()
print(page.title)
print()
print(page.summary)
print()
print(section.text)
print("----------------------------------")


