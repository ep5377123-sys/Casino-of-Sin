#Room Adventure: Casino of Sin
#Ethan Pineiro
#Last Worked: 12/4/25
#Description: In this game, you must make back 10000$ or else an alien loan shark will blow up planet Earth if you cannot repay your debts.
#The only way to mkae this money back to gamble like your life depends on it (it literally does)
#Save humanity, or be sole real reason it ceases to exit. Will clutch up to save humanity?
from CasinoRooms import Room
import random
from death import death
from winner import victory
import sys
#support for tab completion
try:
    TAB_COMPLETE = True
    import TabCompleter as TC
except ModuleNotFoundError:
    TAB_COMPLETE = False

###########################################################################################
#constants
VERBS = ["go","use", "play", "buy"]
inventory = []
money = 500
choice = ""
answer = ""
beverage = ""
bet = 100
#creates a varibale for effects that stores the effect and its duration
activeEffects = {
    "multiplier": None,
    "multiplierDuration": 0,

    "oddsIncrease": None,
    "oddsIncreaseDuration": 0,

    "seeDealerCards": None,
    "visionDuration": 0
}
# Blackjack state — used by the GUI to track a game across multiple button presses (Claude helped me design this state management system for the blackjack game)
blackjackState = {
    "active": False,
    "deck": [],
    "player_card": [],
    "dealer_card": [],
    "message": ""
}
###########################################################################################


##############################################
# CREATE ROOMS
##############################################
def createRooms():
    rooms = []

    main = Room("Main Floor - Cashier")
    roulette = Room("Roulette Room")
    blackjack = Room("Blackjack Room")
    bar = Room("Bar")
    cockfight = Room("Cockfight Pit")
    wheel = Room("Wheel of Fortune Room")

    main.description = "You stand on the casino's main floor. You owe $10,000 to an alien loan shark, and if you do not get the money earth will explode. Goodluck."
    main.addExit("west", roulette)
    main.addExit("east", wheel)
    rooms.append(main)

    roulette.description = "You're in the Roulette Room. Time to put it all on black."
    roulette.addExit("east", main)
    roulette.addExit("north", blackjack)
    roulette.addItem("wheel", "The roulette wheel spins hypnotically.")
    rooms.append(roulette)

    blackjack.description = "Welcome to the Black Jack Room. Ready to play some cards?."
    blackjack.addExit("south", roulette)
    blackjack.addExit("east", bar)
    blackjack.addItem("table", "A blackjack table with scattered chips.")
    rooms.append(blackjack)

    bar.description = "You're at the bar. You can buy drinks here."
    bar.addExit("west", blackjack)
    bar.addExit("east", cockfight)
    rooms.append(bar)

    cockfight.description = "You're in the cockfighting room, get ready to bet on some chickens."
    cockfight.addExit("west", bar)
    cockfight.addExit("south", wheel)
    rooms.append(cockfight)

    wheel.description = "You're in the Wheel of Fortune Room. Test your luck on the Wheel."
    wheel.addExit("north", cockfight)
    wheel.addExit("west", main)
    rooms.append(wheel)

    return rooms, main


##############################################
# MINI-GAMES
##############################################

def spinTheWheel():
    global money
    wheel_numbers = [0, 100, 200, 500, 1000]
    oddsBoost = activeEffects["oddsIncrease"]

    if activeEffects["oddsIncrease"]:
        probability = [0.52, 0.2 * oddsBoost, 0.1 * oddsBoost, 0.06 * oddsBoost, 0.04 * oddsBoost]
    else:
        probability = [0.6, 0.2, 0.1, 0.06, 0.04]

    def spinWheel():
        return random.choices(wheel_numbers, weights=probability, k=1)[0]

    if money > 0:
        money -= bet
        result = spinWheel()

        if activeEffects["multiplier"]:
            money += int(result * activeEffects["multiplier"])
        else:
            money += result

        reduceEffectDurations()
        return f"Wheel landed on: ${result}! New balance: ${money}"
    return "You're out of money!"


