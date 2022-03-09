from .log_time import log_time

def edit_json(json, type, filename):
  print(f"[{log_time()}][GET_CHANGES] Updating {filename} JSON...")

  return {
    "type": type, 
    "profile": filename,
    "pkid": json['meta']['pkid'],
    "meta": json['meta'],
    "data": json['data']
  }