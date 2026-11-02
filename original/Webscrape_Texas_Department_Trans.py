from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import time
from time import sleep
from threading import Thread
import os
import datetime

# Get Driver Working
options = Options()
options.add_argument("start-maximized")
webdriver_service= Service('C:\\Users\\Jay_Oliver\\Downloads\\chromedriver-win64\\chromedriver.exe')

# driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options, service=webdriver_service)
#
now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
video_dir = f"G:\\TDOT Webscraping\\Webcam_{now}" #FIX DIRECTORY JAY!!!!!!!!!!
os.mkdir(video_dir)
os.chdir(video_dir)

#
district = ["ABL", "AMA", "ATL", "AUS", "BMT", "BWD", "BRY", "CHS",
            "CRP", "DAL", "ELP", "FTW", "HOU", "LRD", "LBB", "ODA",
            "PAR", "PHR", "SJT", "SAT", "TYL", "WAC", "WFS", "YKM"]

for district in district:

    # Add URL and get information
    url = f"https://its.txdot.gov/its/District/{district}/cameras"
    driver.get(url)

    # Find the element to scroll
    page = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div[1]/div[1]/div[1]/div[2]")

    if district == "HOU" or district=="DAL":
        fiveMinutes = Thread(target=lambda:sleep(35)) # 2 second thread
        fiveMinutes.start() # start wait time
    elif district == "FTW" or district=="ELP" or district=="SAT" or district=="AUS":
        fiveMinutes = Thread(target=lambda:sleep(20)) # 2 second thread
        fiveMinutes.start() # start wait time
    else:
        fiveMinutes = Thread(target=lambda:sleep(10)) # 2 second thread
        fiveMinutes.start() # start wait time

    x = 0
    y = 800
    while True:
        x +=800
        y +=800
        last_height = driver.execute_script(f"arguments[0].scroll({x}, {y});", page)
        time.sleep(.35)
        if not fiveMinutes.is_alive():
            break

    # Copy information
    webcams = driver.page_source
    page_soup = BS(webcams,"html.parser")
    names = page_soup.find_all('div', class_="card" )
    names = str(names)

    mylines = []
    img_address = []
    camera_name = []

    mylines.append(names.split('\n'))

    # Extract image link
    for element in mylines:
        for address in element:
            if "src=" in address:
                link = address.split('src="')[1]
                link = link.split('"')[0]
                img_address.append(link)

    ### Extract Camera Name
    for element in mylines:
        for name in element:
            if ' $data.icd_Id' in name:
                camera = name.split('>')[1]
                camera = camera.split('<')[0]
                camera_name.append(camera)

    # Write image link and info onto textfiles based on districts
    file = open(f'{district}.txt', 'w')
    for i in range(len(camera_name)):
        # Webshot - extract image
        file.write(str(f'{district}_{camera_name[i]}_{now}_{img_address[i]}\n\n'))
    file.close()