def startCockfight():
    global money, bet

    class Chicken:
        def __init__(self, h, s, d):
            self._health = h
            self._strength = s
            self._defense = d

        def _get_health(self): return self._health
        def _get_strength(self): return self._strength
        def _get_defense(self): return self._defense
        def _set_health(self, h): self._health = h
        def _set_strength(self, s): self._strength = s
        def _set_defense(self, d): self._defense = d

        health = property(_get_health, _set_health)
        strength = property(_get_strength, _set_strength)
        defense = property(_get_defense, _set_defense)

        def calculateAttack(self, opponent_defense):
            # floor at 1 so defense=10 never causes zero damage and an infinite loop
            return max(1, self._strength * (1 - opponent_defense / 10))

        def isStillAlive(self):
            return self._health > 0

    def buildChicken():
        return Chicken(random.randint(50, 100), random.randint(10, 20), random.randint(0, 9))

    if money <= 0:
        return "You're out of money!"

    money -= bet

    ally = buildChicken()
    opponent = buildChicken()
    round_number = 1

    while ally.isStillAlive() and opponent.isStillAlive():
        ally_dmg = ally.calculateAttack(opponent.defense)
        opponent.health -= ally_dmg

        if opponent.isStillAlive():
            enemy_dmg = opponent.calculateAttack(ally.defense)
            ally.health -= enemy_dmg

        round_number += 1

    reduceEffectDurations()

    if ally.isStillAlive():
        if activeEffects["multiplier"]:
            money += int(bet * 2 * activeEffects["multiplier"])
        else:
            money += bet * 2
        return "Your chicken WON!"
    else:
        return "Your chicken LOST..."
    


def startBlackjack(): #calls the black jack game. got this code from https://www.geeksforgeeks.org/python/blackjack-console-game-using-python/ originally, but modified it for the gui with Claude
    global money, blackjackState, bet

    card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    cards_list = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [(card, category) for category in card_categories for card in cards_list]

    def card_value(card):
        if card[0] in ['Jack', 'Queen', 'King']:
            return 10
        elif card[0] == 'Ace':
            return 11
        else:
            return int(card[0])

    if money <= 0:
        return "You do not have enough money to play"

    money -= bet

    # Shuffle and deal
    random.shuffle(deck)
    player_card = [deck.pop(), deck.pop()]
    dealer_card = [deck.pop(), deck.pop()]

    # Save state so Hit/Stand buttons can continue the hand (Claude's idea)
    blackjackState["active"] = True
    blackjackState["deck"] = deck
    blackjackState["player_card"] = player_card
    blackjackState["dealer_card"] = dealer_card
    blackjackState["card_value"] = card_value

    if activeEffects["seeDealerCards"]:
        dealer_show = f"{dealer_card[0][0]} of {dealer_card[0][1]} & {dealer_card[1][0]} of {dealer_card[1][1]}"
    else:
        dealer_show = f"{dealer_card[0][0]} of {dealer_card[0][1]}"

    player_score = sum(card_value(c) for c in player_card)

    return (f"Dealer shows: {dealer_show}\n"
            f"Cards Player Has: {[c[0] for c in player_card]}\n"
            f"Score Of The Player: {player_score}\n"
            f"Hit or Stand?")


