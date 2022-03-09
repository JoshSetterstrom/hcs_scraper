import time
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

class HCSQueue():
  db = client['hcs_queue']['queue']
  bulk_val_container = "//tbody[@class='transactionGridContainer']"
  bulk_val_class = "//td[@class='transactionGridColumn transactionGridColumn-detail']"
  val_class = "//input[@class='dijitReset dijitInputInner']"
  val_li = "//li[contains(@id, 'app_form_formElements_Text_')]"

  def __init__(self, session, session_name):
    self.session = session
    self.session_name = session_name

  ## Creates queue and adds it to queuedb ##
  def add_queue_db(self, id, type, name, profile):
    if "at Site:" in str(profile) or 'at site' in str(profile): 
      profile = str(profile).split(' ')[0]
      
    new_queue = {
      "id": id,
      "type": type,
      "name": name,
      "profile": profile,
      "date": time.strftime('%Y-%m-%d %H:%M:%S')
    }

    self.db.insert_one(new_queue)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}][{self.session_name}] {type} {profile} added to queue.")

  
  def add_queue_bulk(self, id, transaction, type, description):
    transaction.click()
    time.sleep(2) ## Buffer to prevent reading of stale data ##
    self.session.wait_ec("xpath", self.bulk_val_container)
    values = self.session.find_element("xpath", self.bulk_val_class).find_elements_by_xpath(self.bulk_val_class)

    for value in values:
      profile = value.get_attribute('title')
      self.add_queue_db(id, type, description, profile)

    self.session.driver.execute_script("window.history.go(-1)")
    self.session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")


  def add_queue(self, id, transaction, type, description):
    transaction.click()
    self.session.wait_ec("xpath", self.bulk_val_container)
    time.sleep(1)
    li_values = self.session.find_element("xpath", self.val_li, "elements")
    values = li_values[2].find_elements_by_tag_name("input")
    profile = values[1].get_attribute('value')
    self.add_queue_db(id, type, description, profile)
    self.session.driver.execute_script("window.history.go(-1)")
    self.session.wait_ec("id", "simpleGrid_ColumnHeader_txn_seq_id")