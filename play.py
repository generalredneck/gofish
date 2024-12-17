import argparse
#import subprocess
from gofish.gofish import GoFish, Player

parser = argparse.ArgumentParser(description='Parser for command line application')
parser.add_argument('--player1', help='First Player python script', dest="first_player")
parser.add_argument('--player2', help='Second Player python script', dest="second_player")
parser.add_argument('--player3', help='Third Player python script', dest="third_player")
parser.add_argument('--player4', help='Fourth Player python script', dest="fourth_player")
arguments = parser.parse_args()
players = []
if hasattr(arguments, 'first_player') and arguments.first_player:
  players.append(Player(id="player1", script=arguments.first_player))
if hasattr(arguments, 'second_player') and arguments.second_player:
  players.append(Player(id="player2", script=arguments.second_player))
if hasattr(arguments, 'third_player') and arguments.third_player:
  players.append(Player(id="player3", script=arguments.third_player))
if hasattr(arguments, 'fourth_player') and arguments.fourth_player:
  players.append(Player(id="player4", script=arguments.fourth_player))

game = GoFish(players)
game.start()
game.end()
#player_processes = []
#for num, script in enumerate(players):
#  player_processes.insert(num,subprocess.Popen(["python3", script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True))
# Create a subprocess and communicate with its stdin
#with subprocess.Popen(["program_to_pipe_to"], stdin=subprocess.PIPE) as proc:
#    proc.stdin.write(b"Hello from Python!\n")
#    proc.stdin.close()
#
    # Wait for the subprocess to finish
#    proc.wait()
