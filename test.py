__author__ = 'KeithW'

import trpg
import logging

try:
    # Everything depends on readline.
    import readline
except ImportError:
    # May be Windows, so try using a substitute.
    import pyreadline as readline

def main():

    logging.basicConfig(level = logging.ERROR)

    new_player = trpg.Player("Keith")

    player_character = trpg.Character("Aarlok", "Dwarf", "Warrior")
    game = trpg.RPGGame("MegaQuest")
    game.save = 10000
    #game.start_location = 110

    game.load_player(new_player)
    game.load_player_character(player_character)
    game.build_character(player_character)
    game.initialise()

    cli = trpg.RPGCLI(game)
    cli.cmdloop()

    exit(0)

if __name__ == '__main__':
    main()