def playBlackjack(): #called when the player clicks Hit or Stand. this is what plays the actual game.
    global money, choice, blackjackState, bet

    # If no hand is active, deal a new one
    if not blackjackState["active"]:
        return startBlackjack()

    card_value = blackjackState["card_value"]
    deck        = blackjackState["deck"]
    player_card = blackjackState["player_card"]
    dealer_card = blackjackState["dealer_card"]

    choice = choice.lower()

    if choice == "hit":
        new_card = deck.pop()
        player_card.append(new_card)

    player_score = sum(card_value(card) for card in player_card)
    dealer_score = sum(card_value(card) for card in dealer_card)

    # Player bust — hand over
    if player_score > 21:
        blackjackState["active"] = False
        reduceEffectDurations()
        return (f"Cards Player Has: {[c[0] for c in player_card]}\n"
                f"Score Of The Player: {player_score}\n"
                f"Dealer Wins (Player Loss Because Player Score is exceeding 21)\n"
                f"Balance: ${money}")

    # After a hit but not bust — still playing
    if choice == "hit":
        return (f"Cards Player Has: {[c[0] for c in player_card]}\n"
                f"Score Of The Player: {player_score}\n"
                f"Hit or Stand?")

    # Player chose Stand — dealer draws to 17
    if choice == "stand":
        while dealer_score < 17:
            new_card = deck.pop()
            dealer_card.append(new_card)
            dealer_score += card_value(new_card)

        blackjackState["active"] = False

        #couldnt figure out how to get the text to display inside of the game, so Claude made a header that stores the common text that is displayed in all outcomes of the hand to avoid having to repeat it in every outcome and to make it easier to display the text in the gui
        header = (f"Cards Dealer Has: {[c[0] for c in dealer_card]}\n"
                  f"Score Of The Dealer: {dealer_score}\n"
                  f"Cards Player Has: {[c[0] for c in player_card]}\n"
                  f"Score Of The Player: {player_score}\n")

        # Dealer bust — player wins
        if dealer_score > 21:
            if activeEffects["multiplier"]:
                money += int(bet * 2 * activeEffects["multiplier"])
            else:
                money += bet * 2
            reduceEffectDurations()
            return header + f"Player wins (Dealer Loss Because Dealer Score is exceeding 21)\nBalance: ${money}"

        # Player wins
        elif player_score > dealer_score:
            if activeEffects["multiplier"]:
                money += int(bet * 2 * activeEffects["multiplier"])
            else:
                money += bet * 2
            reduceEffectDurations()
            return header + f"Player wins (Player Has High Score than Dealer)\nBalance: ${money}"

        # Dealer wins
        elif dealer_score > player_score:
            reduceEffectDurations()
            return header + f"Dealer wins (Dealer Has High Score than Player)\nBalance: ${money}"

        # Tie
        else:
            money += bet  # return the bet
            reduceEffectDurations()
            return header + f"It's a tie.\nBalance: ${money}"


def playRoulette():
    """Uses the global `answer` variable ('red' or 'black')."""
    global money, answer, bet

    if money <= 0:
        return "You're out of money!"

    ans = answer.lower()
    if ans not in ("red", "black"):
        return "Choose Red or Black first."

    if money < bet:
        return "Not enough money to bet!"

    money -= bet

    if activeEffects["oddsIncrease"]:
        boost = activeEffects["oddsIncrease"]
        if ans == "red":
            result = random.choices(["red", "black"], weights=[0.5 * boost, 0.5], k=1)[0]
        else:
            result = random.choices(["red", "black"], weights=[0.5, 0.5 * boost], k=1)[0]
    else:
        result = random.choice(["red", "black"])

    if ans == result:
        if activeEffects["multiplier"]:
            money += int(bet * 2 * activeEffects["multiplier"])
        else:
            money += bet * 2
        outcome = "You win!"
    else:
        outcome = "You lose!"

    reduceEffectDurations()
    return f"Ball landed on {result}! {outcome} Balance: ${money}"


##############################################
# SHOP  (GUI version — no input() calls)
##############################################

# Consumable definitions live at module level so the GUI can reference them
class Consumable:
    def __init__(self, n, p, e, et, d, dr):
        self._name = n
        self._price = p
        self._effect = e
        self._effectType = et
        self._description = d
        self._duration = dr

    def __repr__(self): return self._name

    def _get_name(self): return self._name
    def _get_price(self): return self._price
    def _get_effect(self): return self._effect
    def _get_effectType(self): return self._effectType
    def _get_description(self): return self._description
    def _get_duration(self): return self._duration
    def _set_name(self, n): self._name = n
    def _set_price(self, p): self._price = p
    def _set_effect(self, e): self._effect = e
    def _set_effectType(self, et): self._effectType = et
    def _set_description(self, d): self._description = d
    def _set_duration(self, dr): self._duration = dr

    name = property(_get_name, _set_name)
    price = property(_get_price, _set_price)
    effect = property(_get_effect, _set_effect)
    effectType = property(_get_effectType, _set_effectType)
    description = property(_get_description, _set_description)
    duration = property(_get_duration, _set_duration)


