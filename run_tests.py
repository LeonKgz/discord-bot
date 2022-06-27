"""
A functional demo of all possible test cases. This is the format you will want to use with your testing bot.
    Run with:
        python example_tests.py TARGET_NAME TESTER_TOKEN
"""
from distest import TestCollector
from distest import run_dtest_bot
from utils import clear_db_table, get_db_row, mention, generate_text, update_db_entry
import random
import sys
import os
import datetime
import json

TEST_USER = int(str(os.getenv('TEST_USER')))
TEST_USER_TOKEN = str(os.getenv('TEST_USER_TOKEN'))
TEST_USER_NAME = 'Zanshin'

# The tests themselves

test_collector = TestCollector()
created_channel = None

async def assert_reply(interface, actual, expected):
  try:
    ret_msg = await interface.assert_reply_contains(actual, expected)
    assert ret_msg.content == expected
    # print("Test is passed")
  except Exception as e:
    print(e)
    exit(-1)

@test_collector()
async def test_submit_description(interface):
  clear_db_table("confessions")
  # clear_db_table("unmarked_confessions")

  msg = f"!рассказать \"{generate_text()}\""
  expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
  await assert_reply(interface, msg, expected)

  # # confirm there is an entry in unmarked_confessions
  # ret = get_db_row("unmarked_confessions", TEST_USER)
  # print(ret)
  # # TODO: For now test user is also a marker
  # assert ret, exit(-1)
  # assert ret["Markers"] == str(TEST_USER), exit(-1)

@test_collector()
async def test_submit_bad_description_no_quotes(interface):
  msg = f"!рассказать {generate_text()}"
  expected = f"{mention(TEST_USER)} ты забыл(а) **кавычки**!"
  await assert_reply(interface, msg, expected)

@test_collector()
async def test_submit_bad_description_no_quotes_around(interface):

  # Inserting random single quote in text
  text = generate_text()
  idx = int(random.random() * len(text))
  text = text[:idx] + "\"" + text[idx:]
  msg = f"!рассказать {text}"
  expected = f"{mention(TEST_USER)} **кавычки** должны быть вокруг!"
  await assert_reply(interface, msg, expected)

  # Inserting random single quote at the beginning 
  text = generate_text()
  text = "\"" + text
  msg = f"!рассказать {text}"
  expected = f"{mention(TEST_USER)} **кавычки** должны быть вокруг!"
  await assert_reply(interface, msg, expected)

  # Inserting random single quote at the end
  text = generate_text()
  text = text + "\""
  msg = f"!рассказать {text}"
  expected = f"{mention(TEST_USER)} **кавычки** должны быть вокруг!"
  await assert_reply(interface, msg, expected)

@test_collector()
async def test_submit_bad_description_quotes_inside(interface):

  # Inserting random single quote in text
  text = generate_text()
  idx = int(random.random() * len(text))
  text = text[:idx] + "\"" + text[idx:]
  msg = f"!рассказать \"{text}\""
  expected = f"{mention(TEST_USER)} если ты хочешь использовать **кавычки** в описании, нужно перед ними поставить **« \\\\ »**, то есть например:\nВместо \"Я работаю в комании \"Комплекс\" три года\" =>  \"Я работаю в комании \\\\\"Комплекс\\\\\" три года\""
  await assert_reply(interface, msg, expected)

@test_collector()
async def test_submit_bad_description_short(interface):

  # Inserting random single quote in text
  text = generate_text(text_size=1)
  msg = f"!рассказать \"{text}\""
  expected = f"{mention(TEST_USER)} твоё описание либо **слишком короткое** либо ты забыл(а) **кавычки**!"
  await assert_reply(interface, msg, expected)

@test_collector()
async def test_submit_bad_description_too_soon(interface):
  clear_db_table("confessions")
  msg = f"!рассказать \"{generate_text()}\""
  expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
  await assert_reply(interface, msg, expected)

  diff = int(random.random() * 7)
  new_date = get_db_row("confessions", TEST_USER)['Timestamp'] - datetime.timedelta(days=diff)
  update_db_entry("confessions", "Timestamp", new_date, TEST_USER)

  msg = f"!рассказать \"{generate_text()}\""
  expected = f"{mention(TEST_USER)} своё описание можно обновлять максимум один раз в 7 дней! \n\n\t**Вы сможете обновить своё через {7 - diff}**"
  await assert_reply(interface, msg, expected)

@test_collector()
async def test_submit_new_description(interface):
  clear_db_table("confessions")
  msg = f"!рассказать \"{generate_text()}\""
  expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
  await assert_reply(interface, msg, expected)

  random_evaluation_value = int(random.random() * 10)
  random_evaluation = {TEST_USER: random_evaluation_value}
  random_evaluation = json.dumps(random_evaluation)
  random_evaluation = random_evaluation.replace("\"", "\\\"")

  update_db_entry("confessions", "Points", random_evaluation, TEST_USER)

  random_social_score = int(random.random() * 100) + random_evaluation_value
  update_db_entry("raiting", "Points", random_social_score, TEST_USER)

  # set a random date between now and now + 7 days
  diff = int(random.random() * 7) + 7
  new_date = datetime.datetime.now() - datetime.timedelta(days=diff)
  update_db_entry("confessions", "Timestamp", new_date, TEST_USER)

  msg = f"!рассказать \"{generate_text()}\""
  expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
  await assert_reply(interface, msg, expected)

  confessions_row = get_db_row("confessions", TEST_USER)
  assert confessions_row, exit(-1)
  assert confessions_row["Points"] == "{}", exit(-1)

