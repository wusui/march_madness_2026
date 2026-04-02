# Copyright (C) 2024, 2025, 2026 Warren Usui, MIT License
"""
I/O operations for reading json data and producing html files.

Main entry point for the web page data independent calculations.
Data for the json files can be extracted from web page dependent scraping
code.
"""
import json
from solver import rank_picks
from html_gen import make_html

def predictions(tourney, orgdir):
    """
    Read the reality.json file for tournament results, and the picks.json
    file to get everybody's individual picks.  Returns the player data and
    a possessive label for the header of the html file.
    """
    def possess(in_string):
        if in_string.endswith('s'):
            return in_string[:-1] + "'s"
        return in_string
    with open(f'{orgdir}/{tourney}_reality.json', 'r', encoding='utf-8') as fd1:
        in_data = fd1.read()
    reality = json.loads(in_data)
    #if len(reality) not in [48, 56, 60]:
    #    print("Can't handle this number of games")
    #    return 'Error'
    with open(f'{orgdir}/{tourney}_picks.json', 'r', encoding='utf-8') as fd2:
        tdata = fd2.read()
    picks = json.loads(tdata)
    return [rank_picks([reality, picks]), possess(tourney.capitalize())]

def make_rpage(tourney, orgdir):
    """
    Open the output html file and write the make_html data to it
    """
    def teams_left():
        with open(f'{orgdir}/{tourney}_reality.json', 'r', encoding='utf-8'
                        ) as jsonfd:
            resultsl = json.load(jsonfd)
            return 64 - len(resultsl)
    def gen_result_page():
        return f'{orgdir}/{tourney}_results_{teams_left()}.html'
    display_html = make_html(predictions(tourney, orgdir), orgdir)
    if display_html == 'Error':
        return
    with open(gen_result_page(), 'w', encoding='utf-8') as fd3:
        fd3.write(display_html)

if __name__ == "__main__":
    make_rpage('mens', 'Mad_as_a_March_Llama')
    #make_rpage('womens', 'Mad_as_a_March_Llama')
