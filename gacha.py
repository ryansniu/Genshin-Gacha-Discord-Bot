import random
import user

class Banner:
    standard_name = "Standard"
    standard_5star_chars = ["Diluc", "Jean", "Keqing", "Mona", "Qiqi"]
    standard_5star_weaps = ["Skyward Harp", "Amos' Bow", "Skyward Atlas", "Lost Prayer to the Sacred Winds", "Skyward Pride", "Wolf's Gravestone", "Skyward Spine", "Primordial Jade Winged-Spear", "Skyward Blade", "Aquila Favonia"]
    standard_4star_chars = ["Amber", "Barbara", "Beidou", "Bennett", "Chongyun", "Diona", "Fischl", "Kaeya", "Lisa", "Ningguang", "Noelle", "Razor", "Rosaria", "Sucrose", "Xiangling", "Xingqiu", "Xinyan", "Yanfei"]
    standard_4star_weaps = ["Favonius Warbow", "Sacrificial Bow", "The Stringless", "Rust", "Favonius Codex", "Sacrificial Fragments", "The Widsith", "Eye of Perception", "Favonius Greatsword", "Sacrificial Greatsword", "The Bell", "Rainslasher", "Favonius Lance", "Dragon's Bane", "Favonius Sword", "Sacrificial Sword", "The Flute", "Lion's Roar"]
    standard_3star_weaps = ["3-Star Weapon"]

    standard_5star_rate = 0.006
    soft_pity_5star_y = 0.994
    soft_pity_5star_x = 17
    standard_4star_rate = 0.051
    soft_pity_4star_rate = 0.551

    def __init__(self, name = standard_name, featured_5star_chars = [], featured_4star_chars = []):
        self.name = name
        self.is_event_banner = self.name != self.standard_name
        self.featured_5star_chars = featured_5star_chars
        self.featured_4star_chars = featured_4star_chars

    def get_5star_pool(self, pity):
        if self.is_event_banner and (pity.featured_5star_pity or random.choice((True, False))): # roll a featured 5-star character
            pity.hard_reset_5star_pity()
            return self.featured_5star_chars
        else: # roll a standard 5-star character
            pity.soft_reset_5star_pity()
            return self.standard_5star_chars + self.standard_5star_weaps

    def get_4star_pool(self, pity):
        if self.is_event_banner and (pity.featured_4star_pity or random.choice((True, False))): # roll a featured 4-star character
            pity.hard_reset_4star_pity()
            return self.featured_4star_chars
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

        curr_5star_rate = self.standard_5star_rate + max(0, pity.current_5star_pity - pity.soft_5star_pity + 1) * self.soft_pity_5star_y / self.soft_pity_5star_x
        curr_4star_rate = self.soft_pity_4star_rate if pity.current_4star_pity >= pity.soft_4star_pity else self.standard_4star_rate

        if pity.current_5star_pity >= pity.hard_5star_pity: # check for guaranteed 5-star pity
            rarity = 5
        elif pity.current_4star_pity >= pity.hard_4star_pity: # check for guaranteed 4+star pity
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
            emoji = ":yellow_circle:" if (wish in self.standard_5star_chars) or (wish in self.featured_5star_chars) else ":yellow_square:"
        elif rarity == 4:
            emoji = ":purple_circle:" if (wish in self.standard_4star_chars) or (wish in self.featured_4star_chars) else ":purple_square:"
        
        return emoji + " " + wish
