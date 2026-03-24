#!/usr/bin/env python3

import random
import time

# change to modify pause times
PAUSE_TIME = 0.5

# change to modify speed at which text appears
SLOW_PRINT_DELAY = 0.015

# optional float argument to modify pause time
def pause(multiplier=1.0):
    time.sleep(PAUSE_TIME * multiplier)

# optional float argument to further modify delays between characters
def slow_print(s, multiplier=1.0):
    for char in s:
        print(char, end='', flush=True)
        time.sleep(SLOW_PRINT_DELAY * multiplier)
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
        self.max_items = 8 
        self.player_skip = False
        self.dealer_skip = False
        self.double_damage = False
        self.shells = []
        self.known_shell = None # tracks shells revealed by magnifier/inverter for Dealer

    def deal_items(self, current_items, count):
        new_items = random.sample(ITEM_POOL, count)
        for item in new_items:
            if len(current_items) < self.max_items:
                current_items.append(item)

    def new_round(self):
        slow_print(f"\n╔═════════════════════════════╗", 0.35)
        slow_print(f"║           ROUND {self.round}           ║", 0.35)
        slow_print(f"╚═════════════════════════════╝", 0.35)
        pause()

        total_shells = random.randint(3, 8)
        live_shells = random.randint(1, total_shells - 1)
        blanks = total_shells - live_shells

        self.shells = ["LIVE"] * live_shells + ["BLANK"] * blanks
        random.shuffle(self.shells)
        self.known_shell = None

        slow_print(f"Shells loaded: {total_shells} (random order) | ({live_shells} LIVE, {blanks} BLANK)")
        pause()

        # change to modify item distributions
        items_to_add = 0
        if self.round == 2:
            items_to_add = 2
        elif self.round >= 3:
            items_to_add = 4
        
        if items_to_add > 0:
            self.deal_items(self.player_items, items_to_add)
            self.deal_items(self.dealer_items, items_to_add)
            slow_print(f"{items_to_add} items distributed...")

        self.round += 1

    def use_item(self, item, user="player"):
        slow_print(f"\n{user.capitalize()} uses {item}...")
        pause()

        if item == "cigarettes":
            if user == "player":
                self.player_hp += 1
                slow_print("You take a drag... +1 HP.")
            else:
                self.dealer_hp += 1
                slow_print("Dealer takes a drag... +1 HP.")

        elif item == "magnifier":
            if self.shells:
                result = self.shells[0]
                if user == "player":
                    slow_print(f"You peer closely... next shell is: {result}")
                else:
                    self.known_shell = result # Dealer now knows shell type

        elif item == "saw":
            self.double_damage = True
            slow_print("Next live shot deals DOUBLE damage.")

        elif item == "handcuffs":
            if user == "player":
                self.dealer_skip = True
                slow_print("Dealer's next turn will be skipped.")
            else:
                self.player_skip = True
                slow_print("You are handcuffed, you lose your next turn.")

        elif item == "beer":
            if self.shells:
                removed = self.shells.pop(0)
                slow_print(f"Shotgun racked, {removed} shell ejected.")
                self.known_shell = None # shell racked, Dealer doesn't know shell

        elif item == "inverter":
            if self.shells:
                self.shells[0] = "LIVE" if self.shells[0] == "BLANK" else "BLANK"
                slow_print("Chambered shell inverted.")
                # if dealer previously knew the shell, swap its polarity
                if self.known_shell:
                    self.known_shell = "LIVE" if self.known_shell == "BLANK" else "BLANK"

        elif item == "medicine":
            if random.random() <= 0.4:
                if user == "player": self.player_hp += 2
                else: self.dealer_hp += 2
                slow_print("Success. +2 HP.")
            else:
                if user == "player": self.player_hp -= 1
                else: self.dealer_hp -= 1
                slow_print("Failed. -1 HP.")

        elif item == "phone":
            if self.shells:
                idx = random.randint(0, len(self.shells) - 1)
                slow_print(f"A whisper through the line... Shell #{idx+1} is {self.shells[idx]}")

        elif item == "adrenaline":
            target_items = self.dealer_items if user == "player" else self.player_items
            if target_items:
                stolen = random.choice(target_items)
                target_items.remove(stolen)
                slow_print(f"{user.capitalize()} stole {stolen}.")
                self.use_item(stolen, user=user)

    def shoot(self, target, shooter):
        if not self.shells:
            return None

        slow_print(f"\n{shooter.capitalize()} pulls the trigger...")
        pause()
        shell = self.shells.pop(0)
        self.known_shell = None
        print("*CLICK*...")
        pause(1.5)
        slow_print(f"Shell is {shell}!")
        pause()

        damage = 2 if self.double_damage else 1
        self.double_damage = False

        if shell == "LIVE":
            if target == "player":
                self.player_hp -= damage
                slow_print(f"You took {damage} damage (-{damage} HP).")
            else:
                self.dealer_hp -= damage
                slow_print(f"Dealer took {damage} damage (-{damage} HP).")
            return "SWITCH"
        else:
            slow_print("Nothing happened.")
            # Shooting yourself with a blank keeps your turn (same for Dealer)
            if target == shooter:
                slow_print(f"{shooter.capitalize()} keeps their turn.")
                return "STAY"
            return "SWITCH"

    def player_turn(self):
        if self.player_skip:
            slow_print("\nYou are handcuffed and lose your turn.", 10.0)
            self.player_skip = False
            return

        turn_active = True
        while turn_active and self.shells:
            slow_print(f"\n=== STATUS ===")
            slow_print(f"You: {self.player_hp} HP  |  Dealer: {self.dealer_hp} HP")
            slow_print(f"Shells Remaining: {len(self.shells)}")
            slow_print(f"Your Items: {self.player_items}")
            slow_print(f"Dealer Items: {self.dealer_items}")
            
            slow_print(f"\n--- YOUR TURN ---")
            choice = input(">>> [1] Shoot Self  [2] Shoot Dealer  [Item Name]: ").strip().lower()

            if choice in self.player_items:
                self.player_items.remove(choice)
                self.use_item(choice, user="player")
                if self.is_game_over():
                    return
                continue # using an item doesn't end your turn

            if choice == "1":
                result = self.shoot("player", shooter="player")
                if result == "SWITCH":
                    turn_active = False
            elif choice == "2":
                result = self.shoot("dealer", shooter="player")
                if result == "SWITCH":
                    turn_active = False
            else:
                # forces player to type a valid input
                print('', end='')
                continue
            
            if self.is_game_over():
                return

    def dealer_turn(self):
        if self.dealer_skip:
            slow_print("\nDealer is handcuffed and loses turn.", 10.0)
            self.dealer_skip = False
            return

        turn_active = True
        while turn_active and self.shells:
            slow_print(f"\n--- DEALER'S TURN ---")
            slow_print(f"HP: {self.dealer_hp} | ITEMS: {self.dealer_items}")
            pause()

            # Dealer item logic: if Dealer has items, uses one 40% of the time
            if self.dealer_items and random.random() < 0.4:
                item = random.choice(self.dealer_items)
                self.dealer_items.remove(item)
                self.use_item(item, user="dealer")
                if self.is_game_over(): return
                continue

            # Dealer will shoot you if it knows shell is LIVE
            if self.known_shell == "LIVE":
                target = "player"
            elif self.known_shell == "BLANK":
                # else Dealer shoots self to keep turn if it knows shell is BLANK
                target = "dealer"
            else:
                # else shoots player 60% of the time
                target = "player" if random.random() < 0.6 else "dealer"

            slow_print(f"Dealer shoots {'YOU' if target=='player' else 'itself'}.")
            pause()

            result = self.shoot(target, shooter="dealer")
            if result == "SWITCH":
                turn_active = False
            if self.is_game_over():
                return

    def is_game_over(self):
        return self.player_hp <= 0 or self.dealer_hp <= 0
    
    def print_game_result(self):
        if self.player_hp <= 0:
            pause(1.5)
            slow_print("\nYou died.")
            pause(3.0)
            slow_print("GAME OVER.\n", 50.0)
        elif self.dealer_hp <= 0:
            pause(1.5)
            slow_print("\nDealer died.")
            pause(3.0)
            slow_print("YOU WIN.\n", 50.0)

# main game loop
def main():
    game = Game()
    slow_print("Welcome to Txtshot Roulette!")
    pause(2.0)
    while True:
        game.new_round()
        while game.shells:
            game.player_turn()
            if game.is_game_over():
                game.print_game_result()
                return
            if game.shells:
                game.dealer_turn()
                if game.is_game_over():
                    game.print_game_result()
                    return
        slow_print("\nOut of shells. Reloading...")
        pause()


if __name__ == "__main__":
    main()