import time, getpass, os, json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .utils.log_time import log_time

with open('../config.json', 'r') as file: config = json.load(file)

class Session():
  def __init__(self, session_name=""):
    self.session_name = session_name
    self.wait_ec_timeout = 0
    self.current_profile = 1
    self.current_profile_timeout = 0


  ## Create chromdriver instance and direct to HCS Portal login ##
  def start(self, headless=False):
    print(f"[{log_time()}][{self.session_name}] Initializing ChromeDriver")

    op = webdriver.ChromeOptions()
    op.add_argument("--log-level=3")
    op.add_argument("--start-maximized")            ## Required to prevent elements from being "out of sight" ##
    op.add_argument("--window-size=1920x1080")      ###       Mostly required for headless instances        ###
    if headless: op.add_argument('--headless')

    self.driver = webdriver.Chrome("C:/Users/Josh/Desktop/ld/hcs_scraper/portal/chromedriver.exe", options=op)
    self.driver.maximize_window()
    self.driver.get("https://hcsportal.allstream.com/login/")


  ##Login into HCS Portal with specified credentials##
  def login(self):
    # if not os.environ['USER'] and not os.environ['PW']:
    #   os.environ['USER'] = getpass.getuser()
    #   os.environ['PW'] = getpass.getpass()
    
    try:
      self.find_element("id", "id_username").send_keys(config[0])
      self.find_element("id", "id_password").send_keys(config[1])
      self.find_element("id", "login-button").click()

    except:
      print(f"[{log_time()}][{self.session_name}] Caught Error: Unable to log into HCS Portal")
      self.driver.close()
      self.driver.quit()
      return

    print(f"[{log_time()}][{self.session_name}] Successfully logged into HCS Portal.")


  ##Logout of HCS Portal
  def logout(self):
    self.find_element("id", "username").click()
    self.find_element("xpath", "//li[@data-dojo-attach-point='logout']").click()
    time.sleep(10)
    print(f"[{log_time()}][{self.session_name}] Successfully logged out of HCS Portal.")


  ##Single level, more manageable find_element or find_elements method for selenium##
  def find_element(self, type, name, element="element"):
    method = [x for x in dir(self.driver) if f"find_{element}_by_{type}" in x]
    function = getattr(self.driver, method[0])
    return function(name)


  ##Waits for element to render to DOM before acting##
  def wait_ec(self, element, name):
    method = [x for x in dir(By) if element.upper() in x]
    function = getattr(By, method[0])

    try:
      WebDriverWait(self.driver, 60).until(
        EC.presence_of_element_located((function, name)))
      self.wait_ec_timeout = 0

    except:
      self.wait_ec_timeout+=1
      
      if self.wait_ec_timeout > 3:
        print(f"[{log_time()}][{self.session_name}] WaitEC timed out too many times. Ending session...")
        self.logout()
        time.sleep(5)
        self.driver.close()
        self.driver.quit()
        return

      print(f"[{log_time()}][{self.session_name}] WaitEC timed out waiting for {name}.")
      print(f"[{log_time()}][{self.session_name}] Retrying {self.wait_ec_timeout} of 3 times.")
      self.driver.refresh()
      self.wait_ec(element, name)


  ##Changes profile type to focus##
  ##Acceptable profiles [Lines, Phones, Subscribers, Voicemail]##
  def change_profile(self, profile):
    self.wait_ec("xpath", "//button[contains(@id, 'app_button_Button_')]")
    self.find_element("id", "app_newMenu_item_3").click()
    elements = self.find_element("class_name", "submenu").find_elements_by_xpath(".//*")
    
    for e in elements:
      if e.text == profile:
        e.click()
        break

    print(f"[{log_time()}][{self.session_name}] Focused profile changed to {profile.title()}.")


  ##Change location of profile list##
  def change_location(self, string):
    self.find_element("id", "dropdown_app_view_simpleControls_Dropdown_1_chosen").click()
    self.find_element("id", "id-app_view_simpleControls_Dropdown_1-chosen-search").send_keys(string)
    elements = self.find_element("class_name", "active-result", "elements")
    for item in elements:
      if string in item.text: 
        item.click()


  ##Adds specified filter to current profile list## 
  def add_filter(self, string):
    self.find_element("xpath", "//button[@data-dojo-attach-point='gridFilterDOM']").click()
    self.wait_ec("id", "dijit_form_TextBox_0")
    self.find_element("id", "dijit_form_TextBox_0").send_keys(string)
    self.find_element("xpath", "//button[@data-dojo-attach-point='applyFilterButton']").click()
    print(f"[{log_time()}][{self.session_name}] Added filter: {string}")


  ##Changes total items to render per page##
  ##Acceptabele ints [25, 50, 100, 200, 500, 1000, 2000]##
  def change_total(self, int):
    self.wait_ec("id", "gridPerPage")
    self.find_element("id", "gridPerPage").click()
    self.find_element("xpath", f"//tr[@aria-label='{int} ']").click()
    print(f"[{log_time()}][{self.session_name}] Changed page total to {int}.")


  ##Navigates to desired page## 
  def navigate_page(self):
    print(f"[{log_time()}][{self.session_name}] Navigating to next page...")
    self.wait_ec("xpath", "//li[contains(@id, 'app_simpleGrid_row')]")
    if self.find_element("id", "gridPageNext").get_attribute("disabled"): return False
    self.find_element("id", "gridPageNext").click()
    time.sleep(5)
    return True


  ##Downloads all JSON files from profiles page##
  def get_json(self):
    def get_progress():
      return self.find_element("id", "app_progressII_Progress_2").get_attribute("style")

    try:
      self.wait_ec("xpath", "//li[contains(@id, 'app_simpleGrid_row_')]")
      list = self.find_element("xpath", "//input[contains(@id, 'dijit_form_CheckBox_')]", "elements")
      list[0].click()

      action = self.find_element("xpath", "//div[@class='btn-group dropdownButtonContainer menuButtonContainer']")
      self.driver.execute_script("arguments[0].setAttribute('class','btn-group dropdownButtonContainer menuButtonContainer open')", action)
      self.wait_ec("xpath", "//ul[@id='id_dropdown_button_row-gridMenu']")
      ddl = self.find_element("xpath", "//ul[@id='id_dropdown_button_row-gridMenu']").find_elements_by_tag_name("li")
      for item in ddl:
        if item.text == "Export": item.click()
      self.wait_ec("xpath", "//div[@item='0']")
      self.find_element("xpath", "//div[@item='0']").click()
      self.find_element("xpath", "//button[@class='btn btn-primary btn-xs no-border']").click()
      time.sleep(1)
      while str(get_progress()) == "visibility: visible; height: 80px; z-index: 999;": pass
      time.sleep(1.5)

    ##Catches any timeouts or errors and saves current position, then recalls get_json##
    except Exception as e:
      print(f"[{log_time()}][{self.session_name}] Exception: {e}")
      self.logout()
      self.driver.close()
      self.driver.quit()
      return