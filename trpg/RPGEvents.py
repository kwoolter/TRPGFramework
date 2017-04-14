__author__ = 'KeithW'

from xml.dom.minidom import *

from .RPGCheck import *
from .RPGXMLUtilities import *


class RPGEvent(RPGCheck):
    def __init__(self, name : str, description : str):
        super(RPGEvent, self).__init__(name, "Event", description)


class RPGEventFactory(object):
    def __init__(self, file_name : str):
        self.file_name = file_name
        self._dom = None
        self._events = {}

    @property
    def count(self):
        return len(self._events)

    def print(self):
        for event in self._events.values():
            print(str(event))

    # get a list of available events in the factory
    def get_available_events(self, character : Character):

        events = []

        for event in self._events.values():
            logging.debug("%s.get_available_events(): Checking event %s is available.", __class__, event.name)
            if event.is_available(character) is True and event.is_completed(character) is False:
                events.append(event)

                logging.debug("%s.get_available_events(): event %s is available.", __class__, event.name)

        return events

    # retrieve a event by name
    def get_event(self, name : str):
        if name in self._events.keys():
            return self._events[name]
        else:
            return None

    # Load in the events contained in the event file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "events"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all events
        events = self._dom.getElementsByTagName("event")

        # for each event...
        for event in events:

            # Get the main tags that describe the conversation
            event_name = xml_get_node_text(event, "name")
            event_description = xml_get_node_text(event, "description")

            # ... and create a basic event object
            new_event = RPGEvent(event_name, event_description)

            logging.info("%s.load(): Loading event '%s'...", __class__, new_event.name)

            # Now collect all of the pre-requisites for this challenge and add them to the challenge
            stat_group = event.getElementsByTagName("pre_requisites")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_event.add_pre_requisite(stat)

            # Now collect all of the checks for this challenge and add them to the challenge
            stat_group = event.getElementsByTagName("checks")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_event.add_check(stat)

            # Now collect all of the rewards for this challenge and add them to the challenge
            stat_group = event.getElementsByTagName("rewards")[0]
            stats = xml_get_stat_list(stat_group)
            for stat in stats:
                new_event.add_reward(stat)

            logging.info("%s.load(): Loaded event '%s'", __class__, str(new_event))


            # Add the new event to the dictionary
            self._events[new_event.name] = new_event

        self._dom.unlink()







