import os
import random
import subprocess
from dataclasses import dataclass, field
import yaml
import time
import re
import sys

SUITS = ['H', 'D', 'C', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class VerboseSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

@dataclass
class Card:
  rank: str
  suit: str
  def __post_init__(self):
    self.validateRank()
    self.validateSuit()
  @staticmethod
  def createFromStr(string:str):
    suit = string[-1]
    rank = string[:-1]
    return Card(rank, suit)
  def __str__(self):
    return f"{self.rank}{self.suit}"
  def validateRank(self):
    if self.rank not in RANKS:
      raise Exception("Value is not a valid card rank.")
  def validateSuit(self):
    if self.suit not in SUITS:
      raise Exception("Suit must be one of H, D, C, or S")

class Deck:
  def __init__(self):
    self.cards = []
    for suit in SUITS:
      for rank in RANKS:
        self.cards.append(Card(rank, suit))
  def deal(self):
    return self.cards.pop()
  def burn(self, card: Card):
    self.cards.insert(0, card)
  def shuffle(self):
    random.shuffle(self.cards)

@dataclass
class Player:
  id: str
  script: str
  hand: list[Card] = field(default_factory=list)
  books: list[str] = field(default_factory=list)
  def __post_init(self):
    self.subprocess = None
  def addToHand(self, card: Card):
    self.hand.append(card)
  def playCard(self, card: Card):
    index = self.hand.index(card)
    if index:
      card = self.hand.pop(index)
    return index
  def createBook(self, rank):
    cards = []
    for suit in SUITS:
      card_to_find = Card(rank, suit)
      index = self.hand.index(card_to_find)
      if not index:
        raise Exception(f"{card_to_find} was not in players hand")
      cards.append(card_to_find)
    for c in cards:
      self.playCard(c)
    self.books.append(rank)
  def __str__(self):
    return self.id
  def startScript(self):
    self.subprocess = subprocess.Popen([sys.executable, self.script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=0)
    os.set_blocking(self.subprocess.stdout.fileno(), False)
    # Wait a bit because it seems to help with stdout parsing.
    time.sleep(1)
    success = True
    try:
      value = self.readLine()
      if value.strip() != "READY":
        success = False
    except InvalidBotResponse:
      print("Player could not be ready")
      success = False
      self.subprocess.terminate()
    return success
  def readLine(self):
    line = ""
    start_time = time.time()
    current_time = start_time
    end_time = start_time + 5
    while not line and current_time < end_time:
      time.sleep(1)
      try:
        line = self.subprocess.stdout.readline()
      except TypeError:
        pass
      current_time = time.time()
    if current_time >= end_time:
      raise InvalidBotResponse("Took longer than 5 seconds.")
    print(f"##FROM:{self.id}##")
    print(line)
    return line


class GoFish:
  def __init__(self, players: list[Player]):
    if not 2 <= len(players) <= 5:
      raise Exception("game requires 2-5 players")
    self.deck = Deck()
    self.currentPlayer = None
    self.players = {}
    for player in players:
      if player.startScript():
        self.players[player.id] = player
    if not 2 <= len(self.players) <= 5:
      raise Exception("game requires 2-5 players")


  def sendGameState(self):
    state = {}
    state["current_player"] = self.currentPlayer.id
    state["pool_empty"] = len(self.deck.cards) == 0
    state["players"] = {}
    for player in self.players.values():
      state["players"][player.id] = {
        "id": player.id,
        "cards_in_hand": len(player.hand),
        "books": player.books
      }
    for player in self.players.values():
      hand = []
      for card in player.hand:
        hand.append(str(card))
        you = {
          "you":{
            "id": player.id,
            "hand": hand,
            "books": player.books,
          }
        } | state
        self.messageToPlayer(player.id, "STATUS\n" + yaml.dump(you, Dumper=VerboseSafeDumper) + "\nEND STATUS")

  def startTurn(self):
    self.messageToAll("TURN START")
    if not self.currentPlayer:
      self.currentPlayer = self.players[random.choice(list(self.players.keys()))]
      self.messageToAll(f"{self.currentPlayer} will be first.")
    self.sendGameState()
    self.messageToAll(f"GO {self.currentPlayer}")

  def listenForCurrentPlayerPlay(self):
    # Look for f"{oppenent_id} do you have any {rank}s"
    # return opponent and rank
    # throw and exception if
    # - player has crashed
    # - player takes longer than 5 secs to respond
    # - player asked for a card not in their hand
    # - player didn't respond in the correct format
    # - player replies with an invalid opponent
    #return opponent, rank
    line = ""
    while line.strip() == "":
      line = self.currentPlayer.readLine()
    result = re.search("^(.*) do you have any ([2-9]|10|[JQKA])s?$", line.strip())
    if not result:
      raise InvalidBotResponse("Asked for cards incorrectly.")
    if result.group(1) in self.players and result.group(1) != self.currentPlayer.id:
      opponent = self.players[result.group(1)]
    else:
      raise InvalidBotResponse("Provided an invalid opponent.")
    if result.group(2):
      rank = result.group(2)
    else:
      raise InvalidBotResponse("")
    #TODO: Check for cards in hand
    return opponent, rank

  def messageToPlayer(self, player_id:str, data):
    # Log
    print(f"##TO:{player_id}##")
    print(data)
    # Send to STDIN of PLayer
    self.players[player_id].subprocess.stdin.write(data + "\n")
    self.players[player_id].subprocess.stdin.flush()

  def messageToAll(self, data):
    # Log
    print("##ALL##")
    print(data)
    # Send to STDIN of all players
    for player in self.players.keys():
      self.players[player].subprocess.stdin.write(data + "\n")
      self.players[player].subprocess.stdin.flush()

  def start(self):
    self.deck.shuffle()
    num_of_players = len(self.players)
    starting_hand = 5
    if 2 <= num_of_players <= 3:
      starting_hand = 7
    for c in range(starting_hand):
      for n in self.players.keys():
        self.players[n].hand.append(self.deck.deal())
    game_end = False
    while not game_end:
      # Start a turn
      self.startTurn()
      # Listen
      continue_turn = True
      try:
        opponent, rank = self.listenForCurrentPlayerPlay()
      except InvalidBotResponse as e:
        continue_turn = False
        #Kick Player out
        self.messageToAll(f"KICKED {self.currentPlayer.id} " + str(e) )
        self.kickPlayer(self.currentPlayer.id)
      #if continue_turn:
        #self.askPlayer
        # Check Opponents Respance
      self.endTurn()
      if num_of_players < 2:
        game_end = True
    # Determine Winner


  def endTurn(self):
    player_ids = list(self.players)
    index = player_ids.index(self.currentPlayer.id)
    new_player = (index + 1) % len(player_ids)
    self.currentPlayer = self.players[player_ids[new_player]]
    # change player to next player
  def end(self):
    for player in self.players.values():
      print(f"KILLING {player.id}")
      player.subprocess.terminate()
  def kickPlayer(self, player_id):
    player = self.players[player_id]
    player.subprocess.terminate()
    for card in player.hand:
      self.deck.burn(card)
    for rank in player.books:
      for suit in SUITS:
        self.deck.burn(Card(rank, suit))
    self.deck.shuffle()

class InvalidBotResponse(Exception):
  pass
