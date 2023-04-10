import pygame
from pygame.locals import *
import sys
from random import *
from pygame.font import *


BOARD_SIZE = 10
        
BOARD_EMPTY = 0
BOARD_MISS = 1
BOARD_HIT = 2
BOARD_INTACT = 3

CARRIER_LEN = 5
BATTLESHIP_LEN = 4
CRUIZER_LEN = 4
SUBMARINE_LEN = 3
DESTROYER_LEN = 2
WINNER_SCORE = CARRIER_LEN + BATTLESHIP_LEN + CRUIZER_LEN + SUBMARINE_LEN + DESTROYER_LEN
ONE_SPOT_LEN = 1

NOBODY_WIN_YET = 0
COMPUTER_WIN = 1
PLAYER_WIN = 2

HORIZONTAL = 0
VERTICAL = 1

EAST = (1, 0)
WEST = (-1, 0)
NORTH = (0, 1)
SOUTH = (0, -1)
DIR = [EAST, WEST, NORTH, SOUTH]

ALL_SHIPS = [('Carrier', 5), ('Battleship', 4), ('Cruiser', 4), ('Submarine', 3), ('Destroyer', 2)]
FLEET_AMOUNT = 5

# model
class Game:
    

    def __init__(self):

        self.player_grid = [BOARD_SIZE * [BOARD_EMPTY] for _ in range(BOARD_SIZE)]
        self.AI_grid = [BOARD_SIZE * [BOARD_EMPTY] for _ in range(BOARD_SIZE)]
        self.player_fleet = []
        self.AI_fleet = []

        self.target_lens = [ONE_SPOT_LEN, DESTROYER_LEN, SUBMARINE_LEN, CRUIZER_LEN, BATTLESHIP_LEN, CARRIER_LEN]
        self.curr_target = None

        self.winner = NOBODY_WIN_YET
        self.winning_squares = []

    def check_win(self,side):
        total_hit = sum((1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if side[i][j] == BOARD_HIT))

        if total_hit == WINNER_SCORE:
            if side == self.player_grid:
                self.winner = COMPUTER_WIN
            else:
                self.winner = PLAYER_WIN

    def check_placement(self, x, y, l, ort, side):
        dx, dy = EAST if ort == HORIZONTAL else NORTH

        if ort == HORIZONTAL:
            if x + l - 1 >= BOARD_SIZE:
                return False
        else:
            if y + l - 1 >= BOARD_SIZE:
                return False

        for _ in range(l):
            if side[x][y] == BOARD_EMPTY:
                x += dx
                y += dy
            else:
                return False

        return True
    
    def AI_check_qualified_horizontal_spots(self, x, y, l):
        dx, dy = EAST

        if x + l - 1 >= BOARD_SIZE:
                return False

        for _ in range(l):
            if self.player_grid[x][y] != BOARD_MISS and self.player_grid[x][y] != BOARD_HIT:
                x += dx
                y += dy
            else:
                return False

        return True

    def AI_directional_check(self, x, y, l, d):
        dx, dy = d

        if dy == 0:
            if x + (l - 1)  * dx >= BOARD_SIZE or x + (l - 1) * dx < 0:
                return False
        else:
            if y + (l - 1) * dy >= BOARD_SIZE or y + (l - 1) * dy < 0:
                return False

        for _ in range(l):
            if self.player_grid[x][y] != BOARD_MISS and self.player_grid[x][y] != BOARD_HIT:
                x += dx
                y += dy
            else:
                return False
        return True

    def check_sink(self, fleet):

        if fleet == self.player_fleet:
            grid = self.player_grid
        else:
            grid = self.AI_grid
        
        sink_list = []
        for i in range(FLEET_AMOUNT):
            ship,l = ALL_SHIPS[i]
            sink = True

            if fleet[i] != None:
                ort, x , y = fleet[i]
                dx, dy = EAST if ort == HORIZONTAL else NORTH


                for _ in range(l):
                    if grid[x][y] == BOARD_HIT:
                        x += dx
                        y += dy
                    else:
                        sink = False
                        break

            if sink == True:
                sink_list.append((ship, l))
                fleet[i] = None
            
        return sink_list

    def AI_fleet_assemble(self, x, y, l, ort):
        if self.check_placement(x, y, l, ort, self.AI_grid):
            for _ in range(l):
                self.AI_grid[x][y] = BOARD_INTACT
                if ort == HORIZONTAL:
                    x += 1
                else:
                    y += 1
            return True
        else:
            return False

    def leftships(self):

        pf = self.player_fleet
        ls = []

        for i in range(FLEET_AMOUNT):
            _, l = ALL_SHIPS[i]
            if pf[i] != None:
                ls.append(l)

        return ls

    def init_scorer(self):
       
        spot_x = spot_y = None
        qualified_spots = []
        
        while spot_x == None and spot_y == None:
            target = self.curr_target
            leftships = self.leftships()
            for j in range(BOARD_SIZE):
                for i in range(BOARD_SIZE):
                    if self.AI_check_qualified_horizontal_spots(i, j, target):
                        qualified_spots.append(i)
                if qualified_spots == []:
                    continue

                qualified_spots_scores = len(qualified_spots) * [0]
                if qualified_spots != []:
                    for x in range(len(qualified_spots)):
                        for d in DIR:
                            for m in leftships:
                                if self.AI_directional_check(qualified_spots[x], j, m, d):
                                    qualified_spots_scores[x] += m
                                    break
                    spot_x = qualified_spots[qualified_spots_scores.index(max(qualified_spots_scores))]
                    spot_y = j
                    break

            if qualified_spots == []:
                self.curr_target = self.target_lens.pop()

            if spot_x != None and spot_y != None:
                return spot_x, spot_y


    def player_play(self, x, y):
        checkspot = self.AI_grid[x][y]
        if checkspot == BOARD_EMPTY:
            self.AI_grid[x][y] = BOARD_MISS
        elif checkspot == BOARD_INTACT:
            self.AI_grid[x][y] = BOARD_HIT 

        self.check_win(self.AI_grid)

    def AI_play(self):

        spot_x, spot_y = self.init_scorer()       
        checkspot = self.player_grid[spot_x][spot_y]

        if checkspot == BOARD_EMPTY:
            self.player_grid[spot_x][spot_y] = BOARD_MISS
        elif checkspot == BOARD_INTACT:
            self.player_grid[spot_x][spot_y] = BOARD_HIT

        self.check_win(self.player_grid)

