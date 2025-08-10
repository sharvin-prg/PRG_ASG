#Sharvin S/O Parathi Thasan 
#S10275355A
#Prg_asg.py

import os
import random

TURNS_PER_DAY = 20
WIN_GP = 500

#dictionary to store important info about the player current game state.
player = {
    "name": "",
    "day": 0,
    "gp": 0,
    "pickaxe": 1,
    "inventory": [],
    "inventory_limit": 10,
    "steps": 0,
    "portal": (0, 0),
    "position": (0, 0),
    "potions": 0,
    "has_torch": False
}

game_map = []
fog_map = []
MAP_WIDTH = 0
MAP_HEIGHT = 0

#selling price range for each type of ore
prices = {
    "copper": (1, 3),
    "silver": (5, 8),
    "gold":   (10, 18)
}
#number of ore pieces player can get when mining a single ore tile
ore_yield = {
    "copper": (1, 5),
    "silver": (1, 3),
    "gold":   (1, 2)
}
mineral_symbols = {"C": "copper", "S": "silver", "G": "gold"}

HIGHSCORE_FILE = "highscores.txt"

# Load the saved high scores in a file
def load_highscores():
    scores = []
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    scores.append(eval(line))
    except FileNotFoundError:        #skip without errors if file not found
        pass
    return scores

#save the highscores toa file 
def save_highscores(scores):
    with open(HIGHSCORE_FILE, "w") as f:
        for s in scores[:5]:
            f.write(str(s) + "\n")

# Add a new high score to the list, sort it, and save it
def add_highscore(name, day, steps, gp):
    scores = load_highscores()
    scores.append({"name": name, "day": day, "steps": steps, "gp": gp})
    scores.sort(key=lambda s: (s["day"], s["steps"], -s["gp"]))
    save_highscores(scores)

# Display the top 5 high scores in a formatted table
def show_highscores():
    scores = load_highscores()
    print("\n--- Top 5 Miners ---")
    if not scores:
        print("No scores yet.")
        return
    print("Rank | Name         | Days | Steps | GP")
    print("----------------------------------------")
    for i, s in enumerate(scores[:5], start=1):
        print(f"{i:>4} | {s['name']:<12} | {s['day']:>4} | {s['steps']:>5} | {s['gp']}")

# Load the game map from a file 
def load_map(filename):
    global game_map, MAP_WIDTH, MAP_HEIGHT
    game_map = []
    with open(filename, "r") as f:
        for line in f:
            game_map.append(list(line.rstrip("\n")))
    MAP_HEIGHT = len(game_map)
    MAP_WIDTH = len(game_map[0]) if MAP_HEIGHT > 0 else 0


