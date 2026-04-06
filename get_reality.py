# (c) 2026 Warren Usui
# This code is licensed under the MIT license (see LICENSE.txt
# for details)
"""
Create reality files
"""
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def get_big_brack(tourney):
    """
    Return a Beautiful soup representation of the main bracket
    """
    driver = webdriver.Chrome()
    wpage = f"https://www.espn.com/{tourney}-college-basketball/bracket"
    driver.get(wpage)
    big_element = driver.find_element(By.TAG_NAME, 'html')
    html_data = big_element.get_attribute('outerHTML')
    driver.close()
    return html_data

def get_ltp_rnd(tourney, orgval):
    """
    Find most recent team to have won a game.
    """
    with open(f"{orgval}/{tourney}_reality.json", 'r',
                        encoding='utf-8') as ifd:
        lwinner = json.loads(ifd.read())
        gindx = len(lwinner) - 1
        startp = list(filter(lambda a: gindx in a, [range(48, 56), range(56, 60),
                                                range(60, 62), range(62, 63)]))[0][0]
    return lwinner[startp:], len(lwinner)

def get_reality(tourney, orgval):
    """
    Collect results of games played and create a file of the winners
    so far in this tournament
    """
    def write_reality(tlist):
        with open(f"{orgval}/{tourney}_reality.json", 'w',
                        encoding='utf-8') as ofd:
            json.dump(tlist, ofd, indent=4)
    htmldata = get_big_brack(tourney)
    soup = BeautifulSoup(htmldata, 'html.parser')
    blist = soup.find_all('div', class_="BracketCell__Name")
    wteamlist = list(map(lambda a: a.text, blist))[64:]
    playedlist = list(filter(lambda a: a != 'TBD', wteamlist))
    endofroundpts = [48, 56, 60, 62]
    print(len(playedlist))
    if len(playedlist) in endofroundpts:
        write_reality(playedlist)

if __name__ == "__main__":
    get_reality('mens', 'Mad_as_a_March_Llama')
    #get_reality('womens', 'Mad_as_a_March_Llama')
