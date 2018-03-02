import sqlite3
import time
import random
import csv
import json

today = int(time.time()/86400)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def nCr(n,r):
    if n < r:
        return 0
    if n-r < r:
        return nCr(n, n-r)
    f = 1
    for i in range(r):
        f *= n-i
        f //= i+1
    return f

def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

def get_names(db):
    players = db.execute('SELECT pla_autoid AS id, pla_name AS name, pla_surname AS surname FROM snk_player').fetchall()
    return {p['id']: p['surname'] if sum([1 for t in players if t['surname']==p['surname']])<=1 else p['name'][0]+'.'+p['surname'] for p in players}

def get_ratings(db, day = None):
    res = db.execute('''
        SELECT rat_pla_autoid AS player, rat_rating AS rating, rat_deviation AS deviation, rat_date AS day, rat_official AS official
        FROM snk_ratings WHERE rat_day=%d
        '''%(today if day is None else day)).fetchall()
    res = {r['player']: {k: r[k] for k in r if k!='player'} for r in res}
    for p in get_names(db):
        if p not in res:
            res[p] = {'rating': 1500 + random.uniform(-0.1,0.1), 'deviation': 350, 'day': 0, 'official': 0}
    res[0] = {'rating': 0, 'deviation': 0, 'day': today, 'official': 0}
    return res

def get_availability():
    res = {}
    with open('availability.csv') as csvfile:
        for row in csv.reader(csvfile, delimiter=','):
            res[int(row[0])] = [0.5 if v == '' else int(v)/2 for v in row[1:]] #random.randint(0,2)/2
    res[0] = [1]*max([len(res[p]) for p in res])
    return res

def frame_prediction(db, pl1, pl2):
    if pl1 == 0:
        return 0
    elif pl2 == 0:
        return 1
    pi = 3.141592653589
    q = 0.0057564627325
    c = (350**2 - 50**2) / 720
    r = get_ratings(db)
    r1 = r[pl1]
    r2 = r[pl2]
    RD1 = min( r1['deviation']**2 + c * (today - r1['day']), 350**2 )
    RD2 = min( r2['deviation']**2 + c * (today - r2['day']), 350**2 )
    g = 1 / (1 + 3 * q**2 * (RD1 + RD2) / pi**2)**0.5
    return 1 / ( 1 + 10**( g * (r2['rating'] - r1['rating']) / 400 ) )

def match_prediction(p, n = 3):
    res = 0
    for k in range(n):
        res += nCr(n+k-1,k) * p**n * (1-p)**k
    return res
    
def match_distribution(p, n = 3):
    res = {}
    for k in range(n):
        res[n+k] = nCr(n+k-1,k) * (p**n * (1-p)**k + p**k * (1-p)**n)
    return res

def flexibility(av1, av2):
    return sum([a1*a2 for a1,a2 in zip(av1,av2)])

def compatibility(av1, av2):
    return max([a1*a2 for a1,a2 in zip(av1,av2)])
    
def flatten(x):
    return [z for y in x for z in y]

def distribution_map(r, reverse = True):
    res = [0]
    for g in range(r):
        nres = []
        for i in range(2**g):
            nres.append(res[i])
            if reverse:
                op = 2**(g+1) - res[i] - 1
            else:
                op = 2**g + i
            nres.append(op)
        res = nres
    return res

def distribute(x, dmap):
    return [x[dmap[i]] for i in range(len(x))]

def generate_trees(perm):
    ptree = {i+2**rounds: {perm[i]: 1} for i in range(2**rounds)}
    ctree = {}
    btree = {}
    ftree = {}

    for r in range(rounds-1,-1,-1):
        for i in range(2**r,2**(r+1)):
            i0, i1 = 2*i, 2*i+1
            
            ctree[i] = 0
            btree[i] = 1
            ftree[i] = 0
            for p0 in ptree[i0]:
                for p1 in ptree[i1]:
                    ctree[i] += ptree[i0][p0] * ptree[i1][p1] * comp[p0][p1]
                    ftree[i] += ptree[i0][p0] * ptree[i1][p1] * flex[p0][p1]
                    if comp[p0][p1] == 0:
                        btree[i] = 0
            
            ptree[i] = {}
            f = frames_to_win[r]
            for p0 in ptree[i0]:
                ptree[i][p0] = ptree[i0][p0] * sum([ptree[i1][p1] * prob[p0][p1][f] for p1 in ptree[i1]])
            for p1 in ptree[i1]:
                ptree[i][p1] = ptree[i1][p1] * sum([ptree[i0][p0] * prob[p1][p0][f] for p0 in ptree[i0]])
                
    return ptree, ctree, btree, ftree

