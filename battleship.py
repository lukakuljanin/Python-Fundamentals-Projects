import os
import json
from simple_colors import red, yellow, green, blue, magenta

TILE_COLOURS = {'-': blue, '■': green, 'X': red}
SHIPS_DICT = {'Carrier': 6, 'Battleship': 5, 'Cruiser': 4, 'Submarine': 3, 'Destroyer': 2}
HITS_REQUIRED = sum(SHIPS_DICT.values())
SAVE_FILE = "battleship_save.json"


# Loads game save file
def load_game():
    try:
        # Try to open battleship save file
        with open(SAVE_FILE, 'r') as file:
            state_data = json.load(file)

        # Return save data if found
        return state_data
    
    # Return none if error
    except (Exception, FileNotFoundError):
        print(red(f"\nError loading game, starting no game"))
        return None

# Checks if game was saved
def save_game(save, current_player, p1_board, p2_board, p1_att_board, p2_att_board, p1_hits, p2_hits):
    # Store data as dictionary / json file format
    state_data = {
        "current_player": current_player,
        "p1_hits": p1_hits,
        "p2_hits": p2_hits,
        "p1_board": p1_board,
        "p2_board": p2_board,
        "p1_att_board": p1_att_board,
        "p2_att_board": p2_att_board,
    }

    try:
        # Write the game state to a json file
        with open(SAVE_FILE, 'w') as file:
            json.dump(state_data, file, indent = 4)
        print(green(f"\nGame successfully saved to {SAVE_FILE}\n"))

    except Exception as error:
        print(red(f"\nError saving game: {error}\n"))

    exit()

# Checks if battle ship file exists
def check_save_file():
    loaded_state = None
    
    # Check for saved game
    if os.path.exists(SAVE_FILE):
        choice = input(yellow(f"\nSaved game found! Load from {SAVE_FILE}? (y/n): "))
        if choice.lower() == 'y':
            loaded_state = load_game()

    return loaded_state


# Colours the board tiles depending on the item
def colour_tile(tile):
    return TILE_COLOURS.get(tile, lambda x: x)(tile)

# Makes a 10 by 10 board
def make_board():
    return [['-' for _ in range(10)] for _ in range(10)]

# Places attack marker on attack board
def attack_ship(letter, number, player, current_att_board , current_def_board, hits):
    row = ord(letter) - 65
    col = number - 1

    # If a none empty tile is targeted
    if current_att_board[row][col] != '-':
        print(red("\nPlease attack an empty tile (-)"))
        input(yellow("\nPress 'ENTER' to continue: "))
        return hits, False

    else:
        # If tile is empty, miss
        if current_def_board[row][col] == '-':
            current_att_board[row][col] = '●'
            print_board(player, current_att_board, 'Attack ')
            print(red("\nMiss!"))

        # If tile is a ship, hit
        else:
            current_att_board[row][col] = 'X'
            hits += 1
            print_board(player, current_att_board, 'Attack ')
            print(green("\nHit!"))

            # Check igf player has won   
            if hits == HITS_REQUIRED:
                print(green(f"\nPlayer '{player}' has won! Congrats!"))
                choice = input(yellow("\nWould you like to play again? (y/n): "))

                if choice.lower() == 'y':
                    start_game()

                else:
                    print("\nBye! Thanks for playing!\n")
                    exit()


        input(yellow("\nPress 'ENTER' to continue: "))
        return hits, True
    

