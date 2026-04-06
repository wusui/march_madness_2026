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
            return txtp + gen_poss(pattern[indx][1])(
                        nval >> len(pattern[0][0]))
        return gp_inn
    def rp_real(reality):
        return [reality, dict(list(map(lambda a: [a, histogram(hdata[1][a])],
                        list(hdata[1].keys()))))]
    def run_hyp(sim_res):
        return mk_hypotheticals(rp_real(histogram(last_full_rnd + sim_res)))
    def mk_btab(entries):
        def get_rnd_pairs(ecount):
            if ecount > 128:
                return 16
            if ecount > 8:
                return 8
            return 4
        def mk_records(entrys):
            def mk_rec_inner(person):
                pvalues = list(map(lambda a: {a[0]: 0, a[1]: 0}, mtches))
                w_outcomes = 0
                recs = list(filter(lambda a: person in a['winners'], entrys))
                tpoints = 0
                for entry in recs:
                    w_outcomes += 1
                    points = 1 / len(entry['winners'])
                    tpoints += points
                    trats = entry['scenario']
                    for pobj in pvalues:
                        tpair = list(pobj.keys())
                        if trats[tpair[0]] > trats[tpair[1]]:
                            pobj[tpair[0]] += points
                        else:
                            pobj[tpair[1]] += points
                return {'name': person, 'games': pvalues,
                        'pct_pt': tpoints / len(entrys),
                        'w_outcomes': w_outcomes}
            return mk_rec_inner
        torder = last_full_rnd[-get_rnd_pairs(len(entries)):]
        mtches1 = list(zip(torder[0::2], torder[1::2]))
        mtches = list(filter(lambda a: a[0] not in won_this_round and
                             a[1] not in won_this_round, mtches1))
        bracks = list(set(chain.from_iterable(
                            list(map(lambda a: a['winners'], entries)))))
        return list(map(mk_records(entries), bracks))
    def get_lfr(fullres):
        if fullres in range(48, 56):
            return 48
        if fullres in range(56, 60):
            return 56
        if fullres in range(60, 62):
            return 60
        return 62
    def fcheck(win_list):
        def fchk_inner(poswin):
            return all(list(map(lambda a: a in poswin, win_list)))
        return fchk_inner
    last_full_rnd = hdata[0][0:get_lfr(len(hdata[0]))]
    won_this_round = hdata[0][len(last_full_rnd):]
    rmatch = last_full_rnd[{48: 32, 56: 48, 60: 56, 62: 60
                            }[len(last_full_rnd)]:]
    pattern = dit_lev(rmatch)
    hyp_sit = list(map(gen_poss(pattern),
                    list(range(2 ** (63 - len(last_full_rnd))))))
    if won_this_round:
        hyp_sit = list(filter(fcheck(won_this_round), hyp_sit))
    wlist = list(map(run_hyp, hyp_sit))
    return [sorted(mk_btab(wlist), key=itemgetter('pct_pt',
                'w_outcomes'), reverse=True), won_this_round, len(hdata[0])]
