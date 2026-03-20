#!/usr/bin/env python3

import random
import time

# change to modify speed at which lines appear
PAUSE_TIME = 1.0

def pause(multiplier=1.0):
    multiplier = 0.5
    time.sleep(PAUSE_TIME * multiplier)

# change to modify speed at which text appears
SLOW_PRINT_DELAY = 0.015

def slow_print(s):
    for char in s:
        print(char, end='', flush=True)
        time.sleep(SLOW_PRINT_DELAY)
    print()

ITEM_POOL = [
    "saw",
    "magnifier",
    "cigarettes",
    "handcuffs",
    "beer",
    "adrenaline",
    "inverter",
    "medicine",
    "phone"
]

class Game:
    def __init__(self):
        self.player_hp = 3
        self.dealer_hp = 3
        self.round = 1

        self.player_items = []
        self.dealer_items = []
        self.max_items = 4

        self.player_skip = False
        self.dealer_skip = False

        self.double_damage = False

    def deal_items(self, count):
        return random.sample(ITEM_POOL, count)

    def new_round(self):
        slow_print(f"\n--- ROUND {self.round} ---")
        pause()

        total_shells = random.randint(3, 6)
        live_shells = random.randint(1, total_shells - 1)
        blanks = total_shells - live_shells

        self.shells = ["LIVE"] * live_shells + ["BLANK"] * blanks
        random.shuffle(self.shells)

        slow_print(f"Shells loaded: {total_shells} (random order)")
        pause(2)

        if self.round == 2:
            self.player_items = self.deal_items(2)
            self.dealer_items = self.deal_items(2)
        elif self.round >= 3:
            self.player_items = self.deal_items(4)
            self.dealer_items = self.deal_items(4)

        self.round += 1

    def use_item(self, item, user="player"):
        slow_print(f"\n{user.capitalize()} uses {item}...")
        pause()

        if item == "cigarettes":
            if user == "player":
                self.player_hp += 1
            else:
                self.dealer_hp += 1
            slow_print("+1 HP!")

        elif item == "magnifier":
            if self.shells:
                slow_print(f"Next shell is: {self.shells[0]}")

        elif item == "saw":
            self.double_damage = True
            slow_print("Next live shot deals DOUBLE damage!")

        elif item == "handcuffs":
            if user == "player":
                self.dealer_skip = True
                slow_print("Dealer's next turn will be skipped!")
            else:
                self.player_skip = True
                slow_print("You will skip your next turn!")

        elif item == "beer":
            if self.shells:
                removed = self.shells.pop(0)
                slow_print(f"Removed a {removed} shell!")

        elif item == "inverter":
            if self.shells:
                self.shells[0] = "LIVE" if self.shells[0] == "BLANK" else "BLANK"
                slow_print("Shell inverted!")

        elif item == "medicine":
            if random.random() < 0.4:
                if user == "player":
                    self.player_hp += 2
                else:
                    self.dealer_hp += 2
                slow_print("+2 HP!")
            else:
                if user == "player":
                    self.player_hp -= 1
                else:
                    self.dealer_hp -= 1
                slow_print("Failed! -1 HP")

        elif item == "phone":
            if self.shells:
                idx = random.randint(0, len(self.shells) - 1)
                slow_print(f"Shell #{idx+1} is {self.shells[idx]}")

        elif item == "adrenaline":
            if user == "player" and self.dealer_items:
                stolen = random.choice(self.dealer_items)
                self.dealer_items.remove(stolen)
                slow_print(f"You stole {stolen}!")
                self.use_item(stolen, user="player")

            elif user == "dealer" and self.player_items:
                stolen = random.choice(self.player_items)
                self.player_items.remove(stolen)
                slow_print(f"Dealer stole {stolen}!")
                self.use_item(stolen, user="dealer")

    def shoot(self, target):
        if not self.shells:
            return None

        slow_print("\nTrigger pulled...")
        pause(2)

        shell = self.shells.pop(0)

        print("*CLICK*...")
        pause(1)

        slow_print(f"It's a {shell} shell!")
        pause(1.5)

        damage = 2 if self.double_damage else 1
        self.double_damage = False

        if shell == "LIVE":
            if target == "player":
                self.player_hp -= damage
                slow_print(f"You took {damage} damage!")
            else:
                self.dealer_hp -= damage
                slow_print(f"Dealer took {damage} damage!")
        else:
            slow_print("Nothing happened.")

        pause(2)
        return shell

    def player_turn(self):
        if self.player_skip:
            slow_print("\nYou are handcuffed and lose your turn!")
            self.player_skip = False
            return

        slow_print("\nYour turn.")
        pause()

        slow_print(f"Your HP: {self.player_hp} | Dealer HP: {self.dealer_hp}")
        slow_print(f"Shells remaining: {len(self.shells)}")
        slow_print(f"Items: {self.player_items}")
        pause()

        choice_check = True
        while choice_check:
            choice = input("Shoot (1 self / 2 dealer), or type item name: ").strip().lower()
    
            if choice in self.player_items:
                self.player_items.remove(choice)
                self.use_item(choice, user="player")
                choice_check = False
                return

            if choice == "1":
                self.shoot("player")
                choice_check = False
            
            if choice == "2":
                self.shoot("dealer")
                choice_check = False
            
            # catch-all for invalid choices, forces choice loop to run again 
            else:
                print('', end='')

    def dealer_turn(self):
        if self.dealer_skip:
            slow_print("\nDealer is restrained and skips turn!")
            self.dealer_skip = False
            return

        slow_print("\nDealer's turn...")
        pause(2)

        # simple AI item usage
        if self.dealer_items and random.random() < 0.5:
            item = random.choice(self.dealer_items)
            self.dealer_items.remove(item)
            slow_print(f"Dealer uses {item}!")
            self.use_item(item, user="dealer")
            return

        slow_print("Dealer raises the shotgun...")
        pause(1.5)
        
        # simple AI target selection
        if random.random() < 0.5:
            target = "player"
        else:
            target = "self"

        slow_print(f"Dealer shoots {'YOU' if target=='player' else 'himself'}.")
        pause(2)

        self.shoot(target)

    def is_game_over(self):
        if self.player_hp <= 0:
            slow_print("\nYou died.")
            pause()
            slow_print("Game over.\n")
            return True
        elif self.dealer_hp <= 0:
            slow_print("\nDealer died.")
            pause()
            slow_print("You win!\n")
            return True
        return False

# Main game loop
def main():
    game = Game()

    while True:
        game.new_round()

        while game.shells:
            game.player_turn()
            if game.is_game_over():
                return

            if game.shells:
                game.dealer_turn()
                if game.is_game_over():
                    return

        print("\nOut of shells. Reloading...")
        pause(2)


if __name__ == "__main__":
    main()