# Checks if ship placement is valid
def valid_placement(length, letter, number, direction, current_board):
    # Change letter and number into row and column
    row = ord(letter) - 65
    col = number - 1
    coords = []
    errors = []
    
    # Get coords for ship placement
    for i in range(length):
        if direction == 'R': coords.append((row, col + i))
        elif direction == 'L': coords.append((row, col - i))
        elif direction == 'D': coords.append((row + i, col))
        elif direction == 'U': coords.append((row - i, col))


    # Check if ship placement is out of bounds
    for row, col in coords:
        if row < 0 or row >= 10 or col < 0 or col >= 10:
            # Append error if detected
            errors.append("Ship would be placed out of bounds")
            break


    # Check if ship placement is adjacent to other ships
    found_adjacent_ship = False

    for row, col in coords:
        # Break if adjacent ships were found 
        if found_adjacent_ship:
            break

        # Check all 8 surrounding tiles using delta row and col
        for delta_row in [-1, 0, 1]:
            # Break if adjacent ships were found
            if found_adjacent_ship:
                break
                
            for delta_col in [-1, 0, 1]:
                # Skip current tile
                if delta_row == 0 and delta_col == 0:
                    continue
                
                check_row, check_col = row + delta_row, col + delta_col
                
                # Check if adjacent position is in bounds
                if 0 <= check_row < 10 and 0 <= check_col < 10:
                    # If adjacent tile has a ship and is not part of the ship being placed
                    if current_board[check_row][check_col] == '■' and (check_row, check_col) not in coords:
                        # Raise flag error
                        found_adjacent_ship = True
                        errors.append("Ship must be at least one tile away from other ships")
                        break
    
    if errors:
        print_errors(errors)
        return False

    else:
        return coords

# Takes in errors list and prints them
def print_errors(errors):
    for i in errors:
        print(red(f"\n{i}"))

    input(yellow("\nPress 'ENTER' to continue: "))

# Prints out the player's board
def print_board(player, current_board, board_type):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(magenta(f"Player {player}'s {board_type}Board\n", ['bold', 'underlined']))
    
    # Print letters on left of board and numbers at the bottom
    for i, row in enumerate(current_board):
        print(magenta(chr(i + 65)), ' '.join(colour_tile(tile) for tile in row))
    print('  ' + ' '.join(str(magenta(i + 1)) for i in range(10)))


# Allows users to target other player's ship
def battle_phase(player, current_att_board, current_def_board, hits):
    while True:
        print_board(player, current_att_board, 'Attack ')

        print(green("\nControls:"))
        print("Format: [letter][number]")
        print("Examples: A5, B10")
        print("Special: 'save' to save game, 'xxx' to quit")

        coord = input(yellow("\nEnter the coordinate you would like to attack: "))

        # Handle save input
        if coord.lower() == 'save':
            return current_att_board, hits, True

        # Quit game
        if coord.lower() == 'xxx':
            print("\nBye! Thanks for playing!\n")
            exit()


        # Check if code is valid length
        if len(coord) in range(2, 4):
            try:
                letter = coord[0].upper()
        
                # Handle both single and double digit numbers 
                number = int(coord[1]) if len(coord) == 2 else int(coord[1:3])
            
            except (ValueError, IndexError):
                print(red("\nInvalid format. Coordinate must be letter + number (ex. A5 or B10)"))
                input(yellow("\nPress 'ENTER' to continue: "))
                continue

            errors = []

            # Validate letter (A-J)
            if letter not in "ABCDEFGHIJ": errors.append("Letter must be a letter from A-J")
    
            # Validate number (1-10)
            if number not in range(1, 11): errors.append("Number must be an integer from 1-10")


            # Print errors if any
            if errors:
                print_errors(errors)

            # If valid
            else:
                hits, valid_attack = attack_ship(letter, number, player, current_att_board, current_def_board, hits)
                    
                # Return attack board and hits if attack is valid
                if valid_attack:
                    return current_att_board, hits, False


        # If coord length isn't valid
        else:
            print(red("\nInvalid format. Coordinate must be 2-3 characters long (ex. A5 or B10)"))
            input(yellow("\nPress 'ENTER' to continue: "))
            
            


