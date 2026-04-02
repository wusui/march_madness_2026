# (c) 2026 Warren Usui
# This code is licensed under the MIT license (see LICENSE.txt
# for details)
"""
Find the unique bracket ids entered in the men's and women's groups
"""
import os
import json
from time import sleep
from datetime import date
from configparser import ConfigParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_brackets_from_groups(orgdir):
    """
    Extract links to mens and womens groups and call get_groups to
    extract bracket information for each group.
    """
    config = ConfigParser()
    config.read('march_madness.ini')
    parse_info = config[orgdir]
    conf_dict = {}
    if config.has_option(orgdir, 'mens'):
        conf_dict['mens'] = parse_info["mens"]
    if config.has_option(orgdir, 'womens'):
        conf_dict['womens'] = parse_info["womens"]
    return get_groups(conf_dict)

def extract_user_ids(driver):
    """
    Find all user ids on the current driver page
    """
    soup = make_html_soup(driver)
    idlist = soup.find_all('a', href=True)
    newlist = list(filter(lambda a: "bracket?id" in a['href'], idlist))
    foundem = list(map(lambda a: [a['href'].split('=')[-1], a.text], newlist))
    return foundem

def make_html_soup(driver):
    """
    Get entire html page and convert to BeautifulSoup object
    """
    big_element = driver.find_element(By.TAG_NAME, 'html')
    html_data = big_element.get_attribute('outerHTML')
    return BeautifulSoup(html_data, 'html.parser')

def get_groups(in_groups):
    """
    Scan the groups and extract the bracket entry ids
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    ret_list = []
    for group, sdirv in get_dir_struct().items():
        driver = webdriver.Chrome(chrome_options)
        gpage = '/'.join([f"https://fantasy.espn.com/games/{sdirv}",
                          f"group?id={in_groups[group]}"])
        driver.get(gpage)
        sleep(5)
        first_element = driver.find_element(By.CSS_SELECTOR,
                                    'div[class="GroupCard-contentField"]')
        gsize = int(first_element.text[len('Group Size'):])
        pcount = gsize // 30
        if (gsize % 30) > 0:
            pcount += 1
        pcount += 1
        llist = []
        for nextb in range(2, pcount+1):
            llist.extend(extract_user_ids(driver))
            driver.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);")
            if nextb == pcount:
                continue
            button = driver.find_element(By.ID, f"{nextb}")
            sleep(2)
            button.click()
            sleep(5)
        ret_list.append([group, llist])
        driver.close()
    return dict(ret_list)

def get_dir_struct():
    """
    Make sure the getintermediate directory names have the right year
    """
    yrv = date.today().year
    return {'mens': f'tournament-challenge-bracket-{yrv}',
            'womens': f'tournament-challenge-bracket-women-{yrv}'}

def save_brackets(orgdir):
    """
    Stash bracket info away in json file
    """
    os.makedirs(orgdir, exist_ok=True)
    brackets = get_brackets_from_groups(orgdir)
    with open(f'{orgdir}/brackets.json', 'w', encoding='utf-8') as json_file:
        json.dump(brackets, json_file, indent=4)

if __name__ == "__main__":
    save_brackets('Mad_as_a_March_Llama')
