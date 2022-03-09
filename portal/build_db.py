from .session import Session
from .utils.update_profile import update_profile

def build_db(profiles):
  session = Session()
  session.start()
  session.login()

  for profile in profiles:
    session.change_profile(profile)
    session.change_total("2000")

    for _ in range(1, 1000):
      session.get_json()
      if session.navigate_page(): pass
      else: break

  session.logout()
  update_profile("", "")