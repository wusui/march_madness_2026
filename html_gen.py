# Copyright (C) 2024, 2025, 2026 Warren Usui, MIT License
"""
Generate the html file used to output results.

The data input to make_html consists of records that will be formatted into
the table header and individual rows of the table, and text to be added to
the text header.
"""
import os
import datetime
import json
from jinja2 import Environment, FileSystemLoader
import pandas as pd

def df_columns(solution):
    """
    Generate the columns headers for the dataframe
    """
    def mk_games():
        """
        Generate the column headers for each game
        """
        def igms():
            """
            Generate the column headers for a game
            """
            return list(map(lambda a: list(a.keys()), solution[0]['games']))
        return list(map(lambda a: '<div>' + a[0] + '</div><div>' + \
                        a[1] + '</div>', igms()))
    return ['<div>NAME<div>', '<div>Winning</div>\n<div>Outcomes</div>',
            '<div>Probable</div>\n<div>Payoff</div>\n'] + mk_games()

def get_ccode(fgame):
    """
    Handle the colors used by the individual cells in the table.
    """
    def gc_inner(dvals):
        """
        Call setf_dvals with numbers representing the color in an
        intermediate form.
        """
        def setf_dvals(cnumbs):
            """
            Convert results to a color in the red to green range
            """
            def setbg_vals(icol):
                """
                Use the color value to vary either the red range
                or green range in the html in the cell.
                """
                if icol < 256:
                    return f'#{icol:02x}ff00'
                return f'#ff{max(511 - icol, 0):02x}00'
            return setbg_vals(int(512 * cnumbs[0] / cnumbs[1] + .5))
        return setf_dvals([abs(dvals[0] - dvals[1]), dvals[0] + dvals[1]])
    return gc_inner(list(fgame.values()))

def df_rows(solution, id_peeps):
    """
    solution is a list of row entries where each row is a list of
    cell values.  Format each cell value to contain the html data
    for that cell (either text, or text on a colored background)
    """
    def strfy(nfloat):
        """
        Format a fractional share in the table.
        """
        return f'{nfloat:.6f}'
    def const_row(row):
        """
        Construct a formatted row
        """
        def left_cols():
            """
            Format the first three columns of a row entry
            """
            return [id_peeps[row['name']], row['w_outcomes'],
                                        strfy(row['pct_pt'])]
        def game_field(fgame):
            """
            fgame is a dict indexed by team names whose values are the
            number of winning entries occur when the team named in the
            index wins the game.  This should return an html table cell
            with the right color for the background.
            """
            def gstyle(style_data):
                """
                Handle white on black cells first (only one team can
                win without busting this bracket). If both teams can
                still win, call get_ccode to format the cell.
                """
                if style_data[0][1] == 0:
                    return '#000000;color:#ffffff'
                return get_ccode(fgame)
            def get_style(teams):
                """
                Return either a '*' if this game has no effect on the
                bracket, or a formatted cell if this pick has some
                importance.
                """
                if teams[0][1] == teams[1][1]:
                    return '*'
                return f'<div style=background-color:{gstyle(teams)}>' + \
                        f'{teams[1][0]}</div>'
            return get_style(sorted(list(zip(fgame.keys(), fgame.values())),
                            key=lambda a: a[1]))
        return left_cols() + list(map(game_field, row['games']))
    return list(map(const_row, solution))

def make_html(solution, orgdir):
    """
    String together all the pieces that compose the html data returned
    as a string.  A pandas dataFrame is used save the table information.
    The dataFrame is converted to an html table that is inserted inside
    a jinja2 formatted html file.
    """
    def set_level(fields):
        """
        Generate the header text for the table.
        """
        return f'{64 - fields[0][2]} teams left'
    def get_template():
        """
        If there is a ../madlib directory, use that directory to find
        the template.html file.  Otherwise, try the current directory.
        """
        pythonpath_os = os.environ.get('PYTHONPATH')
        if 'madlib' in pythonpath_os:
            return f'..{os.sep}madlib'
        return '.'
    if solution == 'Error':
        return solution
    environment = Environment(loader=FileSystemLoader(get_template()))
    template = environment.get_template('template.html')
    oheader = df_columns(solution[0][0])
    prefix = solution[1].replace("'",'').lower()
    with open(f'{orgdir}/brackets.json', 'r', encoding='utf-8') as fd2:
        people = fd2.read()
    id_peeps = dict(json.loads(people)[prefix])
    dframe = pd.DataFrame(df_rows(solution[0][0], id_peeps), columns=oheader)
    tourn = solution[1]
    tlevel = set_level(solution)
    tyear = datetime.date.today().year
    return template.render(tourn=tourn, out_table=dframe.to_html(
            escape=False, index=False), tyear=tyear, tlevel=tlevel)
