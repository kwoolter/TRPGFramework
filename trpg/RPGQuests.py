__author__ = 'KeithW'

from xml.dom.minidom import *

from .RPGCheck import *
from .RPGXMLUtilities import *


# Challenge class which represents the name and description of a challenge as well as:-
# - any prerequisites
# - what the reward are for completing the challenge
# - what checks are performed when a player attempts a challenge
#
class Challenge(RPGCheck):

    # Construct a basic challenge
    # A name, optional description and optional completion message
    def __init__(self, name : str, description : str = "", completion_msg : str=""):

        super(Challenge, self).__init__(name, "QuestChallenge", description, completion_msg)

    def __str__(self):
        return self.name + " - " + self.description


# Quest class for managing all challenges associated with a quest
class Quest(object):

    def __init__(self, name : str, description : str ="", linear: bool = True):
        self.name=name
        self.description = description
        self._challenges = []
        self._linear = linear

    def __str__(self):
        return self.name + " - " + self.description

    # Add a new challenge to the quests
    def add_challenge(self, new_challenge : Challenge):

       # If this is a linear quest and some other challenges have been added to the quest...
        if self._linear is True and len(self._challenges) > 0:

            # Add the prior challenge as a pre-requisite to the new challenge
            pre_req_challenge = self._challenges[len(self._challenges) -1]
            new_challenge.add_pre_requisite(BaseStat(pre_req_challenge.name, "Challenges", RPGCheck.SUCCEEDED))

            logging.info("%s.add_challenge(): Linear quest %s add pre-req '%s' to '%s'", \
                        __class__, self.name, pre_req_challenge.name, new_challenge.name)

        # Add the new challenge to the list of challenges for the quest
        self._challenges.append(new_challenge)

    def get_challenge_by_number(self, challenge_number : int):
        return self._challenges[challenge_number]

    def get_all_challenges(self):
        return self._challenges.copy()

    def get_available_challenges(self, character : Character):

        challenge_list = []

        for challenge in self._challenges:
            # If we find an available challenge that has not been completed then the quest is available
            if challenge.is_available(character) is True and challenge.is_completed(character) is False:
                challenge_list.append(challenge)

        return challenge_list


    # See if this quest is available for a player to attempt
    def is_available(self, character):

        is_available = False

        # Look through the list of challenges to see if any are available..
        for challenge in self._challenges:

            # If we find an available challenge then the quest is available
            if challenge.is_available(character) is True:
                is_available = True
                break

        return is_available

    # Check to see if the specified player has completed this Quest
    def is_completed(self, character : Character):

        completed = True

        for challenge in self._challenges:
            if challenge.is_completed(character) is False:
                completed = False
                break

        return completed

    # Print out the details of a quest
    # If you provide a stat engine then additional info about the player's status is added
    def to_string(self, character : Character = None):

        display_string = "Quest '{0} - {1}' has {2} challenges. Linear({3}).".format(self.name, \
                                                                                  self.description, \
                                                                                  len(self._challenges), \
                                                                                  self._linear)

        if character is not None:
            if self.is_completed(character) is True:
                display_string += " [completed]"
            elif self.is_available(character) is True:
                display_string += " [available]"

        for i in range(0,len(self._challenges)):
            challenge = self._challenges[i]
            display_string += "\n{0}. {1}".format(i + 1, str(challenge))

            if character is not None:
                if challenge.is_completed(character) is True:
                    display_string += " [completed]"
                elif challenge.is_available(character) is True:
                    display_string += " [available]"

        return display_string


class QuestFactory(object):
    '''
    Create some quests from an XML file and store them in a dictionary
    '''

    def __init__(self, file_name : str):

        self.file_name = file_name
        self._dom = None
        self._quests = {}

    @property
    def count(self):
        return len(self._quests)

    # get a list of all of the quest names in the factory
    def get_quest_names(self, character : Character = None):

        if character is None:
            return self._quests.keys()

        quest_names = []

        for quest in self._quests.values():
            logging.debug("%s.get_quest_names(): Checking quest %s is available.", __class__, quest.name)
            if quest.is_available(character) is True or quest.is_completed(character) is True:
                quest_names.append(quest.name)

                logging.debug("%s.get_quest_names(): Quest %s is available.", __class__, quest.name)

        return quest_names

    # get a list of available quests in the factory
    def get_available_quests(self, character : Character):

        quests = []

        for quest in self._quests.values():
            logging.debug("%s.get_quest_names(): Checking quest %s is available.", __class__, quest.name)
            if quest.is_available(character) is True and quest.is_completed(character) is False:
                quests.append(quest)

                logging.debug("%s.get_quest_names(): Quest %s is available.", __class__, quest.name)

        return quests

    # retrieve a quest by name
    def get_quest(self, quest_name : str):
        if quest_name in self._quests.keys():
            return self._quests[quest_name]
        else:
            return None

    # Load in the quest contained in the quest file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "quests"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all quests
        quests = self._dom.getElementsByTagName("quest")

        # for each quest...
        for quest in quests:

            # Get the main tags that describe the quest
            name = xml_get_node_text(quest, "name")
            desc = xml_get_node_text(quest, "description")
            linear = (xml_get_node_text(quest, "linear") == "True")
            #completion_msg = self.xml_get_node_text(quest,"completion_msg")

            # ...and create a basic quest object
            new_quest = Quest(name, description = desc, linear = linear)

            logging.info("%s.load(): Loading Quest '%s'...", __class__, new_quest.name)

            # Next get a list of all of the challenges
            challenges = quest.getElementsByTagName("challenge")

            # For each challenge...
            for challenge in challenges:

                # Get the basic details of the challenge
                name = xml_get_node_text(challenge, "name")
                desc = xml_get_node_text(challenge, "description")
                completion_msg = xml_get_node_text(challenge, "completion_msg")

                # ... and create a basic challenge object which we add to the owning quest
                new_challenge = Challenge(name, desc, completion_msg)
                new_quest.add_challenge(new_challenge)

                logging.info("%s.load(): Loading Challenge '%s'...", __class__, new_challenge.name)

                # Now collect all of the pre-requisites for this challenge and add them to the challenge
                stat_group = challenge.getElementsByTagName("pre_requisites")[0]
                stats = xml_get_stat_list(stat_group)
                for stat in stats:
                    new_challenge.add_pre_requisite(stat)

                # Now collect all of the checks for this challenge and add them to the challenge
                stat_group = challenge.getElementsByTagName("checks")[0]
                stats = xml_get_stat_list(stat_group)
                for stat in stats:
                    new_challenge.add_check(stat)

                # Now collect all of the rewards for this challenge and add them to the challenge
                stat_group = challenge.getElementsByTagName("rewards")[0]
                stats = xml_get_stat_list(stat_group)
                for stat in stats:
                    new_challenge.add_reward(stat)

                logging.info("%s.load(): Loaded Challenge '%s'", __class__, str(new_challenge))

            logging.info("%s.load(): Quest '%s' loaded", __class__, new_quest.name)

            # Add the new quest to the dictionary
            self._quests[new_quest.name] = new_quest

        self._dom.unlink()
