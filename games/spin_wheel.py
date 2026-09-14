import random
inventory = 1000
wheel = [0, 100, 200, 500, 1000]
probability = [0.6, 0.2, 0.1, 0.06, 0.04]
def spinWheel():
    return random.choices(wheel, weights=probability, k=1)[0] #got this from chatgpt

def canStillPlay(inv):
    return inv > 0

while canStillPlay(inventory):

    # ---- PLACE BET ----
    entry = input("Would you like to play? Cost of Entry is 50$: ")
    inventory -= 50
    if entry.lower() != "yes":
        break
    else:
        
        result = spinWheel()
        print(f"Wheel landed on: {result}")
        inventory += (result)   # subtract bet, add winnings
        print(f"New balance: {inventory}")
