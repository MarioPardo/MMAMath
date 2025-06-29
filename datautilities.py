import json
import os
import random
from datetime import datetime

FIGHTERS_FILE = "fighters.json"
FIGHTS_FILE = "fights.json"
RESULT_TYPES = ["KO/TKO", "SUB", "UDEC", "SDEC", "MDEC", "Draw"]

#### FUNCTIONS TO LOAD AND SAVE DATA ####

def load_json_file(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except json.JSONDecodeError:
        print(f"⚠️ Warning: {filepath} is not a valid JSON file. Returning empty dict.")
        return {}

def load_fighters():
    return load_json_file(FIGHTERS_FILE)
    
def load_fights():
    return load_json_file(FIGHTS_FILE)

def save_fighters(fighters):
    with open(FIGHTERS_FILE, "w") as f:
        json.dump(fighters, f, indent=2)

def save_fights(fights):
    with open(FIGHTS_FILE, "w") as f:
        json.dump(fights, f, indent=2)



def generate_fighter_id(existing_ids, digits=7):
    while True:
        new_id = random.randint(1, 10**digits - 1)
        if new_id not in existing_ids:
            return new_id

def generate_fight_id(date_str, fighter1, fighter2):
    try:
        date_part = date_str.replace("-", "")  # "2025-05-07" -> "20250507"
        lastname1 = fighter1.strip().split()[-1]
        lastname2 = fighter2.strip().split()[-1]
        return f"{date_part}{lastname1}{lastname2}"
    except Exception as e:
        print(f"❌ Error generating fight ID: {e}")
        return None

def AddFighter(name, fightIDs=None):
    fightIDs = fightIDs or []
    fighters = load_fighters()

    # Check if name already exists
    for fid, fighter in fighters.items():
        if fighter["name"].lower() == name.lower():
            print(f"Fighter '{name}' already exists with ID {fid}")
            return fid

    # Generate unique ID
    existing_ids = set(fighters.keys())
    new_id = generate_fighter_id(existing_ids)

    # Create and append new fighter
    fighters[str(new_id)] = {"name": name, "fight_ids": fightIDs}
    save_fighters(fighters)

    print(f"Added fighter '{name}' with ID {new_id}")
    return new_id


# fighter1 is always the winner
def AddFight(fighter1name, fighter2name, date_str, result_str):
    fights = load_fights()  

    date = parse_date(date_str)
    if(parse_date == -1):
        return
   # Generate fight ID
    fight_id = generate_fight_id(date_str,fighter1name, fighter2name)

    # Check if fight already exists
    if fight_id in fights:
        print(f"Fight already exists: {fighter1name} vs {fighter2name} on {date_str}")
        return

    # Make sure both fighters exist
    f1_id = AddFighter(fighter1name)
    f2_id = AddFighter(fighter2name)
    

    # Add fight to fight list
    fights[fight_id] = {
        "winner": fighter1name,
        "loser": fighter2name,
        "date": date_str,
        "result": encode_result(result_str)
    }
    save_fights(fights)

    # Update each fighter’s fight list
    fighters = load_fighters()
    fighters[str(f1_id)]["fight_ids"].append(fight_id)
    fighters[str(f1_id)]["fight_ids"].sort(key=lambda x: int(str(x)[:8]), reverse=True)
    fighters[str(f2_id)]["fight_ids"].append(fight_id)
    fighters[str(f2_id)]["fight_ids"].sort(key=lambda x: int(str(x)[:8]), reverse=True)
    save_fighters(fighters)

    print(f" Fight added: {fighter1name} vs {fighter2name} on {date} ({result_str})")


def AddFightToFighter(fighter_id, fight_id):
    fighters = load_fighters()
    fighter = fighters.get(str(fighter_id))
    if fighter:
        if fight_id not in fighter["fight_ids"]:
            fighter["fight_ids"].append(fight_id)
            # Sort fight_ids by the first 8 digits (date part), descending
            fighter["fight_ids"].sort(key=lambda x: int(str(x)[:8]), reverse=True)
            print(f"Added fight {fight_id} to fighter ID {fighter_id}")
        else:
            print(f"Fight {fight_id} already exists for fighter ID {fighter_id}")
    else:
        print(f"Fighter with ID '{fighter_id}' not found.")




############


######  DATA MANAGEMENT FUNCTIONS ######

def get_fighter_by_id(fighter_id):
    fighters = load_fighters()
    return fighters.get(str(fighter_id), None)

def get_fighter_by_name(name):
    fighters = load_fighters()
    for fid, fighter in fighters.items():
        if fighter["name"].lower() == name.lower():
            return {fid: fighter}
    return None

def get_fights_by_fighter(fighter_name):
    fights = load_fights()
    fighter_fights = {}
    for fight_id, fight in fights.items():
        if fight["fighter1"].lower() == fighter_name.lower() or fight["fighter2"].lower() == fighter_name.lower():
            fighter_fights[fight_id] = fight
    return fighter_fights

def get_all_fighter_names():
    fighters = load_fighters()
    return [fighter["name"] for fighter in fighters.values()]


def get_result_from_dict(result_dict):
    for rtype in RESULT_TYPES:
        if result_dict.get(rtype, 0) == 1:
            return rtype
    return "Unknown"





# HELPER FUNCTIONS ######


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"❌ Invalid date format: '{date_str}'. Expected format: YYYY-MM-DD.")
        return -1
    
#Turn result string into dict of booleans aka 0/1
def encode_result(result_str):
    return {rtype: int(rtype == result_str) for rtype in RESULT_TYPES}
