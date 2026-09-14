import random

class Chicken:
    #constructor
    def __init__(self, h, s, d):
        self._health = h
        self._strength = s
        self._defense = d

    #getters
    def _get_health(self):
        return self._health

    def _get_strength(self):
        return self._strength

    def _get_defense(self):
        return self._defense

    #setters
    def _set_health(self, h):
        self._health = h

    def _set_strength(self, s):
        self._strength = s

    def _set_defense(self, d):
        self._defense = d

    #properties    
    health = property(_get_health, _set_health)
    strength = property(_get_strength, _set_strength)
    defense = property(_get_defense, _set_defense)

    #other methods
    def calculateAttack(self, opponent_defense):
        attack_value = self._strength * (1 - opponent_defense/10)
        return attack_value

    def isStillAlive(self):
        return self._health > 0


#Build Opposing Chicken
def buildOpponent():
    health = random.randint(50, 100)
    strength = random.randint(10, 20)
    defense = random.randint(0, 10)
    return Chicken(health, strength, defense)

def buildAlly():
    health = random.randint(50, 100)
    strength = random.randint(10, 20)
    defense = random.randint(0, 10)
    return Chicken(health, strength, defense)

def canStillPlay(inv):
    return inv > 0


# ----------------------------
# CREATE THE CHICKENS
# ----------------------------
allyChicken = buildAlly()
opponentChicken = buildOpponent()

print("The Chickens are ready to battle...\n")
inventory = 1000
round_number = 1

# ----------------------------
# MAIN BATTLE LOOP
# ----------------------------
while canStillPlay(inventory):

    # ---- PLACE BET ----
    bet = int(input("How much do you want to bet? "))
    while bet > inventory or bet <= 0:
        bet = int(input("Invalid bet. Try again: "))

    inventory -= bet

    # ---- NEW BATTLE ----
    while allyChicken.isStillAlive() and opponentChicken.isStillAlive():

        print(f"\n--- ROUND {round_number} ---")
        print(f"Your Chicken: {allyChicken.health} HP")
        print(f"Enemy Chicken: {opponentChicken.health} HP")
        print(f"Inventory: ${inventory}")

        # YOUR CHICKEN ATTACKS
        allyDamage = allyChicken.calculateAttack(opponentChicken.defense)
        opponentChicken.health -= allyDamage
        print(f"\nYour chicken dealt {allyDamage:.1f} damage!")

        # ENEMY COUNTERATTACK
        if opponentChicken.isStillAlive():
            enemyDamage = opponentChicken.calculateAttack(allyChicken.defense)
            allyChicken.health -= enemyDamage
            print(f"Enemy chicken dealt {enemyDamage:.1f} damage!")

        round_number += 1


    # ----------------------------
    # FINAL RESULTS OF THE FIGHT
    # ----------------------------
    print("\n--- BATTLE RESULTS ---")
    if allyChicken.isStillAlive():
        print("Your chicken WON!!!")
        inventory += bet * 2
    else:
        print("Your chicken LOST...")

    print(f"Final Inventory: ${inventory}")

    # STOP IF INVENTORY EMPTY
    if not canStillPlay(inventory):
        break

    # RESET CHICKENS FOR NEXT BET
    allyChicken = buildAlly()
    opponentChicken = buildOpponent()
    round_number = 1