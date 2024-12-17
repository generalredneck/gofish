import sys
import yaml
import logging
from gofish.gofish import Player, Card


class Bot:
  def __init__(self):
    self.me = None

  def updateStatus(self):
    status_yaml = ""
    line = ""
    while line.strip() != "END STATUS":
      status_yaml += line
      line = sys.stdin.readline()
    status = yaml.safe_load(status_yaml)
    logging.debug('Player attribute not set. Syncing status')
    if not self.me:
      logging.debug('Player attribute not set. Syncing status')
      script = sys.executable + " " + " ".join(sys.argv)
      self.me = Player(status["you"]["id"], script)
      for card_str in status["you"]["hand"]:
        self.me.addCard(Card.createfromStr(card_str))
  def listen(self):
    run = True
    logging.debug('Started')
    while run:
      # Check for commands sent to us via the game master.
      line = sys.stdin.readline()
      logging.debug('recieved: %s', line)
      if line.strip() == "STATUS":
        logging.debug('Found STATUS command from game master')
        self.updateStatus()



