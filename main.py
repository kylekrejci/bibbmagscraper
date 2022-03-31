from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import requests
import json
import csv

data = []
today = date.today()
threedays = timedelta(days=3)
todayminusthreedays = today - threedays

todayformatted = today.strftime("%y-%m-%d")
todayminusthreedaysformatted = todayminusthreedays.strftime("%y-%m-%d")

driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()))
driver.get("https://case.maconbibb.us")

element1 = driver.find_element(By.NAME, "caseNumber")
element1.send_keys("22")

element2 = driver.find_element(By.NAME, "startingDate")
element2.send_keys(todayformatted)

element3 = driver.find_element(By.NAME, "endingDate")
element3.send_keys(todayminusthreedaysformatted)

submit = driver.find_element(By.ID, "search-btn")
submit.click()

time.sleep(150)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

driver.close()

links = []
cells = []
for rows in soup.find_all('tr'):
    cells.append(rows.find_all('td'))

for cell in cells:
    if len(cell) == 0:
        continue
    if str(cell[1]) == '<td class="text-left">Complaint</td>':
        links.append(str(cell[5]))
    elif str(cell[1]) == '<td class="text-left">Garnishment - Continuing</td>':
        links.append(str(cell[5]))
    elif str(cell[1]) == '<td class="text-left">Garnishment</td>':
        links.append(str(cell[5]))
    else:
        continue

linksformatted = []
urlbeginning = "https://case.maconbibb.us"

for link in links:
    linksformatted.append(''.join([urlbeginning, link[57:82]]))

for caseurl in linksformatted[:400]:
    row = []

    r = requests.get(caseurl)

    if r is None:
        continue

    rtext = r.text

    casesoup = BeautifulSoup(rtext, 'html.parser')

    scripts = casesoup.find_all("script")

    datascript0 = scripts[1]
    datascript1 = str(datascript0)
    datascript2 = datascript1[20:-10]
    datascript3 = json.loads(datascript2)

    if type(datascript3) is not dict:
        continue

    parties = datascript3.get("parties")

    defendant0 = parties[0]
    defendant1 = json.dumps(defendant0)
    defendant2 = json.loads(defendant1)
    defendant3 = defendant2["fullName"]
    defendant4 = defendant3.swapcase()
    defendant5 = defendant4.title()
    defendant6 = defendant5.split(", ")

    if len(defendant6) > 1:
        defendantfirstname = defendant6[1]
        defendantlastname = defendant6[0]
    else:
        continue

    if defendantfirstname is None:
        continue
    if defendantlastname is None:
        continue

    row.append(defendantfirstname)
    row.append(defendantlastname)

    address0 = defendant2["person"]
    address1 = json.dumps(address0)
    address2 = json.loads(address1)
    address3 = address2.get('address')

    if type(address3) is not dict:
        continue

    addressnumber = address3.get('address1')

    addressstreetandapartmentnumber0 = address3.get('address2')

    if type(addressstreetandapartmentnumber0) is not str:
        continue

    addressstreetandapartmentnumber1 = addressstreetandapartmentnumber0.swapcase()

    if type(addressstreetandapartmentnumber1) is not str:
        continue

    addressstreetandapartmentnumber2 = addressstreetandapartmentnumber1.title()

    if type(addressstreetandapartmentnumber2) is not str:
        continue

    fulladdress = " ".join([addressnumber, addressstreetandapartmentnumber2])

    row.append(fulladdress)

    city0 = address3["city"]
    city1 = city0.swapcase()
    city2 = city1.title()

    row.append(city2)

    state = address3["state"]

    row.append(state)

    zipcode = address3["zip"]

    row.append(zipcode)

    data.append(row)

header = ["FirstName", "LastName", "Address", "City", "State", "ZIP"]
with open('mailinglist.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

quit()