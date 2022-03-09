import os, json
from pathlib import Path
from zipfile import ZipFile
from pymongo import MongoClient
from .compare_json import compare_json
from .edit_json import edit_json
from .log_time import log_time

def update_profile(session_name, action):
  path = os.path.expanduser('~')
  client = MongoClient("mongodb://localhost:27017")
  profile_changes = client['profiles']['profile_changes']

  for item in Path(f"{path}/Downloads").rglob("*.zip"):
    ZipFile(item, "r").extractall(f"{path}/Downloads")
    with open(str(item).split('.zip')[0], "r") as file:
      current_file = json.load(file)

    for profile in current_file['resources']:
      try: new_json = edit_json(profile, 'phones', profile['data']['name'])
      except: pass

      try: new_json = edit_json(profile, 'lines', profile['data']['pattern'])      
      except: pass

      try: new_json = edit_json(profile, 'subscribers', profile['data']['userid'])
      except: pass

      try: new_json = edit_json(profile, 'voicemail', profile['data']['Alias'])
      except: pass

    old_json = client['profiles'][new_json['type']].find_one(
      {'pkid': new_json['pkid']}, 
      {'_id': False})

    for change in compare_json(old_json, new_json):
      profile_changes.find_one_and_update(
        {'pkid': new_json['pkid']},
        {'$push': {'changes': change}},
        upsert=True)

    client['profiles'][new_json['type']].find_one_and_update(
      {"pkid": new_json['pkid']}, 
      {"$set": new_json},
      upsert=True)

    os.remove(item)

    for item in Path(f"{path}/Downloads").rglob("*.json"): os.remove(item)

    print(f"[{log_time()}][{session_name}] Updated {new_json['profile']}")