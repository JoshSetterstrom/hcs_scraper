from deepdiff import DeepDiff
from .log_time import log_time

def compare_json(old, new):
  changes = []
  
  if not old:
    return [{
      "timestamp": log_time(), 
      "action": "profile_created", 
      "value": "Profile created."
    }]

  ddiff = DeepDiff(old, new)

  for change in ddiff:
    if change == 'type_changes' or change == 'dictionary_item_removed': continue

    for key in ddiff[change]:
      item = str(key).split('root')[1]

      if change == 'iterable_item_removed':
        if "['lines']['line']" in key:
          changes.append({
            "timestamp": log_time(), 
            "action": change, 
            "value": f"{item} {ddiff[change][key]['dirn']['pattern']} removed"
        })
        else:
          changes.append({
            "timestamp": log_time(), 
            "action": change, 
            "value": f"{item} removed"
          })

      if change == 'values_changed':
        changes.append({
          "timestamp": log_time(), 
          "action": change, 
          "value": (f"{item} {ddiff[change][key]['old_value']} "+ 
                    f"changed to {ddiff[change][key]['new_value']}")
        })

  return changes