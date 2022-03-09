from pymongo import MongoClient

def remove_queue_item(profile):
  client = MongoClient("mongodb://localhost:27017")
  client['hcs_queue']['queue'].find_one_and_delete({"profile": profile})