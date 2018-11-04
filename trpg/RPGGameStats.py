__author__ = 'KeithW'

from .RPGObject import *


class RPGDerivedStat(DerivedStat):
    def __init__(self, name: str, category: str, owner : RPGObject):
        super(RPGDerivedStat,self).__init__(name, category)
        self._owner = owner

    def add_dependency(self,dependent_stat, optional: bool=False, default_value: float=0):
        stat_name = self._owner.get_public_stat_name(dependent_stat)
        super(RPGDerivedStat,self).add_dependency(stat_name, optional, default_value)

    def get_dependency_value(self, dependency_stat_name):
        stat_name = self._owner.get_public_stat_name(dependency_stat_name)
        value = super(RPGDerivedStat,self).get_dependency_value(stat_name)
        return value




class MaxHP(RPGDerivedStat):
    def __init__(self, owner : RPGObject):
        super(MaxHP,self).__init__("Max HP", "Attributes", owner)
        self.add_dependency("Constitution")

    def calculate(self):
        con = self.get_dependency_value("Constitution")
        return 10 + con

class HP(RPGDerivedStat):
    def __init__(self, owner : RPGObject):
        super(HP,self).__init__("HP", "Attributes", owner)
        self.add_dependency("Max HP")
        self.add_dependency("Damage",optional=True,default_value=0)

    def calculate(self):
        max_HP = self.get_dependency_value("Max HP")
        dmg = self.get_dependency_value("Damage")
        if dmg < 0:
            dmg = 0
        return max_HP - dmg

class MaxLoad(RPGDerivedStat):
    def __init__(self, owner : RPGObject):
        super(MaxLoad,self).__init__("Max Load", "Skills", owner)
        self.add_dependency("Constitution")
        self.add_dependency("Level")

    def calculate(self):
        con = self.get_dependency_value("Constitution")
        lvl = self.get_dependency_value("Level")
        return 10 + con + lvl

class TotalWeight(RPGDerivedStat):
    def __init__(self, owner : RPGObject):
        super(TotalWeight,self).__init__("Total Weight", "Attributes", owner)
        self.add_dependency("Weight")
        self.add_dependency("Item Weight",optional=True,default_value=0)

    def calculate(self):
        weight = self.get_dependency_value("Weight")
        item_weight = self.get_dependency_value("Item Weight")
        return weight + item_weight

class LoadPct(RPGDerivedStat):
    def __init__(self, owner : RPGObject):
        super(LoadPct,self).__init__("Load Pct", "Attributes", owner)
        self.add_dependency("Item Weight",optional=True,default_value=0)
        self.add_dependency("Max Load")

    def calculate(self):
        max_load = self.get_dependency_value("Max Load")
        item_weight = self.get_dependency_value("Item Weight")
        return item_weight*100/max_load


# A Lock-picking Skill stat based on Dex and Int
class Lockpicking(RPGDerivedStat):

    def __init__(self, owner : RPGObject):
        super(Lockpicking,self).__init__("Lockpicking", "Skills", owner)
        self.add_dependency("Dexterity")
        self.add_dependency("Intelligence")

    def calculate(self):
        dex = self.get_dependency_value("Dexterity")
        intell = self.get_dependency_value("Intelligence")
        return dex + intell


class HasMoved(RPGDerivedStat):

    MOVED = 1
    NOT_MOVED = 0

    def __init__(self, owner : RPGObject):
        super(HasMoved,self).__init__("Has Moved", "Map", owner)
        self.add_dependency("Location")
        self.add_dependency("OldLocation",optional=True)

    def calculate(self):
        location = self.get_dependency_value("Location")
        old_location = self.get_dependency_value("OldLocation")
        if old_location == 0 or location == old_location:
            return HasMoved.NOT_MOVED
        else:
            return HasMoved.MOVED


class XPToLevel(RPGDerivedStat):

    _xp_levels = [5,10,15,20,25,30,40,50,75,100]

    def __init__(self, owner : RPGObject):
        super(XPToLevel,self).__init__("XPToLevel", "Attributes", owner)
        self.add_dependency("XP")

    def calculate(self):
        xp = self.get_dependency_value("XP")
        level = 1

        for i in range(0, len(XPToLevel._xp_levels)):
            if xp < XPToLevel._xp_levels[i]:
                break
            else:
                level +=1

        return level

class LevelUP(RPGDerivedStat):

    def __init__(self, owner : RPGObject):
        super(LevelUP,self).__init__("LevelUp", "Attributes", owner)
        self.add_dependency("XPToLevel")
        self.add_dependency("Level")

    def calculate(self):
        xp_level = self.get_dependency_value("XPToLevel")
        current_level = self.get_dependency_value("Level")

        return xp_level - current_level

