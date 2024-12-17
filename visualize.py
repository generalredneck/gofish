import sys
import os
import pygame

# Import the cardsets from the classic sets
from pygame_cards.classics import CardSets, Colors, Level, NumberCard
script_dir = os.path.dirname(os.path.abspath(__file__))

pygame.init()
pygame.font.init()
game_font = pygame.freetype.Font(script_dir + '/fonts/Caveat-Regular.ttf', 36)
size = width, height = 1280, 720

n_rows = 4
h_spacing = -40
v_spacing = 50

hand_card_size = (90,128)
book_card_size = (45,64)

screen = pygame.display.set_mode(size)
bg = pygame.image.load(script_dir + "/images/bg.png")
screen.blit(bg, (0, 0))
game_font.render_to(screen, (1050,0), f"{32} cards in pool", (255,255,255))
book_card = NumberCard("", Level.AS , Colors.HEART)
book_card.graphics.size = book_card_size
hand_card = NumberCard("", 10 , Colors.HEART)
hand_card.graphics.size = hand_card_size
# Show the surface of each cards on the screen
for i in range(4): # Current player.
    row_position = i
    for book_col_position in range(13):
        screen.blit(
            book_card.graphics.surface,
            (
                1280 - (book_col_position * book_card_size[0]),
                (v_spacing) * (1 + row_position) + row_position * hand_card_size[1],
            )
        )
    for j in range(13): # cards in hand of current player.
        col_position = j
        game_font.render_to(screen, (0, (v_spacing) * row_position + 10 + row_position * hand_card_size[1]), f"Player {row_position + 1}", (255,255,255))
        screen.blit(
            hand_card.graphics.surface,
            (
                (h_spacing) * (col_position) + col_position * hand_card_size[0],
                (v_spacing) * (1 + row_position) + row_position * hand_card_size[1],
            ),
        )

pygame.display.update()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    pygame.time.wait(100)
