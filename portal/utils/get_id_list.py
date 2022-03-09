def get_id_list(session):
  id_list = []

  ## Get list of transactions strings ##
  transaction_list = (
    session.find_element("xpath", "//ul[@class='simpleGridContainer']")
    .find_elements_by_xpath(".//li"))

  ## Converts transaction strings to ids ##
  for transaction in transaction_list: 
      if "Success" in transaction.text and not "system" in transaction.text:
        id_list.append(transaction.text[:9])

  return id_list