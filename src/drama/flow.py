"""Attach Google Flow shot data (src/drama/flow_en.txt) to the drama version of each clip in rows9.json.

The page (body3.html, "Prompt สำหรับ Flow" view) composes the final still-image and video prompts from:
  drama.fl = {lab: {id: Thai role label}, x: {key: [english role, look]}, sp: {Thai speaker: [id, thought]},
              s: [{no, h, loc, b: [[cam, loc, text], ...], sfx, g} | {no, h, e: Thai note}]}
h is a hash of the scene's Thai visual text, so the page can tell when a scene was edited after the shot text was written.

Run:  python3 src/drama/flow.py            (gen.py also calls attach() after rebuilding the drama)
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen import labels_for, LABELS

ID = {'พี่นุ่น': 'c', 'พี่ต้น': 'h', 'โอ๊ต': 'f', 'มายด์': 's', 'พี่อร': 'a', 'เบล': 'n', 'พี่เอก': 'r', 'ก้อง': 'j', 'ภูมิ': 'p'}
MAIN = set(ID.values())
LOCS = set('office glass coffee lift lobby exec board wh site sitebox plant lab yard car rest home client gov desk hotel cafe street breakroom carpark expo assoc itroom'.split())
CAMS = set('wide full med two cu ecu ots ins trk high pull pov'.split())
PH = re.compile(r'\{(\w+)\}')


def fnv(s):
    h = 0x811c9dc5
    b = s.encode('utf-16-le')
    for i in range(0, len(b), 2):
        h ^= b[i] | (b[i + 1] << 8)
        h = (h * 0x01000193) & 0xffffffff
    return format(h, '08x')


def parse_x(line):
    m = re.match(r'x@?\s+(\w+)\s*(?:\[([^\]]*)\])?\s*=\s*(.+)$', line)
    if not m: raise ValueError('bad extra: ' + line)
    key, al, desc = m.group(1), m.group(2) or '', m.group(3).strip()
    name, look = desc.split(':', 1)
    return key, dict(n=name.strip(), d=look.strip(), al=[a.strip() for a in al.split('|') if a.strip()])


def parse(path=os.path.join(HERE, 'flow_en.txt')):
    G, E, cur = {}, {}, None
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        if not line or (line.startswith('#') and not line.startswith('## ')): continue
        if line.startswith('x@'):
            k, v = parse_x(line); G[k] = v; continue
        if line.startswith('## '):
            cur = E.setdefault(line[3:].strip(), dict(x={}, s={})); continue
        if line.startswith('x '):
            k, v = parse_x(line); cur['x'][k] = v; continue
        f = [t.strip() for t in line.split(' | ')]
        no = int(f[0])
        if f[1] == 'EDIT':
            cur['s'][no] = dict(e=f[2]); continue
        loc, cam, act = f[1], f[2], f[3]
        rest = f[4:]
        g = next((t[2:].strip() for t in rest if t.startswith('g:')), '')
        ns = next((int(t[2:]) for t in rest if re.match(r'n:\d+$', t)), 0)
        sfx = next((t for t in rest if t and not t.startswith('g:') and not re.match(r'n:\d+$', t)), '')
        beats = []
        for k, b in enumerate(act.split(' // ')):
            bc, bl = cam, loc
            m = re.match(r'\[(\w+)(?:@([^\]]+))?\]\s*(.*)$', b)
            if m: bc, bl, b = m.group(1), m.group(2) or loc, m.group(3)
            beats.append([bc, bl, b.strip()])
        cur['s'][no] = dict(b=beats, sfx=sfx, g=g, n=ns)
    return G, E


def attach(D, path=None, report=True):
    G, E = parse(path) if path else parse()
    probs, n_sc, n_ok = [], 0, 0
    for d in D:
        dr = d.get('drama')
        if not dr: continue
        dr.pop('fl', None)
        scenes = [s for p in dr['sb']['parts'] for s in p['scenes']]
        n_sc += len(scenes)
        ep = E.get(d['date'])
        if not ep: continue
        lab_all = labels_for((d['m'], d['w']), d['date'])
        lab_id = {ID[k]: v for k, v in lab_all.items()}
        id_of = {v: ID[k] for k, v in lab_all.items()}
        id_of.update({v: ID[k] for k, v in LABELS.get((d['m'], d['w']), {}).items()})   # an episode's own labels win over defaults
        X = dict(ep['x'])
        used = set()
        out = []
        for s in scenes:
            e = ep['s'].get(s['no'])
            if not e:
                probs.append(f"{d['date']} scene {s['no']}: missing"); continue
            o = dict(no=s['no'], h=fnv(s['visual']))
            if 'e' in e: o['e'] = e['e']
            else:
                for cam, loc, t in e['b']:
                    if cam not in CAMS: probs.append(f"{d['date']} {s['no']}: cam {cam}")
                    if loc not in LOCS and not loc.startswith('~'): probs.append(f"{d['date']} {s['no']}: loc {loc}")
                    for k in PH.findall(t):
                        if k in MAIN: used.add(k)
                        elif k in X or k in G: used.add(k); X.setdefault(k, G.get(k))
                        else: probs.append(f"{d['date']} {s['no']}: unknown {{{k}}}")
                o['b'] = e['b']
                if e['sfx']: o['sfx'] = e['sfx']
                if e['g']: o['g'] = e['g']
                if e['n']: o['n'] = e['n']
            out.append(o); n_ok += 1
        extra = [no for no in ep['s'] if no not in {s['no'] for s in scenes}]
        if extra: probs.append(f"{d['date']}: scenes not in storyboard {extra}")
        # speakers -> ids
        sp = {}
        for s in scenes:
            for w, _ in s['audio']:
                if 'ผู้บรรยาย' in w or w in sp: continue
                base, th = (w[:-len(' (คิดในใจ)')], 1) if w.endswith('(คิดในใจ)') else (w, 0)
                k = id_of.get(base)
                if not k:
                    for xk, xv in list(X.items()) + list(G.items()):
                        if xv and (base in xv['al']): k = xk; X.setdefault(xk, xv); break
                if k: sp[w] = [k, th]; used.add(k)
        xs = {k: [X[k]['n'], X[k]['d']] for k in sorted(used) if k not in MAIN and X.get(k)}
        dr['fl'] = dict(lab={k: lab_id[k] for k in sorted(used & MAIN)}, x=xs, sp=sp, s=out)
    if report:
        print(f'flow: {n_ok}/{n_sc} scenes have shot data')
        for p in probs: print('  !', p)
    return probs


if __name__ == '__main__':
    path = os.path.join(HERE, '..', 'rows9.json')
    D = json.load(open(path))
    attach(D)
    json.dump(D, open(path, 'w'), ensure_ascii=False, indent=1)
