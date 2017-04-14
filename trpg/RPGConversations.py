__author__ = 'KeithW'

from xml.dom.minidom import *

from .RPGCheck import *
from .RPGXMLUtilities import *


class ConversationLine(RPGCheck):

    NOT_ATTEMPTED = 0
    SUCCEEDED = 1
    FAILED = -1
    REWARDED = 2

    def __init__(self, text : str):

        super(ConversationLine, self).__init__(text, "ConversationLine")

        self.text = text



class Conversation(object):

    def __init__(self, owner : str, linear: bool = True):
        self.owner = owner
        self._lines = []
        self.linear = linear
        self.current_line = 0

    def add_line(self, new_line : ConversationLine):
        self._lines.append(new_line)

    def is_available(self, character : Character):

        available = False

        for line in self._lines:
            if line.is_available(character):
                available = True
                break
        return available

    def is_completed(self, character : Character):

        completed = True

        for line in self._lines:
            if line.is_completed(character) is False:
                completed = False
                break

        return completed

    # Get the next line in the conversation
    def get_next_line(self, character : Character):

        # If this conversation has been completed...
        if self.is_completed(character):
            # then just pick a line at random that is still available
            while True:
                line = self._lines[random.randint(0,len(self._lines)-1)]
                if line.is_available(character):
                    break

        # Else cycle through the lines in sequence
        else:
            line = self._lines[self.current_line]

            # Move to the next line of the conversation
            self.current_line += 1

            # If you have reached the end of the conversation then go back to the beginning
            if self.current_line >= len(self._lines):
                self.current_line = 0

        return line

    def print(self):
        print("%s conversation." % self.owner)
        for line in self._lines:
            print(str(line))


class ConversationFactory(object):

    def __init__(self, file_name : str):

        self.file_name = file_name
        self._dom = None
        self._conversations = {}

    def get_conversation(self, npc_name : str):
        if npc_name in self._conversations.keys():
            return self._conversations[npc_name]
        else:
            return None

    def print(self):
        for conversation in self._conversations.values():
            conversation.print()

    # Load in the quest contained in the quest file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "conversations"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all conversations
        conversations = self._dom.getElementsByTagName("conversation")

        # for each conversation...
        for conversation in conversations:

            # Get the main tags that describe the conversation
            npc_name = xml_get_node_text(conversation, "npc_name")
            linear = (xml_get_node_text(conversation, "linear") == "True")

            # ...and create a basic conversation object
            new_conversation = Conversation(npc_name, linear = linear)

            logging.info("%s.load(): Loading Conversation for NPC '%s'...", __class__, new_conversation.owner)

            # Next get a list of all of the challenges
            lines = conversation.getElementsByTagName("line")

            # For each line...
            for line in lines:

                # Get the basic details of the line
                text = xml_get_node_text(line, "text")

                # ... and create a basic line object which we add to the owning conversation
                new_line = ConversationLine(text)
                new_conversation.add_line(new_line)

                logging.info("%s.load(): Loading line '%s'...", __class__, new_line.text)

                # Now collect all of the pre-requisites for this line and add them to the line
                stat_group = line.getElementsByTagName("pre_requisites")
                if len(stat_group) > 0:
                    stats =xml_get_stat_list(stat_group[0])
                    for stat in stats:
                        new_line.add_pre_requisite(stat)
                        logging.info("%s.load: loading pre-req %s", __class__, str(stat))

                # Now collect all of the rewards for this line and add them to the line
                stat_group = line.getElementsByTagName("rewards")
                if len(stat_group) > 0:
                    stats =xml_get_stat_list(stat_group[0])
                    for stat in stats:
                        new_line.add_reward(stat)
                        logging.info("%s.load: loading reward %s", __class__, str(stat))

                logging.info("%s.load(): Loaded new Line '%s'", __class__, str(new_line))

            logging.info("%s.load(): Conversation '%s' loaded", __class__, new_conversation.owner)

            # Add the new quest to the dictionary
            self._conversations[new_conversation.owner] = new_conversation

        self._dom.unlink()




