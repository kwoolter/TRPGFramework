__author__ = 'KeithW'

import time
import textwrap
import pickle
import os

from .RPGQuests import *
from .RPGMaps import *
from .RPGConversations import *
from .RPGTraps import *
from .RPGEvents import *
from .RPGInventory import *
from .RPGObject import *


class RPGGame(object):
    
    CREATED = 0
    LOADED = 1
    STARTED = 2
    WAIT_TIME = 0.35

    SAVE_GAME_DIR = "\\saves\\"
    GAME_DATA_DIR = "\\data\\"

    def __init__(self, name : str):
        self.name = name
        self._player = None
        self._player_character = None
        self._npcs = None
        self._conversations = None
        self._traps = None
        self._quests = None
        self._locations = None
        self._maps = None
        self._items = None
        self._events = None
        self._state = RPGGame.CREATED
        self.start_location = 10000

        self._wrapper = textwrap.TextWrapper()
        
        self._game_state = StatEngine(self.name)


        RPGGame.SAVE_GAME_DIR = ".\\" + self.name + RPGGame.SAVE_GAME_DIR
        RPGGame.GAME_DATA_DIR = ".\\" + self.name + RPGGame.GAME_DATA_DIR


    @property
    def state(self):
        return self._game_state


    @state.setter
    def state(self, new_state : StatEngine):
        self._game_state = new_state

    # property method to get the current game location
    @property
    def current_location(self):

        location_stat_name = "Location"
        location_id = int(self._player_character.get_stat(location_stat_name).value)
        return location_id

    @current_location.setter
    def current_location(self, new_location_id : int):

        self.old_location = self.current_location

        location_stat_name = "Location"
        self._player_character.update_stat(location_stat_name, new_location_id)

    # property method to get the previous game location
    @property
    def old_location(self):

        location_stat_name = "OldLocation"
        location_id = int(self._player_character.get_stat(location_stat_name).value)
        return location_id

    @old_location.setter
    def old_location(self, location_id : int):

        location_stat_name = "OldLocation"
        self._player_character.update_stat(location_stat_name, location_id)

    @property
    def current_map(self):
        return self._maps.get_map(self._map_level)

    @current_map.setter
    def current_map(self, new_level : int):
        self._map_level = 1

    def initialise(self):

        self.load_characters("characters.csv")
        self.load_conversations("conversations.xml")
        self.load_quests("quests.xml")
        self.load_map("locations.csv", "maplinks.csv")
        self.load_items("items.csv")
        self.load_traps("traps.xml")
        self.load_events("events.xml")

    # Build the stats for a new character
    def build_character(self, new_character : Character):

        # Load in the game classes that are available
        rpg_classes = RPGCSVFactory("Classes", RPGGame.GAME_DATA_DIR + "classes.csv")
        rpg_classes.load()

        # load in the game races that are available
        rpg_races = RPGCSVFactory("Races", RPGGame.GAME_DATA_DIR + "races.csv")
        rpg_races.load()

        # Load in the stats associated with the selected class
        new_character.load_stats(rpg_classes.get_stats_by_name(new_character.rpg_class))

        # Load in the stats associated with the selected race
        new_character.load_stats(rpg_races.get_stats_by_name(new_character.race), overwrite=False)

        # Load in any additional stats required
        new_character.add_derived_stats()



    # Create a new character
    def create_character(self):

        if self._state == RPGGame.STARTED:
            raise (Exception("%s game already started.  Too late to create a character" % self.name))

        # Load in the game classes that are available
        rpg_classes = RPGCSVFactory("Classes", RPGGame.GAME_DATA_DIR + "classes.csv")
        rpg_classes.load()

        # load in the game races that are available
        rpg_races = RPGCSVFactory("Races", RPGGame.GAME_DATA_DIR + "races.csv")
        rpg_races.load()

        print("Creating an new character...")
        player_name = input('What is YOUR name?').title()

        player = Player(player_name)

        character_name = input("What is your character's name?").title()

        # Get a list of all of the playable races and get the player to pick one.
        race_names = rpg_races.get_matching_objects(BaseStat("Playable","",1))
        race = pick("race", race_names)

        # Get a list of all of the playable classes and get the player to pick one.
        rpg_class_names = rpg_classes.get_matching_objects(BaseStat("Playable","",1))
        rpg_class = pick("class", rpg_class_names)

        # Create a new character from the specified name, race and class
        character = Character(character_name, race, rpg_class)

        self.load_player_character(character)

        self.build_character(character)


        character.print()

    def load_player(self, player : Player):
        self._player = player
        logging.info("%s.load_player(): Welcome Player %s to the RPGGame %s!", \
                     __class__, self._player.name, self.name)

    def load_player_character(self, character : Character):
        self._player_character = character
        self._player_character.is_player_character = True
        self._player_character.public_data = self._game_state
        #self._player_character.roll()
        #self._player_character.add_derived_stats()
        self._player_character.add_stat(CoreStat(Location.LOCATION_STAT, "Map", self.start_location))
        logging.info("%s.load_player(): Welcome Character %s to the RPGGame %s!", \
                     __class__, str(self._player_character), self.name)


    def load_quests(self, quest_file_name : str):
        self._quests = QuestFactory(RPGGame.GAME_DATA_DIR + quest_file_name)
        self._quests.load()

    def load_map(self, location_file_name : str, map_links_file_name : str):

        # Load in locations
        self._locations = LocationFactory(RPGGame.GAME_DATA_DIR + location_file_name)
        self._locations.load()

        # Load in level maps
        self._maps = MapFactory(self._locations)
        self._maps.load("Level1",1,RPGGame.GAME_DATA_DIR + map_links_file_name)

    def load_characters(self, character_file_name : str):
        self._npcs = CharacterFactory(RPGGame.GAME_DATA_DIR + character_file_name, self.state)
        self._npcs.load()

        rpg_classes = RPGCSVFactory("Classes", RPGGame.GAME_DATA_DIR + "classes.csv")
        rpg_classes.load()

        rpg_races = RPGCSVFactory("Races", RPGGame.GAME_DATA_DIR + "races.csv")
        rpg_races.load()

        character_names = self._npcs.get_character_names()

        for character_name in character_names:
            character = self._npcs.get_character_by_name(character_name)
            character.load_stats(rpg_classes.get_stats_by_name(character.rpg_class))
            character.load_stats(rpg_races.get_stats_by_name(character.race), False)

    def load_items(self, item_file_name : str):
        self._items = ItemFactory(RPGGame.GAME_DATA_DIR + item_file_name, self.state)
        self._items.load()

    def load_conversations(self, conversation_file : str):

        self._conversations = ConversationFactory(RPGGame.GAME_DATA_DIR + conversation_file)
        self._conversations.load()

    def load_traps(self, file_name : str):

        self._traps = RPGTrapFactory(RPGGame.GAME_DATA_DIR + file_name)
        self._traps.load()

    def load_events(self, file_name : str):

        self._events = RPGEventFactory(RPGGame.GAME_DATA_DIR + file_name)
        self._events.load()

    def game_save(self):
        file_name = RPGGame.SAVE_GAME_DIR + self._player_character.name + ".rpg"
        game_file = open(file_name, "wb")
        pickle.dump(self._player_character, game_file)
        #pickle.dump(self._game_state, game_file)
        game_file.close()

        print("%s saved" % file_name)

    def game_load(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        game_files = []
        for file in os.listdir(RPGGame.SAVE_GAME_DIR):
            if file.endswith(".rpg"):
                game_files.append(file)

        character_file = pick("character", game_files)
        file_name = RPGGame.SAVE_GAME_DIR + character_file

        if confirm("Are you sure you want to load %s?" % character_file):
            game_file = open(file_name, "rb")
            new_player_character = pickle.load(game_file)

            game_file.close()

            self._game_state.remove_all()
            self._game_state.load_stats(new_player_character.public_data.get_all_stats())
            self._player_character = new_player_character
            #self.load_player_character(new_player_character)

            print("\n%s loaded...\n" % character_file)

            self.print_current_location()

            # Hack some stats
            # self._game_state.update_stat("Character:Aarlok:Fly up with Snuggly", 0)
            # self._game_state.update_stat("Character:Aarlok:Fly down with Snuggly", 0)

    def start(self):

        if self._state == RPGGame.STARTED:
            raise (Exception("%s game already started." % self.name))

        if self._player is None or \
            self._player_character is None or \
            self._npcs is None or \
            self._quests is None or \
            self._locations is None or \
            self._maps is None:
            raise(Exception("Not ready to start %s yet as not everything is loaded", self.name))
        else:
            self._state = RPGGame.STARTED
            print("\nWelcome %s, the %s adventure begins...\n" % (str(self._player_character),self.name))
            self.print_summary()
            self.current_location = self.start_location
            self.current_map = 1


            self.inventory(self._player_character)
            print("\n")
            self.print_current_location()
    
    def print_player_character(self):
        if self._player_character is None:
            raise (Exception("You have not yet created a character yet."))

        print(self._player_character.examine())

        level_up = self._player_character.get_stat("LevelUp")
        if level_up is not None and level_up.value > 0:
            if confirm("Do you want to level up?"):
                print("Pick an attribute to increase.")
                stat_name = pick("Core Stat", list(Character.CORE_STAT_NAMES))
                self._player_character.increment_stat(stat_name,1)
                self._player_character.increment_stat("Level",1)

    def print_current_location(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))



        time.sleep(RPGGame.WAIT_TIME)

        # Get any NPCs that are arriving or departing
        arriving_npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))
        departing_npcs = self._npcs.get_matching_characters(BaseStat("OldLocation","NPC",self.current_location ))

        for npc in arriving_npcs:
            stat = npc.get_stat("Has Moved")
            if stat is not None and stat.value == HasMoved.MOVED:
                print("%s arrives." % str(npc))

        for npc in departing_npcs:
            stat = npc.get_stat("Has Moved")
            if stat is not None and stat.value == HasMoved.MOVED:
                print("%s leaves." % str(npc))

        time.sleep(RPGGame.WAIT_TIME)

        # Print our the details of the current location
        text = self.current_map.location_to_string(self.current_location, self._player_character)
        print(self._wrapper.fill(text))

        time.sleep(RPGGame.WAIT_TIME)

        # Get any NPCs that are at the current location and to_string these
        npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))

        for npc in npcs:
            print("%s is here" % str(npc))

        # Get any items that are at the current location
        items = self._items.get_matching_items(BaseStat("Location","None",self.current_location))

        if len(items) > 0:
            time.sleep(RPGGame.WAIT_TIME)
            print("You can see:")
            for item in items:
                print("\t" + item.name)

        time.sleep(RPGGame.WAIT_TIME)

        # Print any events that have been triggered
        self.do_events()

    def print_quests(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        quest_names = self._quests.get_quest_names(self._player_character)

        if len(quest_names) == 0:
            print("You have no quests available.")
        elif len(quest_names) == 1:
            print("You have 1 quest available:")
        else:
            print("You have %i quests available:" % len(quest_names))

        for quest_name in quest_names:
            quest = self._quests.get_quest(quest_name)
            print(quest.to_string(self._player_character))

    def print(self):

        self._game_state.print()

    def do_events(self):
        # See if there are any events
        events = self._events.get_available_events(self._player_character)

        for event in events:
            print(self._wrapper.fill(event.description))

    def do_trap(self):

        # See if there are any traps at the current location
        traps = self._traps.get_available_traps(self._player_character)

        for trap in traps:

            print(trap.description)

            time.sleep(RPGGame.WAIT_TIME)

            result = trap.attempt(self._player_character)

            # If you succeeded....
            if result:
                # Print challenge completion message and list out the rewards
                print(trap.completion_msg)
                rewards = trap.get_rewards()
                for reward in rewards:
                    if hasattr(reward, "description") and reward.description is not None:
                        if reward.description != RPGCheck.SILENT_REWARD:
                            print("\t%s" % reward.description)
                    else:
                        print("\t%+i %s" % (reward.value, reward.name))
            else:
                print(trap.failure_msg)

            print("...")

            time.sleep(RPGGame.WAIT_TIME)

    # Method to guide the player through the available quests, allow them to pick one and then choose what challenge
    # they would like to attempt
    def do_quest(self):

        # We can only attempt quests if the game has started
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get the list of quests that are available
        quests = self._quests.get_available_quests(self._player_character)

        # Get the user to pick which quest they want...
        quest = pick("quest", quests, auto_pick=False)
        print("Quest %s - %s." % (quest.name, quest.description))

        # ..and then get them to pick the challenge they want to attempt
        challenges = quest.get_available_challenges(self._player_character)
        chosen_challenge = pick("challenge", challenges)

        # Now attempt the challenge!
        result = chosen_challenge.attempt(self._player_character)

        # If they succeeded....
        if result:
            # Print challenge completion message and list out the rewards
            print(self._wrapper.fill(chosen_challenge.completion_msg))
            print("You received the following reward(s):")
            rewards = chosen_challenge.get_rewards()
            for reward in rewards:
                if hasattr(reward, "description") and reward.description is not None:
                    if reward.description != RPGCheck.SILENT_REWARD:
                        print("\t%s" % reward.description)
                else:
                    print("\t%+i %s" % (reward.value, reward.name))

            # ...see if the chosen quest has now been completed.
            if quest.is_completed(self._player_character):
                print("Quest '%s' completed!" % quest.name)

            # If the character has moved then print the new location
            moved = self._player_character.get_stat("Has Moved")
            if moved is not None and moved.value == HasMoved.MOVED:
                self.print_current_location()

        # Else they failed!
        else:
            print("You failed challenge %s!" % chosen_challenge.name)

    # Attempt to move the character in a specified direction
    def move(self, direction : str):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Check if a direction was even specified
        if direction is "":
            raise (Exception("You need to specify a direction e.g. NORTH"))

        # Check if the direction is a valid one
        direction = direction.upper()
        if direction not in MapLink.valid_directions:
            raise(Exception("Direction %s is not valid" % direction.title()))

        # Now see if the map allows you to go in that direction
        full_links = self.current_map.get_location_links_map(self.current_location)

        # Remove any hidden links
        links = {}
        for key in full_links.keys():
            if full_links[key].is_hidden(self._player_character) is False:
                links[key] = full_links[key]

        if direction not in links.keys():
            raise (Exception("You can't go %s from here." % direction.title()))

        # OK stat direction is valid...
        else:
            link = links[direction]

            #..but see if it is currently locked...
            if link.is_locked(self._player_character) is True:
                raise(Exception("You can't go %s - %s" % (direction.title(), link.locked_description)))

            # If all good move to the new location
            print("You go %s %s..." % (direction.title(), link.description))
            #self.old_location = self.current_location
            self.current_location = link.to_id
            # Check for traps
            self.do_trap()
            # ...and print the new location...
            self.print_current_location()
            # ..and see if there are any events that have been triggered...
            #self.do_events()


    # Method to allow you to pick an NPC to talk to and have a chat with them
    def talk(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get any NPCs that are at the current location
        npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))

        # pick which one you want to talk to...
        npc = pick("person", list(npcs), auto_pick=True)

        # talk to them...
        print("You talk to %s." % str(npc))
        conversation = self._conversations.get_conversation(npc.name)

        # If they don't have a conversation then raise failure message
        if conversation is None:
            print("%s has nothing to say to you." % npc.name)

        # Otherwise attempt the conversation
        else:
            # Get the next line in the conversation
            next_line = conversation.get_next_line(self._player_character)

            # Attempt it and if it succeeds...
            if next_line.attempt(self._player_character):

                # Print what the NPC has to say
                print("%s says '%s'" % (npc.name, next_line.text))

                # ...and print what rewards you got, if any.
                rewards = next_line.get_rewards()
                if len(rewards) > 0:
                    print("You received the following reward(s):")
                    for reward in rewards:
                        if hasattr(reward, "description") and reward.description is not None:
                            if reward.description != RPGCheck.SILENT_REWARD:
                                print("\t%s" % reward.description)
                        else:
                            print("\t%+i %s" % (reward.value, reward.name))

            # Otherwise print that they don't want to say anything
            else:
                print("%s has nothing to say to you." % npc.name)

    def shop(self):
        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get any NPCs that are at the current location
        vendor_available = False
        npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))
        for npc in npcs:
            if npc.type == Character.TYPE_VENDOR:
                vendor_available = True
                break

        if vendor_available:
            print("Shopkeeper %s is here" % npc.name)
        else:
            raise Exception("No shopkeeper here!")

        inv = Inventory(npc, self._items)
        inv.print()

        choices = ["Buy", "Sell"]
        choice = pick("option",choices)
        if choice == "Cancel":
            raise Exception("You cancelled shopping.")
        elif choice == "Buy":

            item = pick("item", inv.items)
            gold = self._player_character.get_stat("Gold").value

            if item.value > gold:
                raise Exception("%s costs %i gold but you only have %i gold." % (item.name, item.value, gold))
            else:
                char_inv = Inventory(self._player_character, self._items)
                char_inv.add_item(item)
                self._player_character.increment_stat("Gold", item.value*-1)
                print("You bought %s for %i gold" % (item.name, item.value))
        elif choice == "Sell":

            char_inv = Inventory(self._player_character, self._items)
            item = pick("item", char_inv.items)

            # If the item you selected has no value then you can't sell it!
            if item.value <= 0:
                raise Exception("%s doesn't want to buy %s." % (npc.name, item.name))

            gold = self._player_character.get_stat("Gold").value
            inv.add_item(item)
            self._player_character.increment_stat("Gold", item.value)
            print("You sold %s for %i gold" % (item.name, item.value))

    def train(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get any NPCs that are at the current location
        trainer_available = False
        npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))
        for npc in npcs:
            if npc.type == Character.TYPE_TRAINER:
                trainer_available = True
                break

        if trainer_available:
            print("Trainer %s is here" % npc.name)
        else:
            raise Exception("No trainer here!")


    def get_item(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get items at the current location
        items = items = self._items.get_matching_items(BaseStat("Location","None",self.current_location))

        # pick which one you want to get...
        item = pick("item", items, auto_pick=True)

        # Create an inventory object
        inv = Inventory(self._player_character, self._items)

        # attempt to pick up selected item...
        inv.add_item(item)
        print("You picked up %s." % str(item.name))


    def drop_item(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get any items that are in your inventory
        inv = Inventory(self._player_character, self._items)
        items = inv.items

        # pick which one you want to drop...
        item = pick("item", items, auto_pick=False)

        # ...and drop it at the current location...
        print("You dropped %s." % str(item.name))
        inv.drop_item(item)


    def inventory(self, character : Character = None):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        if character is None:
            character = self._player_character

        inv = Inventory(character, self._items)
        inv.print()

        # Print any gold that you have as well
        gold = character.get_stat("Gold")
        if gold is not None and gold.value > 0:
            print("%s has %i gold pieces." % (character.name, gold.value))


    def examine(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        # Get any NPCs that are at the current location
        npcs = self._npcs.get_matching_characters(BaseStat("Location","NPC",self.current_location ))

        # pick which one you want to examine...
        npc = pick("person", list(npcs), auto_pick=True)

        print(npc.examine())
        self.inventory(npc)


    def tick(self):

        # Check if the game has been started yet
        if self._state != RPGGame.STARTED:
            raise (Exception("%s game not ready.  You need to 'start'," % self.name))

        for npc in self._npcs.get_characters():
            npc.tick()

    def print_summary(self):
        print("Welcome to %s." % self.name)
        print("\t- %i locations" % self._locations.count)
        print("\t- %i items" % self._items.count)
        print("\t- %i quests" % self._quests.count)
        print("\t- %i traps" % self._traps.count)
        print("\t- %i events" % self._events.count)
        print("\t- %i npcs" % self._npcs.count)
        print("\n")


# Function to ask the user a simple Yes/No confirmation and return a boolean
def confirm(question : str):

    choices = ["Yes", "No"]

    while True:
        print(question)
        for i in range(0, len(choices)):
            print("%i. %s" % (i+1, choices[i]))
        choice = input("Choice?")
        if is_numeric(choice) and int(choice) > 0 and int(choice) <= (len(choices) +1):
            break
        else:
            print("Invalid choice.  Try again!")

    return (int(choice) == 1)


# Function to present a menu to pick an object from a list of objects
# auto_pick means if the list has only one item then automatically pick that item
def pick(object_type: str, objects: list, auto_pick: bool=False):

    selected_object = None
    choices = len(objects)
    vowels ="AEIOU"
    if object_type[0].upper() in vowels:
        a_or_an = "an"
    else:
        a_or_an = "a"

    # If the list of objects is no good the raise an exception
    if objects is None or choices == 0:
        raise(Exception("No %s to pick from." % object_type))

    # If you selected auto pick and there is only one object in the list then pick it
    if auto_pick is True and choices == 1:
        selected_object = objects[0]

    # While an object has not yet been picked...
    while selected_object == None:

        # Print the menu of available objects to select
        print("Select %s %s:-" % (a_or_an, object_type))

        for i in range(0, choices):
            print("\t%i) %s" % (i + 1, str(objects[i])))

        # Along with an extra option to cancel selection
        print("\t%i) Cancel" % (choices + 1))

        # Get the user's selection and validate it
        choice = input("%s?" % object_type)
        if is_numeric(choice) is not None:
            choice = int(choice)

            if 0 < choice <= choices:
                selected_object = objects[choice -1]
                logging.info("pick(): You chose %s %s." % (object_type, str(selected_object)))
            elif choice == (choices + 1):
                raise (Exception("You cancelled. No %s selected" % object_type))
            else:
                print("Invalid choice '%i' - try again." % choice)
        else:
            print("You choice '%s' is not a number - try again." % choice)

    return selected_object