def AI_init():
    ort = randint(HORIZONTAL, VERTICAL)
    x = randint(0, BOARD_SIZE - 1)
    y = randint(0, BOARD_SIZE - 1)
    return ort, x, y

def AI_ship_placement(init, rpl, game):
    fleet_num = 0

    for i in range(FLEET_AMOUNT):
        ship, l = ALL_SHIPS[i]
        while fleet_num != i + 1:
            loc = init()
            ort, x, y = loc

            if game.AI_fleet_assemble(x, y, l, ort):
                fleet_num += 1
                game.AI_fleet.append(loc)
            else:
                print(rpl)

        print(f'{ship}({l}) Positioning Complete')

# view

Blue = (0, 0, 255)
White = (255, 255, 255)
Yellow = (255, 255, 0)
Red = (255, 0, 0)
Green = (0, 255, 0)
Black = (0, 0, 0)

Square = 30
Radius = 13
BoardWidth = 25 * Square
BoardHeight = 13 * Square
TextSpace = 2 * Square
BoardSize = 10 * Square


def draw(game, surface, prompt = None, prompt_space = TextSpace, t_init = True):
    

    def player_init_draw(game, surface, prompt):
        font = SysFont(None, 15)
        init_text = font.render(prompt, True, Red)
        surface.blit(init_text,[Square, Square])

    surface.fill(White)
    pygame.draw.rect(surface, Blue,
                     (prompt_space, 2 * prompt_space, BoardSize, BoardSize)) 
    pygame.draw.rect(surface, Blue,
                     (prompt_space + BoardSize + prompt_space, 2 * prompt_space, BoardSize, BoardSize))


    pColors = [White, Yellow, Red, Green]
    AIColors = [White, Yellow, Red, White]
    for x in range(0, 10):
        for y in range(0, 10):
            playerpos_x, playerpos_y = prompt_space + x * Square, 2 * prompt_space + y * Square
            aipos_x,aipos_y = prompt_space + BoardSize + prompt_space + x * Square, 2 * prompt_space + y * Square

            pygame.draw.circle(surface, pColors[game.player_grid[x][y]],
                                   (playerpos_x + Square // 2, playerpos_y + Square // 2),
                                   Radius)
            pygame.draw.circle(surface, AIColors[game.AI_grid[x][y]],
                                   (aipos_x + Square // 2, aipos_y + Square // 2),
                                   Radius)


    font = SysFont(None, 30)
    for i in range(10):
        coltext = font.render(str(i + 1), True, Black)
        surface.blit(coltext,[prompt_space + i * Square, prompt_space + Square + int(4.5)])
        surface.blit(coltext,[prompt_space + BoardSize + prompt_space + i * Square, prompt_space + Square + int(4.5)])

        rowtext = font.render(chr(ord('A') + i), True, Black)
        surface.blit(rowtext,[Square, 2 * prompt_space + i * Square + int(4.5)])
        surface.blit(rowtext,[Square + BoardSize + prompt_space, 2 * prompt_space + i * Square + int(4.5)])

    if t_init == True:
        player_init_draw(game, surface, prompt)

def initilization(game, surface):
    ht = ['head', 'tail']
    for ship, l in ALL_SHIPS:

        head_x = head_y = 0
        tail_x = tail_y = 0

        while True:
            for end in ht:
                prompt = f'Click the {end} of your {ship}({l}) to be placed.'
                draw(game, surface, prompt)
                pygame.display.update()

                while True:
                    event = pygame.event.wait()
                    if event.type == MOUSEBUTTONDOWN:
                        pos_x, pos_y = event.pos
                        play_x, play_y = int((pos_x - TextSpace) / Square), int((pos_y - 2 * TextSpace) / Square)

                        if 0 <= play_x < BOARD_SIZE and 0 <= play_y < BOARD_SIZE:
                            if game.player_grid[play_x][play_y] != BOARD_INTACT:
                                game.player_grid[play_x][play_y] = BOARD_INTACT

                                if end == 'head':
                                    head_x, head_y = play_x, play_y
                                else:
                                    tail_x, tail_y = play_x, play_y
                        
                                pygame.display.update()
                                break
            
            if head_x > tail_x and head_y == tail_y:
                head_x, tail_x = tail_x, head_x
            elif head_y > tail_y and head_x == tail_x:
                head_y, tail_y = tail_y, head_y


            if head_x == tail_x and abs(head_y - tail_y) + 1 == l and all((game.player_grid[head_x][head_y + i] == 0 for i in range(1, l - 1))):
                for i in range(1, l - 1):
                    game.player_grid[head_x][head_y + i] = BOARD_INTACT

                game.player_fleet.append((VERTICAL, head_x, head_y))
                pygame.display.update()
                break
                
            elif head_y == tail_y and abs(head_x - tail_x) + 1 == l and all((game.player_grid[head_x + i][head_y] == 0 for i in range(1, l - 1))):
                for i in range(1, l - 1):
                    game.player_grid[head_x + i][head_y] = BOARD_INTACT

                game.player_fleet.append((HORIZONTAL, head_x, head_y))
                pygame.display.update()
                break
            else:
                game.player_grid[head_x][head_y] = BOARD_EMPTY
                game.player_grid[tail_x][tail_y] = BOARD_EMPTY
                while True:
                    prompt = f'Incorrect Positioning, please click to confirm to reselect your {ship}({l})\'s head and tail' 
                    draw(game, surface, prompt)
                    pygame.display.update()

                    event = pygame.event.wait()
                    if event.type == MOUSEBUTTONDOWN:
                        break

def prompt_update(redraw, game, surface, player_sunk, AI_sunk):
    if redraw:
        ships = ''
        prompt = ''
        if game.winner > 0:
            if game.winner == 1:
                prompt = f'Winner is Computer. Click to Restart the Game.'
            else:
                prompt = f'You are the Winner. Click to Restart the Game.'
            draw(game, surface, prompt, t_init = True)
            pygame.display.update()
            while True:
                event = pygame.event.wait()
                if event.type == MOUSEBUTTONDOWN:
                    gaming()
        else:
            if player_sunk != []:
                for ship, l in player_sunk:
                    ships += f'{ship}({l}),'
                ships = ships[:-1]
                prompt = f'Your ship(s) {ships} sunk. '

            if AI_sunk != []:
                ships = ''
                for ship, l in AI_sunk:
                    ships += f'{ship}({l}),'
                ships = ships[:-1]
                if prompt == '':
                    prompt = f'AI\'s ship(s) {ships} sunk.'
                else:
                    prompt += f'-----AI\'s ship(s) {ships} sunk.'

        if prompt != '':
            draw(game, surface, prompt, t_init = True)
        else:
            draw(game, surface)
        pygame.display.update()
        redraw = False

def gaming():

    game = Game()
    game.curr_target = game.target_lens.pop()
    AI_ship_placement(AI_init, "Computer Ships Positioning", game)
    pygame.init()
    pygame.display.set_caption('Battleship')
    redraw = True
    surface = pygame.display.set_mode((BoardWidth, BoardHeight + 2 * Square))
    initilization(game, surface)

    player_sunk = []
    AI_sunk = []
    while True:
        prompt_update(redraw, game, surface, player_sunk, AI_sunk)

        while True:
            event = pygame.event.wait()
            if event.type == QUIT:
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:         
                pos_x, pos_y = event.pos
                play_x, play_y = int((pos_x - 2 * TextSpace - BoardSize) / Square), int((pos_y - 2 * TextSpace) / Square)
                pygame.display.update()
                if 0 <= play_x < BOARD_SIZE and 0 <= play_y < BOARD_SIZE and (game.AI_grid[play_x][play_y] == BOARD_EMPTY or game.AI_grid[play_x][play_y] == BOARD_INTACT):
                    game.player_play(play_x, play_y)
                    AI_sunk = game.check_sink(game.AI_fleet)
                    game.AI_play()
                    player_sunk = game.check_sink(game.player_fleet)

                    print('Round Finish')
                    redraw = True
                    break

gaming()