from pymongo import MongoClient

def get_queue_item():
  client = MongoClient("mongodb://localhost:27017")
  return client['hcs_queue']['queue'].find_one({})