@test_collector()
async def test_submit_retrieve_description(interface):
  clear_db_table("confessions")

  random_text = generate_text()
  msg = f"!рассказать \"{random_text}\""
  expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
  await assert_reply(interface, msg, expected)

  msg = f"!кто {mention(TEST_USER)}"
  # expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"

  expected = f"{mention(TEST_USER)}, вот что {TEST_USER_NAME} говорит о себе: \n\n\t*{random_text}*"
  await assert_reply(interface, msg, expected)


# @test_collector()
# async def test_description_delete(interface):
#   clear_db_table("confessions")
#   msg = f"!рассказать \"{generate_text()}\""
#   expected = f"{mention(TEST_USER)} ваше описание обновлено, проходите!"
#   await assert_reply(interface, msg, expected)
  
# @test_collector()
# async def test_ping(interface):
#     await interface.assert_reply_contains("ping?", "pong!")

# @test_collector()
# async def test_delayed_reply(interface):
#     message = await interface.send_message(
#         "Say some stuff, but at 4 seconds, say 'yeet'"
#     )
#     await interface.get_delayed_reply(5, interface.assert_message_equals, "yeet")


# @test_collector()
# async def test_reaction(interface):
#     await interface.assert_reaction_equals("React with \u2714 please!", u"\u2714")


# @test_collector()
# async def test_reply_equals(interface):
#     await interface.assert_reply_equals("Please say 'epic!'", "epic!")


# @test_collector()
# async def test_channel_create(interface):
#     await interface.send_message("Create a tc called yeet")
#     created_channel = await interface.assert_guild_channel_created("yeet")


# # @test_collector
# # async def test_pin_in_channel(interface):
# #     await interface.send_message("Pin 'this is cool' in yeet")
# #     await interface.assert_guild_channel_pin_content_equals(created_channel )


# @test_collector()
# async def test_channel_delete(interface):
#     await interface.send_message("Delete that TC bro!")
#     await interface.assert_guild_channel_deleted("yeet")


# @test_collector()
# async def test_silence(interface):
#     await interface.send_message("Shhhhh...")
#     await interface.ensure_silence()


# @test_collector()
# async def test_reply_contains(interface):
#     await interface.assert_reply_contains(
#         "Say something containing 'gamer' please!", "gamer"
#     )


# @test_collector()
# async def test_reply_matches(interface):
#     await interface.assert_reply_matches(
#         "Say something matching the regex `[0-9]{1,3}`", r"[0-9]{1,3}"
#     )


# @test_collector()
# async def test_ask_human(interface):
#     await interface.ask_human("Click the Check!")


# @test_collector()
# async def test_embed_matches(interface):
#     embed = (
#         Embed(
#             title="This is a test!",
#             description="Descriptive",
#             url="http://www.example.com",
#             color=0x00FFCC,
#         )
#         .set_author(name="Author")
#         .set_thumbnail(
#             url="https://upload.wikimedia.org/wikipedia/commons/4/40/Test_Example_%28cropped%29.jpg"
#         )
#         .set_image(
#             url="https://upload.wikimedia.org/wikipedia/commons/4/40/Test_Example_%28cropped%29.jpg"
#         )
#     )

#     # This image is in WikiMedia Public Domain
#     await interface.assert_reply_embed_equals("Test the Embed!", embed)


# @test_collector()
# async def test_embed_regex(interface):
#     patterns = {
#         "title": "Test",
#         "description": r"Random Number: [0-9]+",
#     }
#     await interface.assert_reply_embed_regex("Test the Embed regex!", patterns)


# @test_collector()
# async def test_embed_part_matches(interface):
#     embed = Embed(title="Testing Title.", description="Wrong Description")
#     await interface.assert_reply_embed_equals(
#         "Test the Part Embed!", embed, attributes_to_check=["title"]
#     )


# @test_collector()
# async def test_reply_has_image(interface):
#     await interface.assert_reply_has_image("Post something with an image!")


# @test_collector()
# async def test_reply_on_edit(interface):
#     message = await interface.send_message("Say 'Yeah, that cool!'")
#     await asyncio.sleep(1)
#     await interface.edit_message(message, "Say 'Yeah, that is cool!'")
#     await interface.assert_message_contains(message, "Yeah, that is cool!")


# @test_collector()
# async def test_send_message_in_channel(interface):
#     message = await interface.send_message("Say stuff in another channel")
#     await interface.wait_for_message_in_channel(
#         "here is a message in another channel", 694397509958893640
#     )


# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector, timeout=10)