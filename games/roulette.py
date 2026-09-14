import random

inventory = 1000

# user decides how much they will bet

# if user placed too much
def canStillPlay(inv):
    return inv > 0

while canStillPlay(inventory):
    print(f"\nInventory: ${inventory}")
    bet = int(input("How much do you want to bet? "))
    while bet > inventory or bet <= 0:
        bet = int(input("You cannot bet that much, try a smaller value: "))
    print("Choose Red or Black:")
    answer = input("> ")
    result = random.randint(1, 2)
    if result == 1 and answer == "Red":
        print("You won")
        inventory += bet
        print(f"Your balance now {inventory}")
    elif result == 2 and answer == "Black":
        print("You won")
        inventory += bet
        print(f"Your balance now {inventory}")
    else:
        print("You lost")
        inventory -= bet
        print(f"Your balance now {inventory}")
       
