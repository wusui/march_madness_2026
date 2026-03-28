# (c) 2026 Warren Usui
# This code is licensed under the MIT license (see LICENSE.txt
# for details)
"""
Create reality files
"""
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_reality(tourney, orgval):
    """
    Collect results of games played and create a file of the winners
    so far in this tournament
    """
    def write_reality(tlist):
        with open(f"{orgval}/{tourney}_reality.json", 'w',
                        encoding='utf-8') as ofd:
            json.dump(tlist, ofd, indent=4)
    driver = webdriver.Chrome()
    wpage = f"https://www.espn.com/{tourney}-college-basketball/bracket"
    driver.get(wpage)
    big_element = driver.find_element(By.TAG_NAME, 'html')
    html_data = big_element.get_attribute('outerHTML')
    driver.close()
    soup = BeautifulSoup(html_data, 'html.parser')
    blist = soup.find_all('div', class_="BracketCell__Name")
    wteamlist = list(map(lambda a: a.text, blist))[64:]
    playedlist = list(filter(lambda a: a != 'TBD', wteamlist))
    endofroundpts = [48, 56, 60]
    if len(playedlist) in endofroundpts:
        write_reality(playedlist)

if __name__ == "__main__":
    get_reality('mens', 'Mad_as_a_March_Llama')
    get_reality('womens', 'Mad_as_a_March_Llama')
