import sqlite3
import time
import random

today = int(time.time()/86400)

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

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_names(db):
    pl = db.execute('SELECT pla_autoid AS id, snk_player.pla_name AS name, snk_player.pla_surname AS surname FROM snk_player').fetchall()
    return {p['id']: p['surname'] if sum([1 for t in pl if t['surname']==p['surname']])<=1 else p['name'][0]+'.'+p['surname'] for p in pl}

def get_ratings(db, day = None, average = False):
    res = db.execute('''
        SELECT rat_pla_autoid AS player, rat_rating AS rating, rat_deviation AS deviation, rat_date AS day, rat_official AS official
        FROM snk_ratings
        WHERE rat_day=%d
        '''%(today if day is None else day)).fetchall()
    res = { r['player']: {k: r[k] for k in r if k!='player'} for r in res }
    for p in get_names(db):
        if p not in res:
            res[p] = {'rating': 1500 + random.uniform(-0.1,0.1), 'deviation': 350, 'day': 0, 'official': 0}
    res[0] = {'rating': 0, 'deviation': 0, 'day': today, 'official': 0, }
    return res

def frame_prediction(db, pl1, pl2):
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

def match_prediction(db, pl1, pl2, n = 3):
    p = frame_prediction(db, pl1, pl2)
    q = 1 - p
    res = 0
    for k in range(n):
        res += nCr(n+k-1,k) * p**n * q**k
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
            nres.append( res[i] )
            if reverse:
                op = 2**(g+1) - res[i] - 1
            else:
                op = 2**g + i
            nres.append(op)
        res = nres
    return res

def distribute(x):
    return [x[dmap[i]] for i in range(len(x))]


conn = sqlite3.connect('tuscany.snkcoresvr.sqlite')
db = conn.cursor()
db.row_factory = dict_factory

rat = get_ratings(db, day = None)
players = [p for p in sorted(rat, key = lambda p: -rat[p]['rating']) if rat[p]['day']>today-20][:21]

r = min([r for r in range(6) if len(players) <= 2**r])
dmap = distribution_map(r, reverse = True)

if len(players) < 2**r:
    players += [0] * (2**r - len(players))

#players = [20042, 20002, 20049, 20022, 20008, 20012, 20004, 20050, 20003, 20048, 20009, 20014, 20046, 20039, 20010, 20016]
players = list(sorted(players, key = lambda p: -rat[p]['rating'] - 2000*rat[p]['official']))

avail = { p: [1]*7 for p in players }

for p in avail:
    if p != 0:
        avail[p] = [1,1,random.randint(0,1),1,0,0,0]
        random.shuffle(avail[p])
avail[20009] = [0,0,0,0,1,1,0] #Minuto
avail[20012] = [0,0,0,0,1,1,1] #F. Pasqualetti
avail[20014] = [0,0,0,1,0,0,1] #Cordova
avail[20046] = [1,1,1,1,1,0,0] #Di Marco
avail[20002] = [0,1,0,1,0,1,1] #Calzerano
avail[20003] = [1,1,1,1,1,0,1] #Picchi
avail[20033] = [0,0,0,1,1,0,0] #Sichi
avail[20044] = [1,1,1,1,1,1,1] #Besenval
avail[20045] = [1,1,1,1,1,1,1] #Solomko

ran = {players[i]: i+1 for i in range(len(players))}
       
prob = {}
comp = {}
flex = {}
w = 0.2
for p1 in players:
    prob[p1] = {}
    comp[p1] = {}
    flex[p1] = {}
    for p2 in players:
        prob[p1][p2] = w * 0.5 + (1-w) * match_prediction(db, p1, p2, 2)
        comp[p1][p2] = compatibility(avail[p1], avail[p2])
        flex[p1][p2] = flexibility(avail[p1], avail[p2])
        #if comp[p1][p2]==0: print(p1, p2)

groups = [[players[0]]]
for g in range(r):
    groups.append( players[2**g:2**(g+1)] )
zeros = len([p for p in groups[-1] if p == 0])
groups[-1] = [p for p in groups[-1] if p != 0]
groups.append([0] * zeros)

max_comp = None
max_b = 0
max_flex = 0
pres = 1000
g0 = groups[0]
g1 = groups[1]
for g2 in permutations(groups[2]):
    for g3 in permutations(groups[3]):
        success = False
        count = 0
        while count < 100 or (not success and count < 1000):
            if count > 0:
                for g in range(4,r+1):
                    random.shuffle(groups[g])
            
            flat = flatten([g0,g1,g2,g3]+groups[4:r]) + [0] * 2**(r-1)
            nqual = len(groups[r])
            j = 0
            for i in range(2**(r-1)):
                if ran[flat[i]] > 2**(r-1) - nqual:
                    flat[2**r-i-1] = groups[r][j]
                    j += 1
            
            perm = distribute(flat)
            
            ptree = {i+2**r: {perm[i]: 1} for i in range(2**r)}
            ctree = {}
            btree = {}
            ftree = {}
            for i in range(2**r-1,0,-1):
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
                for p0 in ptree[i0]:
                    ptree[i][p0] = ptree[i0][p0] * sum([ptree[i1][p1] * prob[p0][p1] for p1 in ptree[i1]])
                for p1 in ptree[i1]:
                    ptree[i][p1] = ptree[i1][p1] * sum([ptree[i0][p0] * prob[p1][p0] for p0 in ptree[i0]])
            
            c = round(pres * min(ctree.values())) / pres
            b = sum(btree.values())
            f = round( sum(ftree.values()) * min(ftree.values()) )
            
            if max_comp is None or (c, f) > (max_comp, max_flex):
                print(c, f)
                max_comp = c
                max_b = b
                max_flex = f
                opt_perm = perm
                opt_ptree = ptree
                opt_ctree = ctree
                opt_btree = btree
                opt_ftree = ftree
            if min([ctree[i] for i in range(2**(r-1),2**r)]) > 0:
                success = True
            count += 1

name = get_names(db)
print()
for p in players:
    if p != 0:
        print('%2d %-13s'%(ran[p], name.get(p,'')), ' '.join([str(a) for a in avail[p]]), ' %6.2f'%(1/max(1/500,opt_ptree[1][p])))

n = 1
print()
for p in opt_perm:
    #print('%d %s'%(ran[p], name[p]))
    if p != 0:
        print('%2d %-13s %5.2f%%'%(ran[p], name.get(p,''), 100*opt_ptree[1][p]))
    else:
        print('--')
    n = 1-n
    if n: print('\t\t\t')
    
conn.close()