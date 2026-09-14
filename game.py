###########################################################################################
# Name: Dr. Jean Gourd
# Date: 2023-11-13
# Description: A basic Room Adventure game to show its mechanics and gameplay.
###########################################################################################

###########################################################################################
# import libraries
from time import sleep
from Room import Room

# support for tab completion
# don't delete this!
try:
    TAB_COMPLETE = True
    import TabCompleter as TC                       # for tab completion (if available)
except ModuleNotFoundError:
    TAB_COMPLETE = False

###########################################################################################
# constants
# don't delete this!
VERBS = [ "go", "look", "take" ]                    # the supported vocabulary verbs
QUIT_COMMANDS = [ "exit", "quit", "bye" ]           # the supported quit commands

###########################################################################################
# creates the rooms
def createRooms():
    # a list of rooms will store all of the rooms
    # r1 through r4 are the four rooms in the "mansion"
    # currentRoom is the room the player is currently in (which can be one of r1 through r4)
    rooms = []

    # first, create the room instances so that they can be referenced below
    r1 = Room("Room 1")
    r2 = Room("Room 2")
    r3 = Room("Room 3")
    r4 = Room("Room 4")

    # room 1
    r1.description = "You look around the room."
    r1.addExit("east", r2)
    r1.addExit("south", r3)
    r1.addGrabbable("golden_key")
    r1.addItem("chair", "It is made of wicker. No one is sitting on it.")
    r1.addItem("table", "It is made of oak. A golden_key rests on it.")
    rooms.append(r1)

    # room 2
    r2.description = "This room smells funny."
    r2.addExit("west", r1)
    r2.addExit("south", r4)
    r2.addItem("rug", "It appears to be Persian. It also needs to be vacuumed.")
    r2.addItem("fireplace", "It is full of ashes and smells dank.")
    rooms.append(r2)

    # room 3
    r3.description = "You could imagine yourself reading here."
    r3.addExit("north", r1)
    r3.addExit("east", r4)
    r3.addGrabbable("book")
    r3.addItem("bookshelves", "They are empty. Go figure.")
    r3.addItem("statue", "There is nothing special about it.")
    r3.addItem("desk", "The statue is resting on it. So is a book.")
    rooms.append(r3)

    # room 4
    r4.description = "Something may be fermenting in this room."
    r4.addExit("north", r2)
    r4.addExit("west", r3)
    r4.addExit("south", None) # DEATH!
    r4.addGrabbable("6-pack")
    r4.addItem("brew_rig", "Dr. Gourd is brewing some sort of oatmeal stout on the brew rig. A 6-pack is\nresting beside it.")
    rooms.append(r4)

    # set room 1 as the current room at the beginning of the game
    currentRoom = r1

    return rooms, currentRoom

###########################################################################################
# MAIN

# support for tab completion
# don't delete this!
if (TAB_COMPLETE):
    TC.parse_and_bind("tab: complete")

# START THE GAME!!!
inventory = []                      # nothing in inventory...yet
rooms, currentRoom = createRooms()  # add the rooms to the game

# an introduction
print("WELCOME TO ROOM ADVENTURE!")
print("=" * 80)
print("You awake.")

# play forever (well, at least until the player dies or asks to quit)
while (True):
    # set the status so the player has situational awareness
    # the status has room and inventory information
    status = "{}\nYou are carrying: {}\n".format(currentRoom, inventory)

    # if the current room is None, then the player is dead
    # this only happens if the player goes south when in room 4
    # exit the game
    if (currentRoom == None):
        #death() # you'll add this later
        break

    # support for tab completion
    # don't delete this!
    if (TAB_COMPLETE):
        # add the words to support
        words = VERBS + QUIT_COMMANDS + inventory + currentRoom.exits + currentRoom.items + currentRoom.grabbables
        # setup tab completion
        tc = TC.TabCompleter(words)
        TC.set_completer(tc.complete)

    # display the status
    print("=" * 80)
    print(status)

    # prompt for player input
    # the game supports a simple language of <verb> <noun>
    # valid verbs are go, look, and take
    # valid nouns depend on the verb
    action = input("What would you like to do? ")

    # set the user's input to lowercase to make it easier to compare the verb and noun to known values
    action = action.lower().strip()

    # exit the game if the player wants to leave (supports quit, exit, and bye)
    if (action in QUIT_COMMANDS):
        break

    # set a default response
    response = "I don't understand. Try verb noun. Valid verbs are {}.".format(", ".join(VERBS))
    # split the user input into words (words are separated by spaces) and store the words in a list
    words = action.split()

    # the game only understands two word inputs
    if (len(words) == 2):
        # isolate the verb and noun
        verb = words[0].strip()
        noun = words[1].strip()

        # we need a valid verb
        if (verb in VERBS):
            # the verb is: go
            if (verb == "go"):
                # set a default response
                response = "You can't go in that direction."

                # check if the noun is a valid exit
                if (noun in currentRoom.exits):
                    # get its index
                    i = currentRoom.exits.index(noun)
                    # change the current room to the one that is associated with the specified exit
                    currentRoom = currentRoom.exitLocations[i]
                    # set the response (success)
                    response = "You walk {} and enter another room.".format(noun)
            # the verb is: look
            elif (verb == "look"):
                # set a default response
                response = "You don't see that item."

                # check if the noun is a valid item
                if (noun in currentRoom.items):
                    # get its index
                    i = currentRoom.items.index(noun)
                    # set the response to the item's description
                    response = currentRoom.itemDescriptions[i]
            # the verb is: take
            elif (verb == "take"):
                # set a default response
                response = "You don't see that item."

                # check if the noun is a valid grabbable and is also not already in inventory
                if (noun in currentRoom.grabbables and noun not in inventory):
                    # get its index
                    i = currentRoom.grabbables.index(noun)
                    # add the grabbable item to the player's inventory
                    inventory.append(currentRoom.grabbables[i])
                    # set the response (success)
                    response = "You take {}.".format(noun)

    # display the response
    if (currentRoom != None):
        print("=" * 80)
        print(response)

