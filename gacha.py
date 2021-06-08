import json
from enum import Enum
from abc import ABC, abstractmethod
import random

class BannerType(Enum):
    BEGINNER = 0
    STANDARD = 1
    CHARACTER = 2
    WEAPON = 3

    def __srt__(self):
        return self.value.lower()

    @classmethod
    def has_key(cls, name):
        return name in cls.__members__

class Banner(ABC):
    def __init__(self, banner_type, banner_id = None):
        self.banner_type = banner_type
        self.import_data()

    @abstractmethod
    def import_data(self):
        pass

# TL;DR
# Can only pull using a 10 pull
# Can only pull 2 times
# Each 10 pull costs 8 blue fates only
# Uses patch 1.0's character pool, excluding Noelle, Amber, Kaeya, and Lisa
# No weapons except 3 stars
# Has its own pity (which does not affect Event or Standard banner pity)
class BeginnerBanner(Banner):
    pass

class StandardBanner(Banner):
    current_version = 1.5
    #excluded_4star_chars = ["amber", "kaeya", "lisa"]

    standard_5star_rate = 0.006
    soft_pity_5star_lin_rate = 0.994 / 17
    standard_4star_rate = 0.051
    soft_pity_4star_rate = 0.551
    featured_chance = 0.5

    def __init__(self, version = current_version):
        self.name = "Standard"
        self.version = version
        Banner.__init__(self, BannerType.STANDARD)
    
    def import_data(self):
        characters = json.load(open('data/standard-characters.json'))
        weapons = json.load(open('data/standard-weapons.json'))

        # get rid of this later when i can look characters and weapons up from the json
        self.standard_5star_chars = []
        self.standard_4star_chars = []
        for version in characters:
            version_contents = characters[version][0]
            if version_contents['patch'] <= self.version:
                if 'standard_5star_chars' in version_contents:
                    self.standard_5star_chars = version_contents['standard_5star_chars']
                if 'standard_4star_chars' in version_contents:
                    self.standard_4star_chars = version_contents['standard_4star_chars']
        
        self.standard_5star_items = self.standard_5star_chars
        self.standard_4star_items = self.standard_4star_chars
        self.standard_3star_items = []
        for version in weapons:
            version_contents = weapons[version][0]
            if version_contents['patch'] <= self.version:
                if 'standard_5star_weaps' in version_contents:
                    self.standard_5star_items += version_contents['standard_5star_weaps']
                if 'standard_4star_weaps' in version_contents:
                    self.standard_4star_items += version_contents['standard_4star_weaps']
                if 'standard_3star_weaps' in version_contents:
                    self.standard_3star_items += version_contents['standard_3star_weaps']
        #self.standard_4star_items = [item for item in self.standard_4star_items if item not in self.excluded_4star_chars]

    def one_pull(self, player, banner):
        # update player rolls and pity
        player.increment_rolls(self.banner_type) 
        pity = player.get_pity(self.banner_type)

        # calculate current rarity rates
        current_5star_pity = pity.get_value('curr5StarPity')
        current_4star_pity = pity.get_value('curr4StarPity')
        curr_5star_rate = self.standard_5star_rate + max(0, current_5star_pity - pity.soft_5star_pity + 1) * self.soft_pity_5star_lin_rate
        curr_4star_rate = self.soft_pity_4star_rate if current_4star_pity >= pity.soft_4star_pity else self.standard_4star_rate

        # choose a rarity
        rarity = 0
        if current_5star_pity >= pity.hard_5star_pity: # check for guaranteed 5-star pity
            rarity = 5
        elif current_4star_pity >= pity.hard_4star_pity: # check for guaranteed 4+star pity
            rarity = 5 if random.random() < self.standard_5star_rate else 4
        else: # standard or soft pity roll
            rarity = 5 if random.random() < curr_5star_rate else 4 if random.random() < curr_4star_rate else 3
        pity.reset(rarity, False)

        # get the pool of potential items and then one at random
        rarity_pool = self.standard_5star_items if rarity == 5 else self.standard_4star_items if rarity == 4 else self.standard_3star_items
        wish = random.choices(rarity_pool)[0]
        player.debug_info[rarity - 3] += 1
        
        # formats the output
        emoji = ":blue_square:"
        if rarity == 5:
            emoji = ":yellow_circle:" if (wish in self.standard_5star_chars) else ":yellow_square:"
        elif rarity == 4:
            emoji = ":purple_circle:" if (wish in self.standard_4star_chars) else ":purple_square:"
        return emoji + " " + wish

    def get_info(self):
        pass


