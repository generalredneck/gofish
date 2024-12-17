from bot import Bot
import logging
import datetime

class DumbBot(Bot):
  pass

if __name__ == "__main__":
  logging.basicConfig(filename='logs/dumbbot-' + str(datetime.datetime.now()) + '.log', level=logging.DEBUG)
  bot = DumbBot()
  bot.listen()
  #add logging so we can see what the output is
