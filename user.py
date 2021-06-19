from gacha import BannerType

import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv()

cred = credentials.Certificate(os.getenv('FIREBASE_CRED'))
firebase_admin.initialize_app(cred)

db = firestore.client()

class Pity:
    DEFAULT_VALS = [0, False, 0, False]
    PITY_IDS = ['curr4StarPity', 'feat4StarPity', 'curr5StarPity', 'feat5StarPity']

    def __init__(self, doc, banner_type):
        self.data = doc[str(banner_type.name).lower() + 'Pity']
        
        self.hard_5star_pity = 80 if banner_type == BannerType.WEAPON else 90
        self.soft_5star_pity = 64 if banner_type == BannerType.WEAPON else 74
        self.hard_4star_pity = 9 if banner_type == BannerType.WEAPON else 10
        self.soft_4star_pity = 8 if banner_type == BannerType.WEAPON else 9

    def increment_pity(self):
        self.data[self.PITY_IDS[0]] += 1
        self.data[self.PITY_IDS[2]] += 1

    def reset(self, rarity, is_soft_reset):
        if rarity >= 4:
            pity_id = (rarity - 4) * 2
            self.data[self.PITY_IDS[pity_id]] = 0
            self.data[self.PITY_IDS[pity_id + 1]] = is_soft_reset
    
    def reset_all(self):
        self.reset(4, False)
        self.reset(5, False)
    
    def get_value(self, id):
        return self.data[id] if id in self.data else None


class Player:
    HISTORY_LIMIT = 1000

    def __init__(self, doc_ref, doc):
        # assumes the player exists
        self.doc_ref = doc_ref
        self.doc = self.doc_ref.get().to_dict()
        self.pities = dict()
        for banner_type in BannerType:
            self.pities[str(banner_type.name)] = Pity(self.doc, banner_type)

        self.debug_info = [0, 0, 0]

    def increment_rolls(self, banner_type):
        self.doc['totalRolls'] += 1
        self.get_pity(banner_type).increment_pity()
    
    def get_pity(self, banner_type):
        return self.pities[banner_type.name]

    def add_new_item(self, new_item):
        # update player history
        self.doc['history'].insert(0, new_item)
        if len(self.doc['history']) > self.HISTORY_LIMIT:
            self.doc['history'].pop()
        
        # update player inventory
        if new_item in self.doc['inventory']:
            self.doc['inventory'][new_item] += 1
        else:
            self.doc['inventory'][new_item] = 1

    def get_pity_info(self):
        pass

    def get_inventory(self):
        result = ""
        for item, count in self.doc['inventory'].items():
            result += item + " " + str(count) + "\n"
        return result
        
    def get_history(self):
        result = ""
        for item in self.doc['history']:
            result += item + ", "
        return result

    def get_stats(self):
        pass

    def write_to_db(self):
        self.doc_ref.set(self.doc)

    def get_num_beginner_rolls(self):
        return self.doc['numBeginnerRolls']

    def increment_beginner_rolls(self):
        self.doc['numBeginnerRolls'] += 1

    def reset(self):
        self.doc['totalRolls'] = 0
        self.doc['numBeginnerRolls'] = 0
        for banner_type in BannerType:
            self.pities[banner_type.name].reset_all()

    def get_debug_info(self):
        total = float(sum(self.debug_info))
        if total <= 0:
            return "No debug info yet!"
        output = "Total pulls: " + str(total) + '\n'
        output += "3 Stars: " + str(self.debug_info[0]) + ", " + str(self.debug_info[0] / total * 100) + "%\n"
        output += "4 Stars: " + str(self.debug_info[1]) + ", " + str(self.debug_info[1] / total * 100) + "%\n"
        output += "5 Stars: " + str(self.debug_info[2]) + ", " + str(self.debug_info[2] / total * 100) + "%\n"
        return output

def get_unique_id(guild, member):
    return str(guild.id) + "-" + str(member.id)

def create_new_user(guild, member):
    doc_ref = db.collection('users').document(get_unique_id(guild, member))
    if not doc_ref.get().exists:
        doc = {'username': member.name, 'guild': guild.name, 'totalRolls': 0, 'numBeginnerRolls': 0, 'history': [], 'inventory': {}}
        for banner_type in BannerType.__members__:
            doc[str(banner_type).lower() + 'Pity'] = dict(zip(Pity.PITY_IDS, Pity.DEFAULT_VALS))
        doc_ref.set(doc)
        return True
    return False

def get_player(guild, member):
    doc_ref = db.collection('users').document(get_unique_id(guild, member))
    doc = doc_ref.get()
    return None if not doc.exists else Player(doc_ref, doc)

def delete_user(guild, member):
    doc_ref = db.collection('users').document(get_unique_id(guild, member))
    doc = doc_ref.get()
    # TO-DO: delete user from database
    return False
