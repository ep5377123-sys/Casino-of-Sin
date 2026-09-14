#Bar Rooms
class Room:
    def __init__(self, name):
        # rooms have a name, description, exits (e.g., south), exit locations (e.g., to the south is
        # room n), items (e.g., table), item descriptions (for each item), and grabbables (things that
        # can be taken into inventory)
        self._name = name
        self._description = ""
        self._exits = []
        self._exitLocations = []
        self._items = []
        self._itemDescriptions = []
        self._grabbables = []
        self._image = ""
        
    def get_name(self):
        return self._name
    
    def set_name(self, value):
        self._name = value

    def get_description(self):
        return self._description

    def set_description(self, value):
        self._description = value

    def get_exits(self):
        return self._exits

    def set_exits(self, value):
        self._exits = value

    def get_exitLocations(self):
        return self._exitLocations

    def set_exitLocations(self, value):
        self._exitLocations = value
        
    def get_items(self):
        return self._items

    def set_items(self, value):
        self._items = value

    def get_itemDescriptions(self):
        return self._itemDescriptions

    def set_itemDescriptions(self, value):
        self._itemDescriptions = value

    def get_grabbables(self):
        return self._grabbables

    def set_grabbables(self, value):
        self._grabbables = value
        
    def get_image(self):
        return self._image
        
    def set_image(self, value):
        self._image = value
        
    name = property(get_name, set_name)
    description = property(get_description, set_description)
    exits = property(get_exits, set_exits)
    exitLocations = property(get_exitLocations, set_exitLocations)
    items = property(get_items, set_items)
    itemDescriptions = property(get_itemDescriptions, set_itemDescriptions)
    grabbables = property(get_grabbables, set_grabbables)
    image = property(get_image, set_image)
    
    def addExit(self, exit, room):
        # append the exit and room to the appropriate lists
        self._exits.append(exit)
        self._exitLocations.append(room)
    
    def addItem(self, item, desc):
        # append the item and description to the appropriate lists
        self._items.append(item)
        self._itemDescriptions.append(desc)
        
        
    def __str__(self):
        # first, the room name and description
        s = "{}\n".format(self._name)
        s += "{}\n".format(self._description)
        
        # first, the room name and description
        s = "{}\n".format(self._name)
        s += "{}\n".format(self._description)
        
        # next, the exits from the room
        s += "Exits: "
        for exit in self._exits:
            s += exit + " "

        return s
        