__author__ = 'KeithW'

from xml.dom.minidom import *

from .RPGCheck import *
from .RPGXMLUtilities import *


class Trap(RPGCheck):
    def __init__(self, name : str, description : str = "", completion_msg : str="", is_one_shot : bool = True):

        self.is_one_shot = is_one_shot

        super(Trap, self).__init__(name, "Trap", description, completion_msg)

    def attempt(self, character :  Character):

        try:
            result = super(Trap, self).attempt(character)
        except Exception as err:
            result = False
            self.failure_msg = str(err)

        # If this is a one-shot trap then mark completed no matter what
        if self.is_one_shot:
            character.update_stat(self.name, RPGCheck.SUCCEEDED)
        # Else reset the trap as though you have not attempted it
        else:
            character.update_stat(self.name, RPGCheck.NOT_ATTEMPTED)

        return result

class RPGTrapFactory(object):

    def __init__(self, file_name : str):
        self.file_name = file_name
        self._dom = None
        self._traps = {}

    @property
    def count(self):
        return len(self._traps)

    def print(self):
        for trap in self._traps.values():
            print(str(trap))

    # get a list of available traps in the factory
    def get_available_traps(self, character : Character):

        traps = []

        for trap in self._traps.values():
            logging.debug("%s.get_available_traps(): Checking trap %s is available.", __class__, trap.name)
            if trap.is_available(character) is True and trap.is_completed(character) is False:
                traps.append(trap)

                logging.debug("%s.get_available_traps(): Trap %s is available.", __class__, trap.name)

        return traps

    # retrieve a trap by name
    def get_trap(self, name : str):
        if name in self._traps.keys():
            return self._traps[name]
        else:
            return None

    # Load in the traps contained in the trap file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "traps"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all traps
        traps = self._dom.getElementsByTagName("trap")

        # for each trap...
        for trap in traps:

            # Get the main tags that describe the conversation
            trap_name = xml_get_node_text(trap, "name")
            trap_one_shot = (xml_get_node_text(trap, "one_shot").upper() == "TRUE")
            trap_description = xml_get_node_text(trap, "description")
            completion_msg = xml_get_node_text(trap, "completion_msg")

            # ... and create a basic trap object
            new_trap = Trap(trap_name, trap_description, completion_msg, is_one_shot=trap_one_shot)

            logging.info("%s.load(): Loading Trap '%s'...", __class__, new_trap.name)

            # Now collect all of the pre-requisites for this challenge and add them to the challenge
            stat_group = trap.getElementsByTagName("pre_requisites")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_trap.add_pre_requisite(stat)

            # Now collect all of the checks for this challenge and add them to the challenge
            stat_group = trap.getElementsByTagName("checks")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_trap.add_check(stat)

            # Now collect all of the rewards for this challenge and add them to the challenge
            stat_group = trap.getElementsByTagName("rewards")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_trap.add_reward(stat)

            logging.info("%s.load(): Loaded Trap '%s'", __class__, str(new_trap))


            # Add the new trap to the dictionary
            self._traps[new_trap.name] = new_trap

        self._dom.unlink()


