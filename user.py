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
    hard_5star_pity = 90
    soft_5star_pity = 74
    hard_4star_pity = 10
    soft_4star_pity = 9

    def __init__(self, unique_id, is_event_banner):
        self.unique_id = unique_id
        ref = db.collection(u'users').document(unique_id)

        pity_type = u'eventPity' if is_event_banner else u'standardPity'
        self.current_4star_pity = ref.get().to_dict()[pity_type]['curr4StarPity']
        self.featured_4star_pity = ref.get().to_dict()[pity_type]['feat4StarPity']
        self.current_5star_pity = ref.get().to_dict()[pity_type]['curr5StarPity']
        self.featured_5star_pity = ref.get().to_dict()[pity_type]['feat5StarPity']

    def increment_pity(self):
        self.current_4star_pity += 1
        self.current_5star_pity += 1

    def soft_reset_4star_pity(self):
        self.current_4star_pity = 0
        self.featured_4star_pity = True

    def hard_reset_4star_pity(self):
        self.current_4star_pity = 0
        self.featured_4star_pity = False
    
    def soft_reset_5star_pity(self):
        self.current_5star_pity = 0
        self.featured_5star_pity = True

    def hard_reset_5star_pity(self):
        self.current_5star_pity = 0
        self.featured_5star_pity = False

    def reset_all(self):
        self.hard_reset_4star_pity()
        self.hard_reset_5star_pity()

class Player:
    def __init__(self, unique_id):
        # assumes the player exists
        self.unique_id = unique_id
        self.ref = db.collection(u'users').document(unique_id)
        self.total_rolls = self.ref.get().to_dict()['totalRolls']
        self.event_pity = Pity(unique_id, True)
        self.standard_pity = Pity(unique_id, False)

    def increment_rolls(self, is_event_banner):
        self.total_rolls += 1
        pity = self.event_pity if is_event_banner else self.standard_pity
        pity.increment_pity()

    def get_pity(self, is_event_banner):
        return self.event_pity if is_event_banner else self.standard_pity
    
    def get_inventory(self):
        pass
        
    def get_history(self):
        pass

    def get_stats(self):
        pass

    def get_pity_info(self):
        pass

    def write_to_db(self):
        self.ref.update({
            u'totalRolls': self.total_rolls,
            u'eventPity': {
                u'curr4StarPity': self.event_pity.current_4star_pity,
                u'feat4StarPity': self.event_pity.featured_4star_pity,
                u'curr5StarPity': self.event_pity.current_5star_pity,
                u'feat5StarPity': self.event_pity.featured_5star_pity
            },
            u'standardPity': {
                u'curr4StarPity': self.standard_pity.current_4star_pity,
                u'feat4StarPity': self.standard_pity.featured_4star_pity,
                u'curr5StarPity': self.standard_pity.current_5star_pity,
                u'feat5StarPity': self.standard_pity.featured_5star_pity
            }
        })

    def reset(self):
        self.ref.update({
            u'totalRolls': 0,
            u'eventPity': {
                u'feat5StarPity': False,
                u'curr5StarPity': 0,
                u'feat4StarPity': False,
                u'curr4StarPity': 0
            },
            u'standardPity': {
                u'feat5StarPity': False,
                u'curr5StarPity': 0,
                u'feat4StarPity': False,
                u'curr4StarPity': 0
            }
        })

def get_unique_id(guild, member):
    return str(guild.id) + "-" + str(member.id)

def create_new_user(guild, member):
    unique_id = get_unique_id(guild, member)
    doc_ref = db.collection(u'users').document(unique_id)
    if not doc_ref.get().exists:
        doc_ref.set({
            u'username': member.name,
            u'guild': guild.name,
            u'totalRolls': 0,
            u'eventPity': {
                u'feat5StarPity': False,
                u'curr5StarPity': 0,
                u'feat4StarPity': False,
                u'curr4StarPity': 0
            },
            u'standardPity': {
                u'feat5StarPity': False,
                u'curr5StarPity': 0,
                u'feat4StarPity': False,
                u'curr4StarPity': 0
            }
        })
        return True
    return False

def get_player(guild, member):
    unique_id = get_unique_id(guild, member)
    return None if not db.collection(u'users').document(unique_id).get().exists else Player(unique_id)
