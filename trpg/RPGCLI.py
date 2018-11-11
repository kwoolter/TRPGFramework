__author__ = 'KeithW'

import cmd

from .RPGGame import *


class RPGCLI(cmd.Cmd):
    intro = "Welcome to the RPG CLI.\n" \
            "Type 'start' to get going!\n" \
            "Type 'char' to see current character\n" \
            "Type 'new' to create a new character.\n" \
            "Type 'help' to see available commands.\n"
    prompt = "What next?"

    def __init__(self, new_game : RPGGame):
        super(RPGCLI, self).__init__(completekey='tab')
        self.game = new_game

    def do_new(self,arg):
        ' Create a new character.'
        try:
            self.game.create_character()
        except Exception as err:
            print(str(err))

    def do_start(self, arg):
        'Start the game from the beginning.'
        try:
            os.system('cls')
            self.game.start()
        except Exception as err:
            print(str(err))

    def do_game(self, arg):
        try:
            self.game.print()
        except Exception as err:
            print(str(err))

    def do_char(self, arg):
        'Show character details.'
        try:
            self.game.print_player_character()
        except Exception as err:
            print(str(err))

    def do_go(self, arg):
        'Move character in specified direction e.g. go NORTH'
        try:
            self.game.tick()
            self.game.move(arg)
        except Exception as err:
            print(str(err))

    def complete_go(self, text, line, begidx, endidx):
        if not text:
            completions = MapLink.valid_directions
        else:
            completions = [ f
                            for f in MapLink.valid_directions
                            if f.startswith(text.upper())
                            ]
        return completions

    def do_get(self,arg):
        'Get an item at the current location'
        try:
            self.game.get_item()
        except Exception as err:
            print(str(err))

    def do_drop(self,arg):
        'Drop an item from your inventory'
        try:
            self.game.drop_item()
        except Exception as err:
            print(str(err))

    def do_inv(self, arg):
        'Display the inventory.'
        try:
            self.game.inventory()
        except Exception as err:
            print(str(err))


    def do_look(self, arg):
        'Show details of your current location.'

        #self.game.print_current_location()
        try:
            self.game.tick()
            self.game.print_current_location()
        except Exception as err:
            print(str(err))

    def do_journal(self, args):
        'Show the quest journal.'
        try:
            self.game.print_quests()
        except Exception as err:
            print(str(err))

    def do_quest(self, args):
        'Do a quest.'
        #self.game.do_quest()
        #return
        try:
            self.game.do_quest()
            self.game.tick()
        except Exception as err:
            print(str(err))

    def do_talk(self,args):
        'Talk to an NPC.'
        #self.game.talk()
        try:
            self.game.talk()
        except Exception as err:
            print(str(err))

    def do_shop(self,args):
        'Shop with a vendor'
        try:
            self.game.shop()
        except Exception as err:
            print(str(err))

    def do_train(self,args):
        'Train with a trainer'
        try:
            self.game.train()
        except Exception as err:
            print(str(err))

    def do_wait(self, args):
        'Wait and see what happens next.'
        try:
            self.game.tick()
            self.game.print_current_location()
        except Exception as err:
            print(str(err))

    def do_jump(self, args):
        # Force a player character to a new location
        # Useful if you need to fix bugs
        try:
            print("Jumping to {0}".format(args))
            self.game.current_location = args
            self.game.print_current_location()
        except Exception as err:
            print(str(err))


    def do_hack(self, args):
        # Hack a stat in the game stat engine
        # Useful if you need to fix bugs
        try:
            stat_name = input("Stat name?:")
            stat_value = int(input("Stat value?:"))
            self.game.state.update_stat(stat_name, stat_value)
            stat = self.game.state.get_stat(stat_name)
            print("{}".format(stat))

        except Exception as err:
            print(str(err))


    def do_stat(self, args):
        # get a stat from the game stat engine
        # Useful if you need to fix bugs
        try:
            stat_name = input("Stat name?:")
            stat = self.game.state.get_stat(stat_name)
            print("{}".format(stat))

        except Exception as err:
            print(str(err))


    def do_quit(self, arg):
        'Quit the game.'
        if confirm("Are you sure you want to quit?"):
            exit(0)

    def do_items(self,arg):
        self.game._items.print()

    def do_npcs(self,arg):
        self.game._npcs.print()

    def do_chats(self,arg):
        self.game._conversations.print()

    def do_examine(self, arg):
        'Examine a person or item'
        try:
            self.game.examine()
        except Exception as err:
            print(str(err))


    def do_save(self,arg):
        'Save your current progress'
        self.game.game_save()

    def do_load(self,arg):
        'Load a previously saved game'
        try:
            self.game.game_load()
        except Exception as err:
            print(str(err))


def main():

    logging.basicConfig(level = logging.ERROR)

    new_player = Player("Keith")
    player_character = Character("Korgul", "Human", "Warrior")


    game = RPGGame("MegaQuest")

    game.load_player(new_player)
    game.load_player_character(player_character)
    game.build_character(player_character)
    game.initialise()



    cli = RPGCLI(game)
    cli.cmdloop()

    exit(0)

if __name__ == '__main__':
    main()


