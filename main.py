import time, threading, portal

def main():
  check = threading.Thread(target=portal.check_changes)
  get = threading.Thread(target=portal.get_changes)

  check.start()
  time.sleep(30) ## Prevent multiple logins at same time ##
  get.start()

main()