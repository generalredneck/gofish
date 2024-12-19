import sys
import yaml
import logging
import re
from gofish.gofish import Player, Card


class Bot:
  def __init__(self):
    self.me = None
    self.opponents = {}
    self.game_stats = {}

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
    if status["pool_empty"]:
      self.game_stats["pool_empty"] = status["pool_empty"]
  def processTurn(self):
    opponent, rank = self.determinePlay()
    if not rank:
      # My hand is empty Draw
      self.draw()
    else:
      self.ask(opponent, rank)
      # Wait for Reply
      answer = sys.stdin.readline()
      if re.match("go fish", answer, re.IGNORECASE) is not None:
        self.draw()
        # If this draw happens to be what you were asking for, show it and continue
      else:
        match = re.search(r"\b((?:[2-9]|10|[JQKA])[HDCS])(?:,\s*((?:[2-9]|10|[JQKA])[HDCS]))?(?:,\s*((?:[2-9]|10|[JQKA])[HDCS]))?\b", answer, re.IGNORECASE)
        if match:
          # Extract matched cards
          for card in match.groups():
            if card:
              self.addToHand(card)
      self.print("DONE")

  def determinePlay(self):
    # Logic here is used to determine who we are going to ask for a card and
    # what rank we are interested in.

    # Logic for Dumbbot.
    # Always return the very first opponent.
    keys = self.opponents.keys()
    if not keys:
      raise Exception("No opponents!")
    opponent = list(self.opponents.keys())[0]
    # Always return the very first card rank.
    if not self.me.hand:
      # I have no cards
      return False, False
    rank = self.me.hand[0].rank
    return opponent, rank
  def draw(self):
    # Check to see if there are any cards left in the pool
    # If not, Tell game master PASS
    # If there is Tell the game master DRAWING
    # Listen for Card you drew, if there ARE any cards left...
    # add the card to your hand.
    if self.game_stats["pool_empty"]:
      self.print("PASS")
    else:
      self.print("DRAWING")
      card = sys.stdin.readline()
      if card.strip():
        self.addToHand(card.strip())
        return card.strip()
      else:
        raise Exception("Couldn't read card")
    return False
  def addToHand(self, card):
    logging.debug('Recieved a %s', card)
    self.me.addToHand(card)
  def ask(self, opponent, rank):
    self.print(f"{opponent} do you have any {rank}s")
  def createBook(self, rank):
    self.print(f"I created a book of {rank}s")
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
        if line.strip().startswith(self.me.id):
          match = re.search("do you have any ([2-9]|10|[JQKA])s")
          if match.group(1):
            # Search your hand for the cards you need to return.
            pass