SHOP_ITEMS = [
    Consumable("Beer",          100,  2,  "multiplier",    "Gambling profits increase by 1.5x for every win.", 3),
    Consumable("Vodka",         200, 1.2,  "oddsIncrease",  "Your odds of winning increase by 20%.",            2),
    Consumable("Powdered Sugar",300, True, "seeDealerCards","You can see both dealer cards in Blackjack.",      5),
]


def buyItem(item_name):
    """Buy a shop item by name. Returns a result message string."""
    global money, inventory

    item = next((i for i in SHOP_ITEMS if i.name == item_name), None)
    if item is None:
        return "That item doesn't exist."
    if any(i.name == item_name for i in inventory):
        return "You already own that item!"
    if money < item.price:
        return f"You can't afford {item.name} (${item.price}). You have ${money}."

    money -= item.price
    inventory.append(item)
    return f"You bought {item.name} for ${item.price}! Balance: ${money}"


def useItem(item_name):
    """Use an inventory item by name. Returns a result message string."""
    global inventory

    item = next((i for i in inventory if i.name == item_name), None)
    if item is None:
        return "You don't have that item."

    if item.effectType == "multiplier":
        activeEffects["multiplier"] = item.effect
        activeEffects["multiplierDuration"] = item.duration
        msg = f"You drink the {item.name}. Winnings multiplied by {item.effect}x for {item.duration} rounds!"

    elif item.effectType == "oddsIncrease":
        activeEffects["oddsIncrease"] = item.effect
        activeEffects["oddsIncreaseDuration"] = item.duration
        msg = f"You chug the {item.name}. Odds boosted for {item.duration} rounds!"

    elif item.effectType == "seeDealerCards":
        activeEffects["seeDealerCards"] = item.effect
        activeEffects["visionDuration"] = item.duration
        msg = f"Your eyes widen... You can see the dealer's cards for {item.duration} rounds!"

    else:
        msg = "This item has no effect yet."

    inventory.remove(item)
    return msg


# legacy alias so GUI_Room_Adventure.py import still works
def goShop():
    global money
    
    class Consumables: #creates the class for items the player can buy at the bar
        def __init__(self, n, p, e, et, d, dr):
            self._name = n
            self._price = p
            self._effect = e
            self._effectType = et
            self._description = d
            self._duration = dr
        #Generated by chatgpt to get rid of memory location
        def __repr__(self):
            return self._name
        # getters    
        def _get_name(self): return self._name
        def _get_price(self): return self._price
        def _get_effect(self): return self._effect
        def _get_effectType(self): return self._effectType
        def _get_description(self): return self._description
        def _get_duration(self): return self._duration

        # setters
        def _set_name(self, n): self._name = n
        def _set_price(self, p): self._price = p
        def _set_effect(self, e): self._effect = e
        def _set_effectType(self, et): self._effectType = et
        def _set_description(self, d): self._description = d
        def _set_duration(self, dr): self._duration = dr
        
        #properties
        name = property(_get_name, _set_name)
        price = property(_get_price, _set_price)
        effect = property(_get_effect, _set_effect)
        effectType = property(_get_effectType, _set_effectType)
        description = property(_get_description, _set_description)
        duration = property(_get_duration, _set_duration)

    # creates a list for consumables
    consumables = []
    consumables.append(Consumables("Beer", 100, 1.5, "multiplier",
                      "Gambling profits increase by 1.5x for every win.", 3))

    consumables.append(Consumables("Vodka", 200, 1.2, "oddsIncrease",
                      "Your odds of winning increase by 20%.", 2))

    consumables.append(Consumables("Powdered Sugar", 300, True, "seeDealerCards",
                      "You can now see both dealer cards in Blackjack.", 5))

    # asks user what they want to buy
    print("What would you like to buy today?")
    print("a) Beer (Mulitplies your winnings by 1.5x for 3 Rounds)\nb) Vodka (Increases your odds of winning in Roulette and the Wheel of Fortune by 20% for 2 Rounds)\nc) Powdered Sugar (Allows you to see both of the dealer's cards for 5 Rounds)\n> ").lower()


    beverage = item.lower()
    if beverage == "Beer": #buys beer
        item = consumables[0]
    elif beverage == "Vodka": #buys vodka
        item = consumables[1]
    elif beverage == "Powdered Suagr": #buys powdered sugar
        item = consumables[2]
    else:
        return("That is an invalid choice.")
    if any(i.name == item.name for i in inventory):
        return("You already own this item and cannot buy another one.")
    if money < item.price:
        return("You cannot afford that... SCRAM")
    inventory.append(item)
    money -= item.price
    return(f"You bought {item.name}!")

