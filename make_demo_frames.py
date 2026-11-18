"""產生 DEMO 用的 20 球真實紀錄（10/31 成大 vs 義守，3 局下 1 出局滿壘起）。

用法（在 live 資料夾執行）：
  python -I make_demo_frames.py index.html ../cloud_fix/fixed/2026-10-31_左右打投/2026-10-31_成大_vs_義守.json demo_frames.json

- 事件內容取自已內嵌的歷史比賽（game_okcbzm2nnco），時間取自原始雲端紀錄的 ts（只讀，不會修改）。
- 每個 frame 的 t＝相對 DEMO 起點（admin 的 demoStart）的秒數；frame 0 是開場（還沒投第一球）。
- build_live.py 若看到 demo_frames.json，會用它取代內嵌 DEMO 的 frames。
"""
import json, re, sys

page, raw_path, out_path = sys.argv[1:4]
GAME = 'game_okcbzm2nnco'
START = 165        # 內嵌歷史事件的索引：3 局下 DEFAULT6 打擊（1 出局滿壘）
N = 20             # 幾球
LEAD = 35.0        # 第一球（雙殺打）結果約在起點後 35 秒出現（11/19 使用者實看校正：原 18 秒早了 17 秒）

s = open(page, encoding='utf-8').read()
dm = json.loads(re.search(r'<script id="demo-data" type="application/json">([\s\S]*?)</script>', s).group(1))
hist = [g for g in dm['hist'] if g['id'] == GAME][0]
ev = hist['events']
raw = json.load(open(raw_path, encoding='utf-8'))
ts = {e['id']: e['ts'] for e in raw['events']}

base_ids = [e['id'] for e in dm['base']['events']]
assert base_ids == [e['id'] for e in ev[:START]], 'DEMO base 與歷史紀錄前段不一致'

# 實際打序（紀錄系統存的 lineup 與實際上場順序不同；DEMO 依實際 PA 順序顯示）
teams = json.loads(json.dumps(dm['base']['teams']))
away = {p['name']: p for p in teams['away']['lineup'] + teams['away'].get('bench', [])}
order = [('葉詠翔', '2B'), ('王學睿', '3B'), ('張冠瑀', 'SS'), ('林建曄', 'DH'), ('黃昱綸', '1B'),
         ('陳聲皓', 'CF'), ('葉宸銨', 'LF'), ('謝竺庭', 'RF'), ('張永宸', 'C')]
lineup = []
for n, pos in order:
    p = dict(away[n]); p['pos'] = pos; lineup.append(p)
bench_names = {n for n, _ in order}
teams['away']['lineup'] = lineup
teams['away']['bench'] = [p for p in teams['away'].get('bench', []) if p['name'] not in bench_names]

def idx_of(team, name):
    for i, p in enumerate(teams[team]['lineup']):
        if p['name'] == name:
            return i
    return -1

def next_batter(team, k):
    for e in ev[k:]:
        if e.get('battingTeam') == team and e.get('batterName'):
            return idx_of(team, e['batterName'])
    return -1

PITCH = {'ball': '壞球', 'strike_look': '好球（未揮棒）', 'strike_swing': '揮棒落空', 'foul': '界外球', 'hbp': '觸身球'}
OUT = {'GIDP': '雙殺打', '1B': '一壘安打', '2B': '二壘安打', '3B': '三壘安打', 'HR': '全壘打', 'SF': '高飛犧牲打，跑者回本壘得分',
       '一般出局': '出局', 'BB': '四壞球保送', 'HBP': '觸身球保送'}

score = {'home': [1, 0, 1], 'away': [10, 2, 4]}   # 3 局下開始前的比分（同原本 DEMO）

def state_before(k):
    e = ev[k]
    return {'inning': e['inningBefore'], 'half': e['halfBefore'], 'outs': e['outsBefore'],
            'balls': e.get('ballsBefore') or 0, 'strikes': e.get('strikesBefore') or 0,
            'bases': e['basesBefore'],
            'battingIndex': {'home': next_batter('home', k), 'away': next_batter('away', k)},
            'score': json.loads(json.dumps(score))}

def cap(e):
    who = e.get('batterName', '')
    half = f"{e['inningBefore']}局{'上' if e['halfBefore'] == 'top' else '下'}"
    if e.get('finalOutcome'):
        txt = OUT.get(e['finalOutcome'], e['finalOutcome'])
        if e['finalOutcome'] == '一般出局' and e.get('trajectory'):
            txt = e['trajectory'] + '出局'
    else:
        txt = PITCH.get(e.get('pitchResult'), e.get('pitchResult') or '')
    return f"{half}・{who}：{txt}"

t0 = ts[ev[START]['id']]
# 內嵌歷史只留投手更換；把原始紀錄裡開場前的其他換人（例：守備更換 LF 葉宸銨）補回來，打序由觀賽頁依紀錄推算
raw_ev = raw['events']; start_raw = [i for i, e in enumerate(raw_ev) if e['id'] == ev[START]['id']][0]
extra = [{k: e.get(k) for k in ('id', 'type', 'kind', 'inPlayerName', 'outPlayerName', 'position', 'inningBefore', 'halfBefore', 'battingTeam', 'fieldingTeam', 'summary') if e.get(k) is not None}
         for e in raw_ev[:start_raw] if e['type'] == 'sub' and e.get('kind') != '投手更換']
frames = [{'t': 0, 'cap': '真實比賽重播：10/31 成大 vs 義守，3局下 1出局滿壘，王昱峻對 DEFAULT6。影片和紀錄會一起走。',
           'events': extra, 'state': state_before(START)}]
k = START; used = 0
while used < N:
    e = ev[k]
    if e['type'] in ('pitch', 'battedball'):
        used += 1
    # 比分：跨半局時補 0，得分加進當局
    side = 'away' if e['halfBefore'] == 'top' else 'home'
    while len(score[side]) < e['inningBefore']:
        score[side].append(0)
    if e.get('runsThisPlay'):
        score[side][e['inningBefore'] - 1] += e['runsThisPlay']
    nxt = state_before(k + 1)
    nside = 'away' if nxt['half'] == 'top' else 'home'
    while len(nxt['score'][nside]) < nxt['inning']:
        nxt['score'][nside].append(0)
    frames.append({'t': round(LEAD + (ts[e['id']] - t0) / 1000, 1), 'cap': cap(e), 'events': [e], 'state': nxt})
    k += 1

json.dump(frames, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
print('frames', len(frames), 'span', frames[-1]['t'], 's')
