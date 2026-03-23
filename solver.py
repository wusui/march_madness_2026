# Copyright (C) 2024, 2025, 2026 Warren Usui, MIT License
"""
Create future bracket lists that contain all possible outcomes.
Run each individual against all possible brackets.
Find winning conditions for each individual and produce a sorted list
of possible winners and outcomes needed.
"""
from operator import itemgetter
from itertools import chain

def histogram(tlist):
    """
    Generate dict of wins predicted indexed by team name
    """
    def hst_in(tkeys):
        def hst_in2(team):
            return(team, len(list(filter(lambda a: a == team, tlist))))
        return dict(list(map(hst_in2, tkeys)))
    return hst_in(sorted(list(set(tlist))))

def score_sit(tdata):
    """
    Compute the points for a bracket
    """
    def ord_info(tdict):
        return dict(sorted(tdict.items(), reverse=True,
                           key=lambda item: item[1]))
    def scr_rec(brket):
        def tscore(tms):
            def get_pts(ateam):
                if ateam not in tdata[0]:
                    return 0
                return (2 ** (min(tms[ateam], tdata[0][ateam])) - 1) * 10
            return sum(list(map(get_pts, tms)))
        return [brket, tscore(tdata[1][brket])]
    return ord_info(dict(list(map(scr_rec, tdata[1]))))

def rank_picks(hdata):
    """
    Generate all possible remaining outcomes and produce the records that
    are displayed on the html page built by get_webpage
    """
    def mk_hypotheticals(tdata):
        scores = score_sit(tdata)
        winr = list(filter(lambda a: scores[a] == max(scores.values()), scores))
        return {'winners': winr, 'scenario': tdata[0]}
    def dit_lev(tlist):
        def gen_round(pairings):
            def gen_round2(countv):
                return list(map(lambda a: pairings[a][(countv >> a) % 2],
                             list(range(len(pairings)))))
            return gen_round2
        pairings = list(zip(tlist[0::2], tlist[1::2]))
        nround = list(map(gen_round(pairings), list(range(2 ** len(pairings)))))
        if len(nround) == 1:
            return nround
        return list(map(lambda a: [a, dit_lev(a)], nround))
    def gen_poss(pattern):
        def gp_inn(nval):
            indx = nval % (2 ** len(pattern[0][0]))
            txtp = pattern[indx][0]
            if len(txtp) == 1:
                return txtp
            return txtp + gen_poss(pattern[indx][1])(nval >> len(pattern[0][0]))
        return gp_inn
    def rp_real(reality):
        return [reality, dict(list(map(lambda a: [a, histogram(hdata[1][a])],
                        list(hdata[1].keys()))))]
    def run_hyp(sim_res):
        return mk_hypotheticals(rp_real(histogram(hdata[0] + sim_res)))
    def mk_btab(entries):
        def proc_b(bracket):
            def proc_w(wsample):
                wmarg = gwvals[len(entries)]
                wval = 1 / len(wsample['winners'])
                tlist = list(filter(lambda a: wsample['scenario'][a] >= wmarg,
                                    wsample['scenario']))
                return [wval, tlist]
            def tratings(tm_list):
                def tcount(team):
                    def add_val(tm_lst):
                        if team in tm_lst[1]:
                            return tm_lst[0]
                        return 0.0
                    return [team, sum(list(map(add_val, tm_list)))]
                uteams = list(set(chain.from_iterable(
                            list(map(lambda a: a[1], tm_list)))))
                return dict(list(map(tcount, uteams)))
            def matchup(tm_rats):
                def mtch_inner(matchup):
                    def set_v(team_indx):
                        if team_indx not in tm_rats:
                            return [team_indx, 0.0]
                        return [team_indx, tm_rats[team_indx]]
                    return dict(list(map(set_v, matchup)))
                return list(map(mtch_inner, mtches))
            gwvals = {32768: 3, 128: 4, 8: 5}
            winz = list(filter(lambda a: bracket in a['winners'], entries))
            wpoints = list(map(proc_w, winz))
            pvalue = sum(list(map(lambda a: a[0], wpoints)))
            return {'name': bracket, 'w_outcomes': len(winz),
                      'pct_pt': pvalue / len(entries),
                      'games': matchup(tratings(wpoints))}
        def gb_list(ent_list):
            return list(set(list(chain.from_iterable(
                    list(map(lambda a: a['winners'], ent_list))))))
        tmatch = {32768: 16, 128: 8, 8: 4}
        torder = hdata[0][-tmatch[len(entries)]:]
        mtches = list(zip(torder[0::2], torder[1::2]))
        return list(map(proc_b, gb_list(entries)))
    offset =  2 * len(hdata[0]) - 64
    rmatch = hdata[0][offset:]
    pattern = dit_lev(rmatch)
    hyp_sit = list(map(gen_poss(pattern),
                    list(range(2 ** (63 - len(hdata[0]))))))
    wlist = list(map(run_hyp, hyp_sit))
    return sorted(mk_btab(wlist), key=itemgetter('pct_pt', 'w_outcomes'),
                reverse=True)