def generate_opt_perm():
    max_comp = None
    max_b = 0
    max_flex = 0
    pres = 1000
    groups = [players[int(2**r):2**(r+1)] for r in range(-1,rounds)]
    g0 = groups[0]
    g1 = groups[1]
    for g2 in permutations(groups[2]):
        for g3 in permutations(groups[3]):
            success = False
            count = 0
            while count < 100 or (not success and count < 1000):
                if count > 0:
                    for r in range(4,rounds+1):
                        random.shuffle(groups[r])
                
                flat = flatten([g0,g1,g2,g3]+groups[4:]) + [0] * (2**rounds - players_number)
                perm = distribute(flat, dmap)
                ptree, ctree, btree, ftree = generate_trees(perm)
                
                c = round(pres * min(ctree.values())) / pres
                b = sum(btree.values())
                f = round( sum(ftree.values()) * min(ftree.values()) )
                
                if max_comp is None or (c, f) > (max_comp, max_flex):
                    print(c, f)
                    max_comp = c
                    max_b = b
                    max_flex = f
                    opt_perm = perm
                    
                if min([ctree[i] for i in range(2**(rounds-1),2**rounds)]) > 0:
                    success = True
                count += 1
    return opt_perm

def import_perm():
    with open('bracket.json') as jsonfile:
        perm = json.load(jsonfile)
    return perm
    
def export_perm(perm):
    with open('bracket.json', 'w') as jsonfile:
        json.dump(perm, jsonfile)


conn = sqlite3.connect('tuscany.snkcoresvr.sqlite')
db = conn.cursor()
db.row_factory = dict_factory

rat = get_ratings(db)

players = [p for p in sorted(rat, key = lambda p: -rat[p]['rating']) if p != 0 and rat[p]['day']>today-30][:20]
           
#players = [20042, 20002, 20049, 20022, 20008, 20012, 20004, 20050, 20003, 20048, 20009, 20014, 20046, 20039, 20010, 20016]
frames_to_win = [5, 4, 3, 2]

players = list(sorted(players, key = lambda p: -rat[p]['rating'] - 2000*rat[p]['official']))
players_number = len(players)
rounds = min([r for r in range(6) if players_number <= 2**r])
dmap = distribution_map(rounds, reverse = True)
players_0 = players + [0]
ran = {players_0[i]: i+1 for i in range(len(players_0))}
avail = get_availability()
frames_to_win += [frames_to_win[-1]] * (rounds - len(frames_to_win))

prob = {}
comp = {}
flex = {}
for p1 in players_0:
    prob[p1] = {}
    comp[p1] = {}
    flex[p1] = {}
    for p2 in players_0:
        prob[p1][p2] = {}
        for n in frames_to_win:
            prob[p1][p2][n] = match_prediction(frame_prediction(db, p1, p2), n)
        comp[p1][p2] = compatibility(avail[p1], avail[p2])
        flex[p1][p2] = flexibility(avail[p1], avail[p2])

#opt_perm = generate_opt_perm()
#export_perm(opt_perm)

opt_perm = import_perm()

opt_ptree, opt_ctree, opt_btree, opt_ftree = generate_trees(opt_perm)

fexp = {p: 0 for p in players}
for r in range(rounds):
    for i in range(2**r,2**(r+1)):
        i0, i1 = 2*i, 2*i+1
        for p0 in opt_ptree[i0]:
            for p1 in opt_ptree[i1]:
                if 0 not in [p0,p1]:
                    dist = match_distribution(frame_prediction(db, p0, p1), frames_to_win[r])
                    exp = sum([opt_ptree[i0][p0] * opt_ptree[i1][p1] * dist[l] * l for l in dist])
                    fexp[p0] += exp
                    fexp[p1] += exp

name = get_names(db)
print()
for p in players:
    if p != 0:
        coef = '%6.2f'%(1/max(1/500,opt_ptree[1][p]))
        print('%2d %-13s %5.2f%%  (%.1f)'%(ran[p], name.get(p,''), 100*opt_ptree[1][p], fexp[p]))

n = 1
print()
for p in opt_perm:
    #print('%d %s'%(ran[p], name[p]))
    if p != 0:
        print('%2d %-13s %5.2f%%'%(ran[p], name.get(p,''), 100*opt_ptree[1][p]))
    else:
        print('--')
    n = 1-n
    if n: print()

for i in range(1, 2**(rounds+1)):
    stage = max([g for g in range(rounds+1) if i%(2**g)==0])
    start = (i-2**stage) // 2
    end = start + 2**stage
    p = sorted(opt_perm[start : end], key = lambda p: ran[p])[0]
    
    if stage!=0 or 0 not in opt_perm[start//2*2 : start//2*2 + 2]:
        print('%s%2d %-13s'%(' '*((20-stage)*stage), ran[p], name.get(p,'')))

print()
frames = sum([fexp[p] for p in fexp])/2
avg_time = 50/60
per_h = 10
cost = frames*avg_time*per_h
print('%.0f'%frames, '%.2f'%(frames/players_number), round(cost), round(cost/players_number))

conn.close()
