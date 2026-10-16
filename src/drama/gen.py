"""Build the drama ("ชั้น 12") version of every clip into rows9.json as d['drama'].
Run: python3 drama/gen.py   (idempotent; regenerates from d['sb'] + mappings below)"""
import json, re, copy, sys, os
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(S, 'drama'))
from samples import SAMPLES
from realcase2 import REAL, VIS, GAGS
from dur import syl

FEMALE = {'เบล', 'มายด์', 'พี่อร', 'พี่นุ่น'}
MALE = {'พี่ต้น', 'โอ๊ต', 'พี่เอก', 'ก้อง', 'ภูมิ', 'คุณวิชัย'}
CAST = FEMALE | MALE
N = 'ผู้บรรยาย'

# role label (as used in the case version) -> cast member, per clip (m, w)
MAP = {
 ('ธ.ค. 2569', 1): {'Engineer': 'เบล'},
 ('ธ.ค. 2569', 3): {'เจ้าหน้าที่สรรหา': 'เบล', 'ผู้จัดการฝ่ายบุคคล': 'พี่เอก'},
 ('ม.ค. 2570', 1): {'Marketing': 'มายด์'},
 ('ม.ค. 2570', 3): {'เจ้าหน้าที่บริการลูกค้า': 'โอ๊ต', 'หัวหน้าฝ่ายบริการ': 'พี่ต้น'},
 ('ก.พ. 2570', 1): {'Sales Manager': 'มายด์'},
 ('ก.พ. 2570', 5): {'พนักงานบัญชี': 'พี่อร', 'เพื่อนร่วมงาน': 'โอ๊ต'},
 ('มี.ค. 2570', 1): {'ผู้จัดการโครงการก่อสร้าง': 'พี่ต้น'},
 ('มี.ค. 2570', 3): {'ช่างเทคนิคไซต์': 'โอ๊ต', 'หัวหน้างานไซต์': 'พี่ต้น'},
 ('เม.ย. 2570', 1): {'พนักงานขาย': 'มายด์'},
 ('เม.ย. 2570', 3): {'Sales Engineer คนใหม่': 'ก้อง', 'Sales Manager': 'มายด์'},
 ('พ.ค. 2570', 1): {'ผู้บริหาร': 'พี่ต้น', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('พ.ค. 2570', 3): {'เจ้าหน้าที่บัญชี': 'พี่อร', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('มิ.ย. 2570', 1): {'Site Manager': 'พี่ต้น'},
 ('มิ.ย. 2570', 3): {'หัวหน้างานไซต์': 'โอ๊ต'},
 ('ก.ค. 2570', 1): {'Business Manager': 'โอ๊ต'},
 ('ก.ค. 2570', 3): {'วิศวกรโครงการ': 'โอ๊ต', 'ผู้จัดการโครงการ': 'พี่ต้น'},
 ('ส.ค. 2570', 1): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร'},
 ('ส.ค. 2570', 3): {'ช่างติดตั้งโซลาร์': 'โอ๊ต', 'หัวหน้าทีมติดตั้ง': 'พี่ต้น'},
 ('ก.ย. 2570', 1): {'Project Manager': 'พี่ต้น'},
 ('ก.ย. 2570', 3): {'วิศวกรพี่เลี้ยง': 'โอ๊ต'},
 ('ต.ค. 2570', 1): {'Site Manager': 'พี่ต้น'},
 ('ต.ค. 2570', 3): {'วิศวกรโครงการ': 'มายด์'},
 ('พ.ย. 2570', 1): {'ผู้จัดการจัดซื้อ': 'พี่อร'},
 ('พ.ย. 2570', 3): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร', 'ผู้จัดการฝ่ายจัดซื้อ': 'พี่ต้น'},
 ('ธ.ค. 2570', 1): {'พนักงานบัญชี': 'พี่อร', 'เพื่อนร่วมงาน': 'เบล'},
 ('ธ.ค. 2570', 3): {'วิศวกรออกแบบ': 'เบล', 'หัวหน้าแผนกวิศวกรรม': 'พี่ต้น'},
 ('ม.ค. 2571', 1): {'Business Development': 'มายด์'},
 ('ม.ค. 2571', 3): {'ช่างเทคนิคโซลาร์': 'โอ๊ต', 'หัวหน้าทีมติดตั้ง': 'พี่ต้น'},
 ('ก.พ. 2571', 1): {'Sales': 'พี่ต้น'},
 ('ก.พ. 2571', 3): {'Sales Engineer': 'มายด์', 'วิศวกรออกแบบ': 'เบล'},
 ('มี.ค. 2571', 1): {'Sales Manager': 'มายด์'},
 ('มี.ค. 2571', 3): {'Sales Manager': 'พี่ต้น'},
 ('เม.ย. 2571', 1): {'ทีมงาน': 'พี่ต้น'},
 ('เม.ย. 2571', 3): {'หัวหน้าไซต์งาน': 'พี่ต้น', 'ธุรการไซต์งาน': 'เบล', 'เจ้าหน้าที่บัญชี': 'พี่อร'},
 ('พ.ค. 2571', 1): {'IT': 'เบล'},
 ('พ.ค. 2571', 3): {'เจ้าหน้าที่ HR': 'พี่เอก', 'เจ้าหน้าที่ IT': 'เบล'},
 ('มิ.ย. 2571', 1): {'Project Manager': 'พี่ต้น', 'Project Engineer': 'โอ๊ต'},
 ('มิ.ย. 2571', 3): {'เจ้าหน้าที่วางแผนการผลิต': 'พี่อร'},
 ('ก.ค. 2571', 1): {'พนักงาน A': 'โอ๊ต', 'พนักงาน B': 'มายด์'},
 ('ก.ค. 2571', 3): {'วิศวกรขาย': 'มายด์'},
 ('ส.ค. 2571', 1): {'วิศวกรอาวุโส': 'โอ๊ต', 'HR': 'พี่เอก'},
 ('ส.ค. 2571', 3): {'เจ้าหน้าที่ความปลอดภัย': 'โอ๊ต'},
 ('ก.ย. 2571', 1): {'Engineer บริษัท': 'เบล'},
 ('ก.ย. 2571', 3): {'วิศวกรระบบอัตโนมัติ': 'ก้อง', 'หัวหน้าวิศวกรรม': 'พี่ต้น'},
 ('ต.ค. 2571', 1): {'เจ้าหน้าที่จัดซื้อ': 'ภูมิ', 'ผู้จัดการ': 'พี่อร'},
 ('ต.ค. 2571', 3): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร', 'วิศวกรฝ่ายผลิต': 'โอ๊ต'},
 ('พ.ย. 2571', 1): {'Sales Manager': 'มายด์', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('พ.ย. 2571', 3): {'ผู้จัดการไซต์โซลาร์ฟาร์ม': 'โอ๊ต'},
 ('ธ.ค. 2571', 1): {'ผู้จัดการโครงการ': 'พี่ต้น', 'วิศวกรโครงการ': 'โอ๊ต'},
 ('ธ.ค. 2571', 3): {'วิศวกรออกแบบ': 'เบล', 'ผู้จัดการโครงการ': 'มายด์'},
 ('ม.ค. 2572', 1): {'หัวหน้าทีม': 'พี่ต้น', 'พนักงาน A': 'โอ๊ต', 'พนักงาน B': 'มายด์'},
 ('ม.ค. 2572', 3): {'หัวหน้าหน่วยซ่อมบำรุง': 'พี่ต้น', 'เพื่อนร่วมงานอาวุโส': 'พี่อร'},
 ('ก.พ. 2572', 1): {'วิศวกรโครงการ': 'โอ๊ต'},
 ('ก.พ. 2572', 3): {'พนักงานฝ่ายผลิต': 'ภูมิ', 'หัวหน้าไลน์ผลิต': 'พี่ต้น'},
 ('มี.ค. 2572', 1): {'พนักงาน': 'พี่อร'},
 ('มี.ค. 2572', 3): {'Project Coordinator': 'เบล', 'วิศวกรโครงการ': 'โอ๊ต'},
 ('เม.ย. 2572', 1): {'Project Manager': 'พี่ต้น'},
 ('เม.ย. 2572', 3): {'วิศวกรสนาม': 'ภูมิ', 'หัวหน้าคนงาน': 'โอ๊ต', 'ผู้จัดการโครงการ': 'พี่ต้น'},
 ('พ.ค. 2572', 1): {'Auditor': 'พี่อร'},
 ('พ.ค. 2572', 3): {'เจ้าหน้าที่จัดซื้อ': 'ภูมิ', 'ผู้จัดการจัดซื้อ': 'พี่อร'},
 ('มิ.ย. 2572', 1): {'กรรมการสอบสวน': 'พี่เอก'},
 ('มิ.ย. 2572', 3): {'เจ้าหน้าที่ HR': 'ภูมิ', 'หัวหน้าแผนก HR': 'พี่เอก'},
 ('ก.ค. 2572', 1): {'Marketing': 'มายด์'},
 ('ก.ค. 2572', 3): {'เจ้าหน้าที่ธุรการโรงงาน': 'เบล', 'ผู้จัดการโรงงาน': 'พี่ต้น'},
 ('ส.ค. 2572', 1): {'เจ้าหน้าที่การเงิน': 'พี่อร'},
 ('ส.ค. 2572', 3): {'เจ้าหน้าที่วิเคราะห์ธุรกิจ': 'ภูมิ', 'หัวหน้าทีม': 'เบล'},
 ('ก.ย. 2572', 1): {'Project Director': 'พี่ต้น', 'Procurement': 'พี่อร', 'Sales': 'มายด์', 'Marketing': 'เบล', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('ก.ย. 2572', 3): {'วิศวกรจบใหม่': 'ภูมิ', 'วิศวกรอาวุโส': 'เบล'},
}
# year-arc beats shown in the closing scene's picture (no extra voice, so length stays the same)
ARC = {
 ('ก.พ. 2570', 5): 'ฉากหลัง: พี่อรวางแฟ้มลง ยิ้มโล่งใจ เพื่อนร่วมทีมชั้น 12 ส่งกาแฟให้',
 ('ก.ย. 2570', 3): 'ฉากหลัง: เบลเปิด Email "ผ่านทดลองงาน" แล้วแปะโน้ต 3 คำถามที่จอของตัวเอง',
 ('ต.ค. 2570', 1): 'ฉากหลัง: ป้ายชื่อบนโต๊ะพี่ต้นเปลี่ยนเป็น "ผู้จัดการฝ่ายปฏิบัติการ" กระดานทีมเขียนว่า "ดีลใหญ่ เริ่มแล้ว"',
 ('ส.ค. 2571', 3): 'ฉากหลัง: โอ๊ตกลับเข้าห้องประชุมโครงการใหญ่ เก้าอี้ที่เคยว่างมีคนนั่งแล้ว',
 ('ก.ย. 2571', 3): 'ฉากหลัง: กระดานทีมเขียนว่า "ส่งมอบดีลใหญ่ ✓" ทีมชั้น 12 ปรบมือ',
 ('ต.ค. 2571', 1): 'ฉากหลัง: ภูมิ น้องใหม่ เดินตามเบลไปที่โต๊ะ เบลยื่นโน้ต 3 คำถามให้',
 ('ม.ค. 2572', 1): 'ฉากหลัง: ทีมชั้น 12 กลับมานั่งทำงานด้วยกันตามปกติ ไม่มีใครถามหาชื่อผู้แจ้ง',
 ('ส.ค. 2572', 3): 'ฉากหลัง: ภูมิแปะโน้ต 3 คำถามที่จอของตัวเอง เบลยิ้ม',
 ('ก.ย. 2572', 3): 'ฉากหลัง: กล้องเลื่อนผ่านทุกโต๊ะที่มีโน้ตคำถามก่อนตัดสินใจแปะอยู่ จบที่แก้วพี่ต้นที่สลักใหม่ว่า "งานต้องเดิน...อย่างถูกต้อง"',
}
# industry words -> neutral company words (generic setting)
GENERIC = [
 ('ไซต์สถานีไฟฟ้า', 'ไซต์งาน'), ('สถานีไฟฟ้าแรงสูง', 'พื้นที่ซ่อมบำรุงระบบ'), ('สถานีไฟฟ้า', 'ไซต์งาน'), ('ไซต์โซลาร์ฟาร์ม', 'ไซต์งาน'), ('โซลาร์ฟาร์ม', 'ไซต์ลูกค้า'),
 ('ติดตั้งโซลาร์', 'ติดตั้งระบบ'), ('งานติดโซลาร์', 'งานติดตั้งระบบ'), ('Drawing', 'แบบ'), ('ติดโซลาร์', 'ติดตั้งระบบ'), ('แผงโซลาร์', 'อุปกรณ์'),
 ('น้ำมันหม้อแปลง', 'น้ำมันเครื่องจักร'), ('หม้อแปลง', 'เครื่องจักร'), ('ตู้ไฟฟ้า', 'ตู้ควบคุม'),
 ('เวลาดับไฟ', 'เวลาหยุดระบบ'), ('ดับไฟ', 'หยุดระบบ'),
]
def generic(t):
    for a, b in GENERIC: t = t.replace(a, b)
    return t

def sub_roles(text, mp):
    for role in sorted(mp, key=len, reverse=True):
        name = mp[role]
        text = re.sub(re.escape(role) + r'(?:\s?(?:หญิง|ชาย|หนุ่ม|สาว)|(?:หญิง|ชาย|หนุ่ม|สาว|คนหนึ่ง|คนนี้|ของเรา))*', name, text)
    return text

def particles(line, who):
    if who in MALE:
        line = re.sub(r'นะคะ|นะค่ะ', 'นะครับ', line)
        line = line.replace('ค่ะ', 'ครับ').replace('ดิฉัน', 'ผม')
        line = re.sub(r'คะ(?![ก-๙])', 'ครับ', line)
        line = line.replace('หนู', 'ผม')
    elif who in FEMALE:
        line = line.replace('นะครับ', 'นะคะ')
        line = re.sub(r'(พี่|หัวหน้า|คุณ)ครับ', r'\1คะ', line)
        line = re.sub(r'(ไหม|มั้ย|หรือ|เหรอ|อะไร|ยังไง|อย่างไร|ไหน|เท่าไร|กี่\S*|ใคร)ครับ', r'\1คะ', line)
        line = line.replace('ครับ?', 'คะ?').replace('ครับ”', 'ค่ะ”').replace('ครับ ', 'ค่ะ ').replace('ครับ', 'ค่ะ')
        line = line.replace('ผม', 'หนู' if who == 'เบล' else 'เรา')
    return line

def tsec(t):
    a, b = t.split(':'); return int(a) * 60 + int(b)

def build(d):
    key = (d['m'], d['w'])
    if key in SAMPLES:
        dr = copy.deepcopy(SAMPLES[key]); dr['sb']['audience'] = d['sb'].get('audience'); return dr
    mp = MAP.get(key, {})
    sb = copy.deepcopy(d['sb'])
    cast = []
    for role, name in mp.items():
        if name not in cast: cast.append(name)
    lead = cast[0] if cast else 'ทีมชั้น 12'
    parts = []
    for pi, p in enumerate(sb['parts']):
        scenes = []
        for s in p['scenes']:
            s['visual'] = generic(sub_roles(s['visual'], mp))
            s['title'] = generic(sub_roles(s['title'], mp))
            s['desc'] = generic(s.get('desc') or '')
            generic_line = pi > 0 or s['title'] in ('เปิดเรื่อง', 'จุดตัดสินใจ')
            au = []
            explain = pi == 1 and s['title'] != 'สัญญาณเตือน' and all(w == N for w, _ in s['audio'])
            for w, x in s['audio']:
                who = mp.get(w, w)
                if w.endswith('(คิดในใจ)'):
                    base = w.replace(' (คิดในใจ)', '')
                    who = mp.get(base, base) + ' (คิดในใจ)'
                x = generic(x if (w == N and generic_line) else sub_roles(x, mp))
                if explain and w == N:
                    who, x = 'พี่นุ่น', '“' + x + '”'
                x = particles(x, who.replace(' (คิดในใจ)', ''))
                au.append([who, x])
            if explain:
                s['visual'] = f'พี่นุ่นคุยกับ{lead}ที่มุมกาแฟ ภาพประกอบ: ' + s['visual']
            s['audio'] = au
            s['screen'] = [[a, generic(b)] for a, b in s['screen']]
            scenes.append(s)
        parts.append(dict(name=generic(p['name']), scenes=scenes))
    if key in ARC:
        last = parts[-1]['scenes'][-1]
        last['visual'] = last['visual'] + ' · ' + ARC[key]
    if 'พี่นุ่น' not in cast: cast.append('พี่นุ่น')
    est = d.get('est')
    return dict(title=d.get('topic'), cast=cast, lead=lead, est=est,
                sb=dict(audience=sb.get('audience'), theme=f'ละครซีรีส์ "ชั้น 12" · ตัวเอกตอนนี้: {lead}', music=sb.get('music'), parts=parts))

def fmt_t(x):
    x = int(round(x)); return f'{x // 60}:{x % 60:02d}'

def apply_real(dr, key):
    scenes = [s for p in dr['sb']['parts'] for s in p['scenes']]
    for a, b in VIS.get(key, []):
        for s in scenes: s['visual'] = s['visual'].replace(a, b)
    r = REAL.get(key)
    if not r: return dr
    by = {s['no']: s for s in scenes}
    for no, ch in r['edits'].items():
        s = by[no]
        a, b = s['time'].split('–'); d0 = tsec(b) - tsec(a)
        old = syl(' '.join(x for _, x in s['audio'])) or 1
        for k, v in ch.items(): s[k] = v
        new = syl(' '.join(x for _, x in s['audio']))
        s['_d'] = max(4, d0 * new / old)
    t = 0.0
    for s in scenes:
        a, b = s['time'].split('–'); d = s.pop('_d', tsec(b) - tsec(a))
        s['time'] = fmt_t(t) + '–' + fmt_t(t + d); t += d
    dr['est'] = int(round(t))
    dr['ref'] = r['ref']
    return dr

_gag_n = {}
def add_gag(dr, key):
    if key in SAMPLES: return
    lead = dr.get('lead')
    g = GAGS.get(lead)
    if not g: return
    k = _gag_n.get(lead, 0); _gag_n[lead] = k + 1
    last = dr['sb']['parts'][-1]['scenes'][-1]
    last['visual'] = last['visual'] + ' · มุกท้ายตอน: ' + g[k % len(g)]

def script_of(dr):
    L = []
    for p in dr['sb']['parts']:
        a, b = p['scenes'][0]['time'].split('–')[0], p['scenes'][-1]['time'].split('–')[1]
        L.append(f'[{a}–{b} | {p["name"]}]')
        for s in p['scenes']:
            for w, x in s['audio']: L.append(f'{w}: {x}')
            for w, x in s['screen']: L.append(f'{w}: {x}')
        L.append('')
    return '\n'.join(L).strip()

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(S, 'rows9.json')
    D = json.load(open(path))
    n = 0
    for d in D:
        if not d.get('w') or not d.get('sb'): continue
        dr = build(d)
        if dr.get('est') is None: dr['est'] = d.get('est')
        dr = apply_real(dr, (d['m'], d['w'])); add_gag(dr, (d['m'], d['w'])); dr['script'] = script_of(dr)
        if dr.get('est') is None: dr['est'] = d.get('est')
        d['drama'] = dr; n += 1
    json.dump(D, open(path, 'w'), ensure_ascii=False, indent=1)
    print('drama built for', n, 'clips')
