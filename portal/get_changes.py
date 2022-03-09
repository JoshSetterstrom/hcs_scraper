import time
from .session import Session
from .mongodb.get_queue_item import get_queue_item
from .mongodb.remove_queue_item import remove_queue_item
from .mongodb.remove_profile import remove_profile
from .mongodb.update_did import update_did
from .utils.update_profile import update_profile
from .utils.log_time import log_time
from .utils.current_time import current_time

def get_changes():
  session = Session(session_name="GET_CHANGES")
  session.start()
  print(f"[{log_time()}][{session.session_name}] Session Initialized.")
  
  session.login()
  session.wait_ec("xpath", "//button[@aria-label='View All CUCM Lines']")

  while True:
    if current_time():
      try:
        queue_item = get_queue_item()

        if queue_item:
          if "Delete" in queue_item['name']:
            remove_profile(queue_item['profile'], queue_item['type'])
            remove_queue_item(queue_item['profile'])
            print(f"[{log_time()}][{session.session_name}] Profile {queue_item['type']} {queue_item['profile']} has been removed.")

          else:
            session.driver.refresh()
            session.change_profile(queue_item['type'])
            session.wait_ec("xpath", "//li[contains(@id, 'app_simpleGrid_row_')]")
            session.add_filter(queue_item['profile'])
            session.get_json()
            update_profile("", queue_item['name'])
            update_did()
            remove_queue_item(queue_item['profile'])

            session.wait_ec("xpath", "//button[@class='gridPagingRemoveFilter']")
            session.find_element("xpath", "//button[@class='gridPagingRemoveFilter']").click()

        else: pass

        time.sleep(10)

      except Exception as e:
        print(f"[{log_time()}][{session.session_name}] Unexpected Error in Session: {e}")
        print(f"[{log_time()}][{session.session_name}] Skipping queue item.")

    else:
      ## Refresh session and prevent timeout ##
      session.logout()
      session.driver.close()
      session.driver.quit()
      time.sleep(300)
      get_changes()