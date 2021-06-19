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

def get_banner(banner_id, version):
    if banner_id == 'beginner':
        return BeginnerBanner()
    elif banner_id == 'standard':
        return StandardBanner(version)
    else:
        character_banners = json.load(open('data/character-banners.json'))
        if banner_id in character_banners:
            return EventBanner(True, banner_id)
        weapon_banners = json.load(open('data/weapon-banners.json'))
        if banner_id in weapon_banners:
            return EventBanner(False, banner_id)
        return None

class Banner(ABC):
    standard_5star_rate = 0.006
    soft_pity_5star_lin_rate = 0.994 / 17
    standard_4star_rate = 0.051
    soft_pity_4star_rate = 0.551

    def __init__(self, banner_type, banner_id = None):
        self.banner_type = banner_type
        self.import_data()

    @abstractmethod
    def import_data(self):
        pass

class BeginnerBanner(Banner):
    excluded_4star_chars = ['amber', 'kaeya', 'lisa', 'noelle']
    guaranteed_4star_char = 'noelle'

    def __init__(self):
        self.name = "Beginner"
        Banner.__init__(self, BannerType.BEGINNER)
    
    def import_data(self):
        characters = json.load(open('data/standard-characters.json'))
        weapons = json.load(open('data/standard-weapons.json'))
        self.standard_5star_chars = characters['1.0'][0]['standard_5star_chars']
        self.standard_4star_chars = [char for char in characters['1.0'][0]['standard_4star_chars'] if char not in self.excluded_4star_chars]
        self.standard_3star_weaps = weapons['1.0'][0]['standard_3star_weaps']

    def ten_pull(self, player):
        player.increment_beginner_rolls()
        pity = player.get_pity(self.banner_type)
        all_pulls = []
        for _ in range(10):
            player.increment_rolls(self.banner_type)
            
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
                rarity = 5 if (player.get_num_beginner_rolls() > 1) and (random.random() < self.standard_5star_rate) else 4
            else: # standard or soft pity roll
                rarity = 5 if random.random() < curr_5star_rate else 4 if random.random() < curr_4star_rate else 3
            pity.reset(rarity, False)

            # get the pool of potential items and then one at random
            rarity_pool = []
            if rarity == 5:
                rarity_pool = self.standard_5star_chars
            elif rarity == 4:
                if player.get_num_beginner_rolls() > 1 or self.guaranteed_4star_char in all_pulls:
                    rarity_pool = self.standard_4star_chars
                else:
                    rarity_pool = [self.guaranteed_4star_char]
            elif rarity == 3:
                rarity_pool = self.standard_3star_weaps
            wish = random.choices(rarity_pool)[0]
            player.add_new_item(wish)
            player.debug_info[rarity - 3] += 1

            # formats the output
            emoji = ":yellow_circle:" if rarity == 5 else ":purple_circle:" if rarity == 4 else ":blue_square:"
            all_pulls.append(emoji + " " + wish)
        return all_pulls


class StandardBanner(Banner):
    def __init__(self, version):
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
                    self.standard_5star_chars += version_contents['standard_5star_chars']
                if 'standard_4star_chars' in version_contents:
                    self.standard_4star_chars += version_contents['standard_4star_chars']
        
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

    def one_pull(self, player):
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
        player.add_new_item(wish)
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


class EventBanner(Banner):
    excluded_4star_chars = ['amber', 'kaeya', 'lisa']
    featured_chance = 0.5

    def __init__(self, is_char_banner, banner_id):
        self.is_char_banner = is_char_banner
        if not self.is_char_banner:
            self.standard_5star_rate = 0.007
            self.soft_pity_5star_lin_rate = 0.993 / 17
            self.standard_4star_rate = 0.06
            self.soft_pity_4star_rate = 0.47
            self.featured_chance = 0.75

        self.banner_id = banner_id
        Banner.__init__(self, BannerType.CHARACTER if self.is_char_banner else BannerType.WEAPON)
    
    def import_data(self):
        standard_characters = json.load(open('data/standard-characters.json'))
        standard_weapons = json.load(open('data/standard-weapons.json'))
        event_banner = json.load(open('data/character-banners.json' if self.is_char_banner else 'data/weapon-banners.json'))
        self.banner_data = event_banner[self.banner_id]
        self.version = self.banner_data['game-version']

        # get rid of this later when i can look characters and weapons up from the json
        self.standard_5star_chars = []
        self.standard_4star_chars = []
        for version in standard_characters:
            version_contents = standard_characters[version][0]
            if version_contents['patch'] <= self.version:
                if self.is_char_banner and 'standard_5star_chars' in version_contents:
                    self.standard_5star_chars += version_contents['standard_5star_chars']
                if 'standard_4star_chars' in version_contents:
                    self.standard_4star_chars += version_contents['standard_4star_chars']
        self.standard_4star_chars = [char for char in self.standard_4star_chars if char not in self.excluded_4star_chars]
        
        # get rid of this later when i can look characters and weapons up from the json
        self.standard_5star_weaps = []
        self.standard_4star_weaps = []
        self.standard_3star_items = []
        for version in standard_weapons:
            version_contents = standard_weapons[version][0]
            if version_contents['patch'] <= self.version:
                if not self.is_char_banner and 'standard_5star_weaps' in version_contents:
                    self.standard_5star_weaps += version_contents['standard_5star_weaps']
                if 'standard_4star_weaps' in version_contents:
                    self.standard_4star_weaps += version_contents['standard_4star_weaps']
                if 'standard_3star_weaps' in version_contents:
                    self.standard_3star_items += version_contents['standard_3star_weaps']
        
        # get the featured items
        self.featured_5star_items = self.banner_data['featured_5star_chars' if self.is_char_banner else 'featured_5star_weaps']
        self.featured_4star_items = self.banner_data['featured_4star_chars' if self.is_char_banner else 'featured_4star_weaps']
        
        self.standard_5star_items = [item for item in (self.standard_5star_chars + self.standard_5star_weaps) if item not in self.featured_5star_items]
        self.standard_4star_items = [item for item in (self.standard_4star_chars + self.standard_4star_weaps) if item not in self.featured_4star_items]

    def get_5star_pool(self, pity):
        if pity.get_value('feat5StarPity') or random.random() < self.featured_chance: # roll a featured 5-star item
            pity.reset(5, False)
            return self.featured_5star_items
        else: # roll a standard 5-star item
            pity.reset(5, True)
            return self.standard_5star_items

    def get_4star_pool(self, pity):
        if pity.get_value('feat4StarPity') or random.random() < self.featured_chance: # roll a featured 4-star item
            pity.reset(4, False)
            return self.featured_4star_items
        else: # roll a standard 4-star item
            pity.reset(4, True)
            return self.standard_4star_items

    def get_3star_pool(self, pity):
        return self.standard_3star_items

    def one_pull(self, player):
        rarity = 0
        rarity_pool = []

        # update player rolls and pity
        player.increment_rolls(self.banner_type) 
        pity = player.get_pity(self.banner_type)

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
        player.add_new_item(wish)
        player.debug_info[rarity - 3] += 1

        emoji = ":blue_square:"
        if rarity == 5:
            emoji = ":yellow_circle:" if wish in self.standard_5star_chars or (self.is_char_banner and wish in self.featured_5star_items) else ":yellow_square:"
        elif rarity == 4:
            emoji = ":purple_circle:" if wish in self.standard_4star_chars or (self.is_char_banner and wish in self.featured_4star_items) else ":purple_square:"
        
        return emoji + " " + wish

    # returns who's featured
    def get_info(self):
        pass