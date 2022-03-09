from pymongo import MongoClient

def remove_queue_item(pkid, json):
  client = MongoClient("mongodb://localhost:27017")
  return client['profiles']['profile_changes'].find_one({"pkid": pkid})