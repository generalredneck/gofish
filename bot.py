import sys
import yaml
import logging
from gofish.gofish import Player, Card


class Bot:
  def __init__(self):
    self.me = None
    self.opponents = {}

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
        self.me.addToHand(Card.createFromStr(card_str))
    for player in status["players"]:
      if player != self.me.id:
        self.opponents[player] = status["players"][player]
  def processTurn(self):
    opponent, rank = self.determinePlay()
    self.ask(opponent, rank)
  def determinePlay(self):
    # Always return the very first opponent.
    opponent = list(self.opponents.keys())[0]
    # Always return the very first card rank.
    rank = self.me.hand[0].rank
    return opponent, rank
  def ask(self, opponent, rank):
    self.print(f"{opponent} do you have any {rank}s")
  def print(self, value):
    logging.debug("Printed: %s", value)
    print(value, flush=True)
  def listen(self):
    run = True
    logging.debug('Started')
    self.print("READY")
    while run:
      # Check for commands sent to us via the game master.
      line = sys.stdin.readline()
      if line.strip() == "STATUS":
        logging.debug('Found STATUS command from game master')
        self.updateStatus()
      if self.me and isinstance(self.me, Player):
        if line.strip() == f"GO {self.me.id}":
          logging.debug("It's my turn")
          self.processTurn()
        