'''
class CharacterBanner(Banner):
    excluded_4star_chars = ["amber", "kaeya", "lisa"]
    standard_5star_chars = ["Diluc", "Jean", "Keqing", "Mona", "Qiqi"]
    standard_5star_weaps = ["Skyward Harp", "Amos' Bow", "Skyward Atlas", "Lost Prayer to the Sacred Winds", "Skyward Pride", "Wolf's Gravestone", "Skyward Spine", "Primordial Jade Winged-Spear", "Skyward Blade", "Aquila Favonia"]
    standard_4star_chars = ["Amber", "Barbara", "Beidou", "Bennett", "Chongyun", "Diona", "Fischl", "Kaeya", "Lisa", "Ningguang", "Noelle", "Razor", "Rosaria", "Sucrose", "Xiangling", "Xingqiu", "Xinyan", "Yanfei"]
    standard_4star_weaps = ["Favonius Warbow", "Sacrificial Bow", "The Stringless", "Rust", "Favonius Codex", "Sacrificial Fragments", "The Widsith", "Eye of Perception", "Favonius Greatsword", "Sacrificial Greatsword", "The Bell", "Rainslasher", "Favonius Lance", "Dragon's Bane", "Favonius Sword", "Sacrificial Sword", "The Flute", "Lion's Roar"]
    standard_3star_weaps = ["3-Star Weapon"]

    standard_5star_rate = 0.006
    soft_pity_5star_lin_rate = 0.994 / 17
    standard_4star_rate = 0.051
    soft_pity_4star_rate = 0.551
    featured_chance = 0.5

    def __init__(self, name = standard_name, featured_5star_items = [], featured_4star_items = []):
        self.name = name
        self.is_event_banner = self.name != self.standard_name
        self.featured_5star_items = featured_5star_items
        self.featured_4star_items = featured_4star_items

    def get_5star_pool(self, pity):
        if self.is_event_banner and (pity.featured_5star_pity or random.random() < featured_chance): # roll a featured 5-star character
            pity.hard_reset_5star_pity()
            return self.featured_5star_items
        else: # roll a standard 5-star character
            pity.soft_reset_5star_pity()
            return self.standard_5star_chars + self.standard_5star_weaps

    def get_4star_pool(self, pity):
        if self.is_event_banner and (pity.featured_4star_pity or random.random() < featured_chance): # roll a featured 4-star character
            pity.hard_reset_4star_pity()
            return self.featured_4star_items
        else: # roll a standard 4-star character
            pity.soft_reset_4star_pity()
            return self.standard_4star_chars + self.standard_4star_weaps

    def get_3star_pool(self, pity):
        return self.standard_3star_weaps

    def one_pull(self, player, banner):
        rarity = 0
        rarity_pool = []

        # update player rolls and pity
        player.increment_rolls(self.is_event_banner) 
        pity = player.get_pity(self.is_event_banner)

        current_5star_pity = pity.get_value('curr5StarPity')
        current_4star_pity = pity.get_value('curr4StarPity')

        curr_5star_rate = self.standard_5star_rate + max(0, current_5star_pity - pity.soft_5star_pity + 1) * self.soft_pity_5star_lin_rate
        curr_4star_rate = self.soft_pity_4star_rate if current_4star_pity >= pity.soft_4star_pity else self.standard_4star_rate

        if current_5star_pity >= pity.hard_5star_pity: # check for guaranteed 5-star pity
            rarity = 5
        elif current_4star_pity >= pity.hard_4star_pity: # check for guaranteed 4+star pity
            rarity = 5 if random.random() < self.standard_5star_rate else 4
        else: # standard/soft pity roll
            rarity = 5 if random.random() < curr_5star_rate else 4 if random.random() < curr_4star_rate else 3

        if rarity == 5:
            rarity_pool = self.get_5star_pool(pity)
        elif rarity == 4:
            rarity_pool = self.get_4star_pool(pity)
        elif rarity == 3:
            rarity_pool = self.get_3star_pool(pity)
        wish = random.choices(rarity_pool)[0]

        emoji = ":blue_square:"
        if rarity == 5:
            emoji = ":yellow_circle:" if (wish in self.standard_5star_chars + self.featured_5star_items) else ":yellow_square:"
        elif rarity == 4:
            emoji = ":purple_circle:" if (wish in self.standard_4star_chars + self.featured_4star_items) else ":purple_square:"
        
        return emoji + " " + wish

    # returns who's featured
    def get_info(self):
        pass

class WeaponBanner(Banner):
    standard_5star_chars = []
    standard_5star_weaps = ["Skyward Harp", "Amos' Bow", "Skyward Atlas", "Lost Prayer to the Sacred Winds", "Skyward Pride", "Wolf's Gravestone", "Skyward Spine", "Primordial Jade Winged-Spear", "Skyward Blade", "Aquila Favonia"]

    standard_5star_rate = 0.007
    soft_pity_5star_lin_rate = 0.993 / 17
    standard_4star_rate = 0.06
    soft_pity_4star_rate = 0.551
    featured_chance = 0.75

    def __init__(self, id):
        self.name = name
        self.is_event_banner = self.name != self.standard_name
        self.featured_5star_items = featured_5star_items
        self.featured_4star_items = featured_4star_items

'''