# ALlows users to place ships on their boards
def place_phase(player, current_board):
    ships = SHIPS_DICT.copy()

    while ships:
        print_board(player, current_board, '')
        
        print(green("\nAvailable ships:"))
        for name, size in ships.items():
            print(f"{name}: {size}")
        
        print(green("\nControls:"))
        print("Format: [length][row][column][direction]")
        print("Examples: 5A1R (Carrier at A1 going right), 3B10L (Cruiser at B10 going left)")
        print("Directions: R = right, L = left, U = up, D = down")
        print("Special: 'x' to reset board, 'xxx' to quit")
        
        code = input(yellow("\nEnter code: "))
    
        # Reset ship placements
        if code.lower() == 'x':
            ships = SHIPS_DICT.copy()
            current_board = make_board()
            print(green("\nAll ships removed!"))
            input(yellow("\nPress 'ENTER' to continue: "))
            continue
    
        # Quit game
        elif code.lower() == 'xxx':
            print("\nBye! Thanks for playing!\n")
            exit()


        # Validate the input code and returns parsed values or error message
        if len(code) in range(4, 6):
            try:
                length = int(code[0])
                letter = code[1].upper()
        
                # Handle both single and double digit numbers 
                if len(code) == 4:
                    number = int(code[2])
                    direction = code[3].upper()
                else:
                    number = int(code[2:4])
                    direction = code[4].upper()
            
            except (ValueError, IndexError):
                print(red("\nInvalid format. Code must be length + letter + number + direction (ex. 5A1D or 4B10D)"))
                input(yellow("\nPress 'ENTER' to continue: "))
                continue

            errors = []

            # Validate ship length exists in available ships
            if length not in ships.values(): errors.append(f"Invalid ship length. Available lengths: {set(ships.values())}")
    
            # Validate letter (A-J)
            if letter not in "ABCDEFGHIJ": errors.append("Letter must be a letter from A-J")
    
            # Validate number (1-10)
            if number not in range(1, 11): errors.append("Number must be an integer from 1-10")
    
            # Validate direction
            if direction not in "RLUD": errors.append("Direction must be R (right), L (left), U (up), or D (down)")
            

            # Print errors if any
            if errors:
                print_errors(errors)

            # If code format is valid, check if ship placement is valid
            else:
                coords = valid_placement(length, letter, number, direction, current_board)

                # Place ship if placement is valid
                if coords:
                    # Place ship on board
                    for row, col in coords:
                        current_board[row][col] = '■'

                    # Remove ship from ships dictionary
                    for ship_name, ship_size in list(ships.items()):
                        if ship_size == length:
                            del ships[ship_name]
                            break

                    # Check if it was the last ship
                    if not ships:
                        print_board(player, current_board, '')
                        print("\nAll ships placed!")
                        confirm = input(yellow("\nAre you satisfied with your ship placement? (y/n): "))
                            
                        if confirm.lower() == 'y':
                            print(green("\nShip placement confirmed!"))
                            input(yellow("\nPress 'ENTER' to continue: "))
                            return current_board 

                        else:
                            # Reset ships and board for the player
                            ships = SHIPS_DICT.copy()
                            current_board = make_board()
                            print("\nResetting your board, place your ships again!")
                            input(yellow("\nPress 'ENTER' to continue: "))


        # If code isn't correct length
        else:
            print(red("\nInvalid format. Code must be 4-5 characters long (ex. 5A1D or 4B10D)"))
            input(yellow("\nPress 'ENTER' to continue: "))


# Main function that starts the game
def start_game():
    # Check if save file exists
    loaded_state = check_save_file()

    # If saved game is loaded
    if loaded_state:
        # Load all game variables from the state
        current_player = loaded_state["current_player"]
        p1_board = loaded_state["p1_board"]
        p2_board = loaded_state["p2_board"]
        p1_att_board = loaded_state["p1_att_board"]
        p2_att_board = loaded_state["p2_att_board"]
        p1_hits = loaded_state["p1_hits"]
        p2_hits = loaded_state["p2_hits"]
        
        # Do a single battle phase for player 2 if it's their turn to finish cycle
        if current_player == 2:
            p2_att_board, p2_hits, save = battle_phase(2, p2_att_board, p1_board, p2_hits)
            if save:
                save_game(2, p1_board, p2_board, p1_att_board, p2_att_board, p1_hits, p2_hits)


    # If new game has started
    else:
        p1_board = place_phase(1, make_board())
        p2_board = place_phase(2, make_board())

        p1_att_board = make_board()
        p2_att_board = make_board()

        p1_hits = p2_hits = 0


    # Battle phase loop
    while True:
        p1_att_board, p1_hits, save = battle_phase(1, p1_att_board, p2_board, p1_hits)
        if save:
            save_game(1, p1_board, p2_board, p1_att_board, p2_att_board, p1_hits, p2_hits)

        p2_att_board, p2_hits, save = battle_phase(2, p2_att_board, p1_board, p2_hits)
        if save:
            save_game(2, p1_board, p2_board, p1_att_board, p2_att_board, p1_hits, p2_hits)


start_game()