#create a hidden "fog" layer over the entire map,as unseen (False) until the player explores them.
def initialize_fog():
    global fog_map
    fog_map = [[False for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]


#show 3×3 area around the given (x, y) position as TRUE in  fog map
def clear_fog_around(x, y):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                fog_map[ny][nx] = True



# Main menu for the game + choice input
def main_menu():
    print(" ---------------- Welcome to Sundrop Caves! ---------------- ")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.\n")
    print("How quickly can you get the 500 GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")
    print(" --- Main Menu ---- ")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")
    while True:
        choice = input("Your choice? ").strip().upper()
        if choice in ("N","L","H","Q"):
            return choice
        print("Please enter N, L, H or Q.")



# to start a new game with default player settings + name input
def start_new_game():
    player["name"] = input("Greetings, Miner! What is your name? ").strip()
    player.update({
        "day": 0,
        "gp": 0,
        "pickaxe": 1,
        "inventory": [],
        "inventory_limit": 10,
        "steps": 0,
        "portal": (0, 0),
        "position": (0, 0),
        "potions": 0,
        "has_torch": False
    })
    load_map("level1.txt")
    initialize_fog()
    clear_fog_around(0, 0)
    print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!")
    show_town_menu()



# Load a saved game from a file, if it exists 
def load_saved_game():
    try:
        with open("savegame.txt", "r") as f:
            data = eval(f.read())
        player.update(data["player"])
        player.setdefault("potions", 0)
        player.setdefault("has_torch", False)
        load_map("level1.txt")
        initialize_fog()
        print(f"Welcome back, {player['name']}!")
        show_town_menu()
    except Exception:
        print("No valid savegame found.")



# Save the current game state to a file 
def save_game():
    with open("savegame.txt", "w") as f:
        f.write(str({"player": player}))
    print("Game saved.")



# Check if the player has won the game by reaching the required GP
def check_win_condition():
    if player["gp"] >= WIN_GP:
        print("\n" + "-" * 60)
        print(f"Well done, {player['name']} — you have {player['gp']} GP!")
        print(f"It took you {player['day']} days and {player['steps']} steps.")
        print("You retire happily. You win!")
        print("-" * 60)
        add_highscore(player["name"], player["day"], player["steps"], player["gp"])
        main()



#to sell ore to GP if its in the inventory(backback) 
def sell_ore():
    if not player["inventory"]:
        return
    print("\nSelling your ores...")
    total = 0
    for ore in player["inventory"]:
        if ore in prices:
            low, high = prices[ore]
            total += random.randint(low, high)
    player["gp"] += total
    player["inventory"].clear()   #empty backpack after selling
    print(f"Total GP earned: {total}")
    check_win_condition()


#upgrade player backpack to increase inventory limit
def upgrade_backpack():
    cost = player["inventory_limit"] * 2
    if player["gp"] >= cost:
        player["gp"] -= cost
        player["inventory_limit"] += 2
        print(f"Backpack upgraded! New capacity: {player['inventory_limit']}")
    else:
        print("Not enough GP.")



#upgrade player pickaxe to mine silver and gold ores
def upgrade_pickaxe():
    if player["pickaxe"] >= 3:
        print("Pickaxe already at Level 3 (max).")
        return
    if player["pickaxe"] == 1:
        cost = 50
        next_text = "Level 2 (mine silver)"
    else:
        cost = 150
        next_text = "Level 3 (mine gold)"
    print(f"Upgrade to {next_text} for {cost} GP? (Y/N)")
    while True:
        ans = input("> ").strip().upper()
        if ans == "Y":
            if player["gp"] >= cost:
                player["gp"] -= cost
                player["pickaxe"] += 1
                print(f"Pickaxe upgraded! New level: {player['pickaxe']}")
            else:
                print("Not enough GP.")
            break
        elif ans == "N":
            print("No upgrade bought.")
            break
        else:
            print("Please enter Y or N.")



#buy stamina to restore 5 turns in the mine
def buy_potion():
    cost = 20
    if player["gp"] >= cost:
        player["gp"] -= cost
        player["potions"] += 1
        print("You bought a Stamina Potion. (+5 turns when used in the mine)")
    else:
        print("Not enough GP.")


#buy magic torch to increase viewport size in the mine
def buy_magic_torch():
    if player["has_torch"]:
        print("You already own the Magic Torch.")
        return
    cost = 50
    if player["gp"] >= cost:
        player["gp"] -= cost
        player["has_torch"] = True
        print("You bought the Magic Torch! Viewport is now 5x5 in the mine.")
    else:
        print("Not enough GP.")



#enter shop to buy item
def buy_stuff():
    while True:
        print("\n ----------------------- Shop Menu -------------------------")
        print(f"(B)ackpack upgrade to carry {player['inventory_limit'] + 2} items for {player['inventory_limit'] * 2} GP")
        if player["pickaxe"] == 1:
            print("(P)ickaxe upgrade to Level 2 (silver) for 50 GP")
        elif player["pickaxe"] == 2:
            print("(P)ickaxe upgrade to Level 3 (gold) for 150 GP")
        else:
            print("(P)ickaxe upgrade (MAX)")
        print("(S)tamina potion (+5 turns) for 20 GP")
        if not player["has_torch"]:
            print("(M)agic torch for 50 GP (5x5 viewport)")
        else:
            print("(M)agic torch (OWNED)")
        print("(L)eave shop")
        print("-----------------------------------------------------------")
        print(f"GP: {player['gp']}   Potions: {player['potions']}")
        choice = input("Your choice? ").strip().upper()
        if choice == "B":
            upgrade_backpack()
        elif choice == "P":
            upgrade_pickaxe()
        elif choice == "S":
            buy_potion()
        elif choice == "M":
            buy_magic_torch()
        elif choice == "L":
            break
        else:
            print("Enter B, P, S, M or L.")



#show updated player info 
def show_player_info():
    print("\n ----- Player Information -----")
    print(f"Name: {player['name']}")
    print(f"Current position: {player['position']}")
    print(f"Pickaxe level: {player['pickaxe']} (1=copper,2=silver,3=gold)")
    gold = player["inventory"].count("gold")
    silver = player["inventory"].count("silver")
    copper = player["inventory"].count("copper")
    print(f"Gold: {gold}  Silver: {silver}  Copper: {copper}")
    print("-" * 30)
    print(f"Load: {len(player['inventory'])} / {player['inventory_limit']}")
    print(f"GP: {player['gp']}")
    print(f"Steps taken: {player['steps']}")
    print(f"Potions: {player['potions']}  Torch: {'Yes' if player['has_torch'] else 'No'}")


#show the mine map with player position and portal
def show_mine_map():
    print("\n+------------------------------+")
    for y in range(MAP_HEIGHT):
        row = "|"
        for x in range(MAP_WIDTH):
            if player["position"] == (x, y):
                row += "M"
            elif (x, y) == player["portal"]:
                row += "P"
            elif fog_map[y][x]:
                row += game_map[y][x]
            else:
                row += "?"
        row += "|"
        print(row)
    print("+------------------------------+")