def bottomsUp(): #allows the Player to Use the item in their inventory
    global inventory, money

    if len(inventory) == 0:
        print("You don’t have anything to use.")
        return

    print("\nYour Inventory:")
    for i, item in enumerate(inventory): #generated by chatgpt
        print(f"{i+1}) {item.name} - {item.description} (Effect: {item.effectType})")

    choice = input("\nWhich item do you want to use? Enter number: ")

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(inventory):
        print("Invalid choice.")
        return
    
    item = inventory[int(choice) - 1]

    # -----------------------------------------
    #apply effects
    # -----------------------------------------
    if item.effectType == "multiplier":
        print(f"You drink the {item.name}. Your profits are now multiplied by {item.effect}x!")
        activeEffects["multiplier"] = item.effect
        activeEffects["multiplierDuration"] = item.duration

    elif item.effectType == "oddsIncrease":
        print(f"You chug the {item.name}. Your odds of winning are now increased by {item.effect * 100}%")
        activeEffects["oddsIncrease"] = item.effect
        activeEffects["oddsIncreaseDuration"] = item.duration

    elif item.effectType == "seeDealerCards":  # Powdered Sugar
        print("Your eyes widen… You can see the dealer’s cards now.")
        activeEffects["seeDealerCards"] = item.effect
        activeEffects["visionDuration"] = item.duration

    else:
        print("This item has no effect yet.")

    #remove used item
    inventory.remove(item)
    print(f"{item.name} has been used.\n")


##############################################
# EFFECT HELPER
##############################################

def reduceEffectDurations():
    if activeEffects["multiplierDuration"] > 0:
        activeEffects["multiplierDuration"] -= 1
        if activeEffects["multiplierDuration"] == 0:
            activeEffects["multiplier"] = None

    if activeEffects["oddsIncreaseDuration"] > 0:
        activeEffects["oddsIncreaseDuration"] -= 1
        if activeEffects["oddsIncreaseDuration"] == 0:
            activeEffects["oddsIncrease"] = None

    if activeEffects["visionDuration"] > 0:
        activeEffects["visionDuration"] -= 1
        if activeEffects["visionDuration"] == 0:
            activeEffects["seeDealerCards"] = None


##############################################
# TERMINAL MAIN (unchanged — runs if you launch this file directly)
##############################################
if __name__ == "__main__": #had to add this so that when I import code to GUI, it doesnt play the text-based version of the game
    rooms, currentRoom = createRooms()

    print("\nWelcome to the Casino of Sin.")
    print("Use commands like: go east, play blackjack, buy drinks\n")

    while True:
        print("=" * 80)
        print(currentRoom)
        print(f"Money: ${money}")
        print(f"Inventory: {inventory}")

        action = input("What would you like to do? ").lower().strip()
        words = action.split()

        if len(words) == 2:
            verb, noun = words
            if verb == "go" and noun in currentRoom.exits:
                i = currentRoom.exits.index(noun)
                currentRoom = currentRoom.exitLocations[i]
            elif verb == "play":
                if noun == "wheel" and currentRoom.name == "Wheel of Fortune Room":
                    print(spinTheWheel())
                elif noun == "ring" and currentRoom.name == "Cockfight Pit":
                    print(startCockfight())
                elif noun == "blackjack" and currentRoom.name == "Blackjack Room":
                    print(startBlackjack())
                elif noun == "roulette" and currentRoom.name == "Roulette Room":
                    ans = input("Red or Black? ").lower()
                    answer = ans
                    print(playRoulette())
            elif verb == "buy" and noun == "drinks" and currentRoom.name == "Bar":
                print("Items: Beer ($50), Vodka ($150), Powdered Sugar ($300)")
                choice_item = input("Which item? ")
                print(buyItem(choice_item))
                