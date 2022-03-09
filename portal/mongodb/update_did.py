from pymongo import MongoClient

def update_did():
  client = MongoClient("mongodb://localhost:27017")
  dids = client['profiles']['did'].find({}, {'_id': False})

  for did in dids:
    if not did['line']: continue

    if did['description'] and 'Spare' in did['description']:
      print(did)
      # line = client['profiles']['lines'].find_one({"profile": did['line']})

      # if line:
      #   print(line['profile'])
      #   did['description'] = line['data']['alertingName']
      #   did['assigned'] = True

      # else:
      #   did['description'] = "Spare"
      #   did['assigned'] = False

      # client['profiles']['did'].find_one_and_update({"line": did['line']}, {"$set": did})

update_did()