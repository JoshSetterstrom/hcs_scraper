from pymongo import MongoClient

def remove_profile(profile, type):
  client = MongoClient("mongodb://localhost:27017")
  client['profiles'][type].find_one_and_delete({"profile": profile})