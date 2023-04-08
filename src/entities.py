"""This module holds creatures and stuff that moves around"""
import events
from tile import Tile

import functools
import itertools

class Entity():
    """A dynamic object on the map, such as a player or monster"""

    def __init__(self, tile, x, y, get_gameworld_cell):
        self.tile = tile
        self.x = x
        self.y = y
        self.get_gameworld_cell = get_gameworld_cell

        self.inventory = []

    def player_collision(self, player):
        """Called when the player attempts to enter the same cell as this entity

        Return whether the player should complete the move or not.
        """
        return True

    def die(self):
        """Remove this entity from the world"""
        events.trigger_event("on_entity_death", self)

class Player(Entity):
    """A player character"""

    def __init__(self, *args, **kwargs):
        tile = Tile('@', foreground="WHITE", background="CYAN")
        super(Player, self).__init__(tile, *args, **kwargs)

        #A flag that might temporarily be set to false during the move step if something
        #prevents the player from moving
        self.should_move = True 

        events.listen_to_event("player_move", self.move)
        events.listen_to_event("player_should_stop", self.cancel_move)
        events.listen_to_event("player_display_inventory", self.display_inventory)
        events.listen_to_event("player_drop_inventory", self.drop_inventory)
        events.listen_to_event("player_use_portal", self.use_portal)

    def move(self, x_dir, y_dir):
        """Check the map and move the player in the given direction

        x_dir, y_dir: Values between -1 and 1 specifying the direction the player
        will move along that axis.
        """
        self.should_move = True
        next_coords = (self.x + x_dir, self.y + y_dir)

        #First we directly inform the contents of the next cell that a player is trying
        #to enter it - this way we can minimize the use of the event
        next_cell_feature, next_cell_entities = self.get_gameworld_cell(*next_coords)
        thingies = next_cell_entities + [next_cell_feature]
        for thingy in thingies:
            self.should_move = (thingy.player_collision(self) and self.should_move)

        #Then we trigger an event for anyone not in the next cell who might care
        #If they stop us from moving, they should trigger "player_should_stop"
        events.trigger_event("player_enter_space", self, *next_coords)

        if self.should_move:
            self.x, self.y = next_coords

    def cancel_move(self):
        """Stop an in-progress movement
        
        Triggered by the 'player_should_stop' event.
        """
        self.should_move = False

    def receive_item(self, item):
        """Add item to the player's inventory"""
        self.inventory.append(item)
        events.trigger_event("print_message", "Picked up {0}".format(item))

    def display_inventory(self):
        """Display a message listing the player's inventory"""
        header = "Carrying:\n"
        nothing_func = lambda *args: None
        action_list = [(item, nothing_func) for item in self.inventory]
        if len(action_list) == 0:
            header += "Nothing at all"
        events.trigger_event("print_list", action_list, header=header)
        
    def drop_inventory(self):
        """Present list of inventory items and drop the one selected on
        the ground
        """
        header = "Choose item to drop:\n"
        def drop(get_gameworld_cell, x, y, item):
            item_entity = ItemPickup([item], x, y, get_gameworld_cell)
            events.trigger_event("world_add_entity", item_entity)
            self.inventory.remove(item)
        action_list = [(item, functools.partial(drop, get_gameworld_cell=self.get_gameworld_cell, x=self.x, y=self.y, item=item)) for item in self.inventory]
        if len(action_list) == 0:
                header += "You hold nothing!"
        events.trigger_event("print_list", action_list, header=header)

    def use_portal(self):
        """Use a portal the player is standing on"""
        cell_feature, _ = self.get_gameworld_cell(self.x, self.y)
        # for feature in cell_features:
            # if callable(hasattr(feature.__class__, "activate_portal")):
        if hasattr(cell_feature.__class__, "activate_portal"):
            cell_feature.activate_portal(self)
            # break


class ItemPickup(Entity):
    """An item's presence in the world

    When the player walks over it, they pick it up, which puts its inventory items
    in their inventory and destroys this object.
    """

    def __init__(self, items, *args, **kwargs):
        tile = Tile('%', foreground="YELLOW", background="BLACK", bold=True)
        super(ItemPickup, self).__init__(tile, *args, **kwargs)

        self.inventory.extend(items)

    def player_collision(self, player):
        """On player collision, the player gets the contained items"""
        for item in self.inventory:
            player.receive_item(item)
        self.die()
        return True

class Signpost(Entity):
    """An entity that displays a message when the player bumps into it"""

    def __init__(self, message, *args, **kwargs):
        super(Signpost, self).__init__(*args, **kwargs)

        self.message = message
        self.let_player_through = False

    def player_collision(self, player):
        """On player collision, display the message"""
        events.trigger_event("print_message", self.message)
        return self.let_player_through
