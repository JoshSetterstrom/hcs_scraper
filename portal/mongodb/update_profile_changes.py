from pymongo import MongoClient

def update_profile_changes(profile, file):
  client = MongoClient("mongodb://localhost:27017")
  client['profiles']['profile_changes'].find_one_and_update(
    {"profile": profile}, 
    {"$set": file}, 
    upsert=True)