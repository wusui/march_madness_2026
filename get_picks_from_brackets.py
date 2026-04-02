# (c) 2026 Warren Usui
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Read the bracket data in brackets.json and extract the contestants picks
"""
import json
from selenium import webdriver
from get_brackets_from_groups import get_dir_struct, make_html_soup
def extract_picks_from_bracket(brckt_data):
    """
    Given html file, return picks as a list of teams
    """
    driver = webdriver.Chrome()
    driver.get(brckt_data)
    soup = make_html_soup(driver)
    champ_pick = soup.find('span',
                        class_="PrintChampionshipPickBody-outcomeName")
    my_picks = soup.find_all('div', class_="PrintBracketOutcome-teamName")
    results = list(map(lambda a: a.text, my_picks))
    if champ_pick is None:
        driver.close()
        return []
    if champ_pick.text.startswith(results[-2]):
        results.append(results[-2])
    else:
        results.append(results[-1])
    driver.close()
    return results

def get_picks_from_brackets(tourney, orgval):
    """
    Call extract_picks_from_bracket for all bracket entries
    """
    dstruct = get_dir_struct()
    mid_dir =  dstruct[tourney]
    with open(f'{orgval}/brackets.json', 'r', encoding='utf-8') as json_file:
        brackets = json.load(json_file)
    entry_list = []
    for brack in brackets[tourney]:
        pfile = '/'.join(['https://fantasy.espn.com/games',
                         mid_dir, f'bracket?id={brack[0]}'])
        pick_values = pfile
        my_pix = extract_picks_from_bracket(pick_values)
        print(brack[1])
        entry_list.append([brack[0], my_pix[64:]])
    result = dict(list(filter(None, entry_list)))
    with open(f"{orgval}/{tourney}_picks.json", 'w', encoding='utf-8') as ofd:
        json.dump(result, ofd, indent=4)

if __name__ == "__main__":
    get_picks_from_brackets('womens', 'Mad_as_a_March_Llama')
    get_picks_from_brackets('mens', 'Mad_as_a_March_Llama')
