import random

#if player score or dealer score is greater than 21, they automatically lose
#type in hit, or play, gives the user a random card, if they hit, they have to play
#make it so you can see ONE of dealers card
#hit = dont add card, call = add card, fold, give up (lose half your bet)

card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
cards_list = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
deck = [(card, category) for category in card_categories for card in cards_list]
inventory = 1000

def canStillPlay(inv):
    return inv > 0
    
def card_value(card):
    if card[0] in ['Jack', 'Queen', 'King']:
        return 10
    elif card[0] == 'Ace':
        return 11
    else:
        return int(card[0])


while canStillPlay(inventory):
    
    print(f"\nInventory: ${inventory}")
    bet = int(input("How much do you want to bet? "))
    while bet > inventory or bet <= 0:
        bet = int(input("You cannot bet that much, try a smaller value: "))
                
    
    inventory -= bet
    random.shuffle(deck)
    player_card = [deck.pop(), deck.pop()]
    dealer_card = [deck.pop(), deck.pop()]
    print(f"Dealer shows: {dealer_card[0]}")
    while True:

        player_score = sum(card_value(card) for card in player_card)
        dealer_score = sum(card_value(card) for card in dealer_card)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("\n")
        choice = input('What do you want? ["hit" to request another card, "stand" to keep your hand]: ').lower()
        
        if choice == "hit":
            new_card = deck.pop()
            player_card.append(new_card)
            player_score = sum(card_value(card) for card in player_card)
            break
           
        
        elif choice == "stand":
            break

    while dealer_score < 17:
        new_card = deck.pop()
        dealer_card.append(new_card)
        dealer_score += card_value(new_card)

    print("Cards Dealer Has:", dealer_card)
    print("Score Of The Dealer:", dealer_score)
    print("\n")
    
    if player_score > 21:
        print("Cards Dealer Has:", dealer_card)
        print("Score Of The Dealer:", dealer_score)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("Dealer Wins (Winner Loss Because Winner Score is exceeding 21)")
                
    elif dealer_score > 21:
        print("Cards Dealer Has:", dealer_card)
        print("Score Of The Dealer:", dealer_score)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("Player wins (Dealer Loss Because Dealer Score is exceeding 21)")
    
        inventory += bet*2
    
    elif player_score > dealer_score:
        print("Cards Dealer Has:", dealer_card)
        print("Score Of The Dealer:", dealer_score)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("Player wins (Player Has High Score than Dealer)")
        
        inventory += bet*2
        
    elif dealer_score > player_score:
        print("Cards Dealer Has:", dealer_card)
        print("Score Of The Dealer:", dealer_score)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("Dealer wins (Dealer Has High Score than Player)")
    
    
    else:
        print("Cards Dealer Has:", dealer_card)
        print("Score Of The Dealer:", dealer_score)
        print("Cards Player Has:", player_card)
        print("Score Of The Player:", player_score)
        print("It's a tie.")
        
        inventory += bet
