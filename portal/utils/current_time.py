from datetime import datetime

def current_time():
  current_time = int(''.join(str(datetime.now().time()).split(':')[:-1]))

  return True if current_time < 5 else False