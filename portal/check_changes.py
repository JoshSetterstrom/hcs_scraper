import time, json

from .mongodb.hcsqueue import HCSQueue
from .session import Session
from .utils.get_id_list import get_id_list
from .utils.log_time import log_time
from .utils.current_time import current_time

def check_changes():
  with open("portal/json/cases.json", "r") as file: cases = json.load(file)

  session = Session(session_name="CHECK_CHANGES")
  session.start(headless=True)

  print(f"[{log_time()}][{session.session_name}] Session Initialized")

  session.login()
  session.wait_ec("xpath", "//button[@aria-label='View All CUCM Lines']")
  session.find_element("xpath", "//li[@class='icon blue inbox']").click()
  time.sleep(1)
  session.find_element("xpath", "//i[@class='icon-arrow-right']").click()
  session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")

  print(f"[{log_time()}][{session.session_name}] Checking for new transactions...")

  try:
    session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")
    session.change_total(50)
    session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")

    id_list = get_id_list(session)

    while True:
      if current_time():
        session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")

        new_id_list = get_id_list(session)

        if id_list == new_id_list: pass

        else:
          new_items = list(set(id_list) ^ set(new_id_list))

          for id in new_items:
            print(f"[{log_time()}][{session.session_name}] Retrieving {id}")


            transaction_list = (
              session.find_element("xpath", "//ul[@class='simpleGridContainer']")
              .find_elements_by_xpath(".//li"))

            for transaction in transaction_list:
              if "Success" in transaction.text and transaction.text[:9] == id:
                string = transaction.text

                for description, type in cases['cases'].items():
                  action = string.split('admin')[0][9:]

                  if description == action:
                    print(f"[{log_time()}][{session.session_name}] Adding {id} to queue")
                    queue = HCSQueue(session, session.session_name)
                    if "Bulk" in action: queue.add_queue_bulk(id, transaction, type, description)
                    else: queue.add_queue(id, transaction, type, description)
                    print(f"[{log_time()}][{session.session_name}] Checking for new transactions...")
                    break

                break

        id_list = new_id_list
        time.sleep(5)
        session.driver.refresh()

      else:
        ## Refresh session and prevent timeout ##
        print(f"[{log_time()}][{session.session_name}] Restarting Session...")
        session.logout()
        session.driver.close()
        session.driver.quit()
        time.sleep(300)
        print(f"[{log_time()}][{session.session_name}] Session Restarted.")
        check_changes()

  except Exception as e:
    print(f"[{log_time()}][{session.session_name}] Unexpected Error in Session: {e}")
    session.driver.refresh()
    pass