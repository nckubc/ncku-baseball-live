"""把「及時資料處理」內嵌的 DEMO 資料複製進線上觀賽頁。
用法：python -I build_live.py ../realtime/及時資料處理/index.html index.src.html index.html
若同資料夾有 demo_frames.json（由 make_demo_frames.py 產生），會用它取代 DEMO 的 frames（真實 20 球）。"""
import sys, os, json
rt, src, out = sys.argv[1:4]
r = open(rt, encoding='utf-8').read()
a = r.index('<script id="demo-data" type="application/json">') + len('<script id="demo-data" type="application/json">')
b = r.index('</script>', a)
demo = r[a:b]
fr = os.path.join(os.path.dirname(os.path.abspath(src)), 'demo_frames.json')
if os.path.exists(fr):
    d = json.loads(demo)
    d['frames'] = json.load(open(fr, encoding='utf-8'))
    demo = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    print('frames from demo_frames.json:', len(d['frames']))
    en = os.path.join(os.path.dirname(os.path.abspath(src)), 'demo_enrich.json')
    if os.path.exists(en):
        E = json.load(open(en, encoding='utf-8')); n = 0
        evs = list(d['base']['events']) + [e for f in d['frames'] for e in f.get('events', [])] + [e for g in d.get('hist', []) for e in g.get('events', [])]
        for e in evs:
            for k, v in E.get(e.get('id'), {}).items():
                if e.get(k) is None: e[k] = v; n += 1
        demo = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        print('enriched fields:', n)
s = open(src, encoding='utf-8').read()
assert s.count('__DEMO_DATA__') == 1
import time
s = s.replace("var BUILD='__BUILD__'", "var BUILD='" + time.strftime('%Y%m%d%H%M%S') + "'")
open(out, 'w', encoding='utf-8', newline='').write(s.replace('__DEMO_DATA__', demo))
print('demo bytes', len(demo))
