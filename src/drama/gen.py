"""Build the drama ("ชั้น 12") version of every clip into rows9.json as d['drama'].
Run: python3 drama/gen.py   (idempotent; regenerates from d['sb'] + mappings below)"""
import json, re, copy, sys, os
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(S, 'drama'))
from samples import SAMPLES
from realcase2 import REAL, VIS, GAGS
from dur import syl
from smooth import ASK, EDITS as SMOOTH
from natural import NAT
from tight import TIGHT, SUBS, EXACT
from film import FILM, SCREEN, DROP
from thai import THAI

FEMALE = {'เบล', 'มายด์', 'พี่อร', 'พี่นุ่น'}
MALE = {'พี่ต้น', 'โอ๊ต', 'พี่เอก', 'ก้อง', 'ภูมิ', 'คุณวิชัย'}
CAST = FEMALE | MALE
N = 'ผู้บรรยาย'

# role label (as used in the case version) -> cast member, per clip (m, w)
MAP = {
 ('ธ.ค. 2569', 3): {'Engineer': 'เบล'},
 ('ก.พ. 2570', 1): {'เจ้าหน้าที่สรรหา': 'เบล', 'ผู้จัดการฝ่ายบุคคล': 'พี่เอก'},
 ('ม.ค. 2570', 3): {'Marketing': 'มายด์'},
 ('ก.พ. 2570', 3): {'เจ้าหน้าที่บริการลูกค้า': 'โอ๊ต', 'หัวหน้าฝ่ายบริการ': 'พี่ต้น'},
 ('มี.ค. 2570', 1): {'Sales Manager': 'มายด์'},
 ('มี.ค. 2570', 5): {'พนักงานบัญชี': 'พี่อร', 'เพื่อนร่วมงาน': 'โอ๊ต'},
 ('เม.ย. 2570', 1): {'ผู้จัดการโครงการก่อสร้าง': 'พี่ต้น'},
 ('พ.ค. 2570', 1): {'ช่างเทคนิคไซต์': 'โอ๊ต', 'หัวหน้างานไซต์': 'พี่ต้น'},
 ('เม.ย. 2570', 3): {'พนักงานขาย': 'มายด์'},
 ('พ.ค. 2570', 3): {'Sales Engineer คนใหม่': 'ก้อง', 'Sales Manager': 'มายด์'},
 ('มิ.ย. 2570', 1): {'ผู้บริหาร': 'พี่ต้น', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('ก.ค. 2570', 1): {'เจ้าหน้าที่บัญชี': 'พี่อร', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('มิ.ย. 2570', 3): {'Site Manager': 'พี่ต้น'},
 ('ก.ค. 2570', 3): {'หัวหน้างานไซต์': 'โอ๊ต'},
 ('ส.ค. 2570', 1): {'Business Manager': 'โอ๊ต'},
 ('ก.ย. 2570', 1): {'วิศวกรโครงการ': 'โอ๊ต', 'ผู้จัดการโครงการ': 'พี่ต้น'},
 ('ส.ค. 2570', 3): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร'},
 ('ต.ค. 2570', 1): {'ช่างติดตั้งโซลาร์': 'โอ๊ต', 'หัวหน้าทีมติดตั้ง': 'พี่ต้น'},
 ('ก.ย. 2570', 3): {'Project Manager': 'พี่ต้น'},
 ('ต.ค. 2570', 3): {'วิศวกรพี่เลี้ยง': 'โอ๊ต'},
 ('พ.ย. 2570', 1): {'Site Manager': 'พี่ต้น'},
 ('ธ.ค. 2570', 1): {'วิศวกรโครงการ': 'มายด์'},
 ('พ.ย. 2570', 3): {'ผู้จัดการจัดซื้อ': 'พี่อร'},
 ('ธ.ค. 2570', 3): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร', 'ผู้จัดการฝ่ายจัดซื้อ': 'พี่ต้น'},
 ('ม.ค. 2571', 1): {'พนักงานบัญชี': 'พี่อร', 'เพื่อนร่วมงาน': 'เบล'},
 ('ก.พ. 2571', 1): {'วิศวกรออกแบบ': 'เบล', 'หัวหน้าแผนกวิศวกรรม': 'พี่ต้น'},
 ('ม.ค. 2571', 3): {'Business Development': 'มายด์'},
 ('ก.พ. 2571', 3): {'ช่างเทคนิคโซลาร์': 'โอ๊ต', 'หัวหน้าทีมติดตั้ง': 'พี่ต้น'},
 ('มี.ค. 2571', 1): {'Sales': 'พี่ต้น'},
 ('เม.ย. 2571', 1): {'Sales Engineer': 'มายด์', 'วิศวกรออกแบบ': 'เบล'},
 ('มี.ค. 2571', 3): {'Sales Manager': 'มายด์'},
 ('เม.ย. 2571', 3): {'Sales Manager': 'พี่ต้น'},
 ('พ.ค. 2571', 1): {'ทีมงาน': 'พี่ต้น'},
 ('มิ.ย. 2571', 1): {'หัวหน้าไซต์งาน': 'พี่ต้น', 'ธุรการไซต์งาน': 'เบล', 'เจ้าหน้าที่บัญชี': 'พี่อร'},
 ('พ.ค. 2571', 3): {'IT': 'เบล'},
 ('มิ.ย. 2571', 3): {'เจ้าหน้าที่ HR': 'พี่เอก', 'เจ้าหน้าที่ IT': 'เบล'},
 ('ก.ค. 2571', 1): {'Project Manager': 'พี่ต้น', 'Project Engineer': 'โอ๊ต'},
 ('ส.ค. 2571', 1): {'เจ้าหน้าที่วางแผนการผลิต': 'พี่อร'},
 ('ก.ค. 2571', 3): {'พนักงาน A': 'โอ๊ต', 'พนักงาน B': 'มายด์'},
 ('ส.ค. 2571', 3): {'วิศวกรขาย': 'มายด์'},
 ('ก.ย. 2571', 1): {'วิศวกรอาวุโส': 'โอ๊ต', 'HR': 'พี่เอก'},
 ('ต.ค. 2571', 1): {'เจ้าหน้าที่ความปลอดภัย': 'โอ๊ต'},
 ('ก.ย. 2571', 3): {'Engineer บริษัท': 'เบล'},
 ('ต.ค. 2571', 3): {'วิศวกรระบบอัตโนมัติ': 'ก้อง', 'หัวหน้าวิศวกรรม': 'พี่ต้น'},
 ('พ.ย. 2571', 1): {'เจ้าหน้าที่จัดซื้อ': 'ภูมิ', 'ผู้จัดการ': 'พี่อร'},
 ('ธ.ค. 2571', 1): {'เจ้าหน้าที่จัดซื้อ': 'พี่อร', 'วิศวกรฝ่ายผลิต': 'โอ๊ต'},
 ('พ.ย. 2571', 3): {'Sales Manager': 'มายด์', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('ธ.ค. 2571', 3): {'ผู้จัดการไซต์โซลาร์ฟาร์ม': 'โอ๊ต'},
 ('ม.ค. 2572', 1): {'ผู้จัดการโครงการ': 'พี่ต้น', 'วิศวกรโครงการ': 'โอ๊ต'},
 ('ก.พ. 2572', 1): {'วิศวกรออกแบบ': 'เบล', 'ผู้จัดการโครงการ': 'มายด์'},
 ('ม.ค. 2572', 3): {'หัวหน้าทีม': 'พี่ต้น', 'พนักงาน A': 'โอ๊ต', 'พนักงาน B': 'มายด์'},
 ('ก.พ. 2572', 3): {'หัวหน้าหน่วยซ่อมบำรุง': 'พี่ต้น', 'เพื่อนร่วมงานอาวุโส': 'พี่อร'},
 ('มี.ค. 2572', 1): {'วิศวกรโครงการ': 'โอ๊ต'},
 ('เม.ย. 2572', 1): {'พนักงานฝ่ายผลิต': 'ภูมิ', 'หัวหน้าไลน์ผลิต': 'พี่ต้น'},
 ('มี.ค. 2572', 3): {'พนักงาน': 'พี่อร'},
 ('เม.ย. 2572', 3): {'Project Coordinator': 'เบล', 'วิศวกรโครงการ': 'โอ๊ต'},
 ('พ.ค. 2572', 1): {'Project Manager': 'พี่ต้น'},
 ('มิ.ย. 2572', 1): {'วิศวกรสนาม': 'ภูมิ', 'หัวหน้าคนงาน': 'โอ๊ต', 'ผู้จัดการโครงการ': 'พี่ต้น'},
 ('พ.ค. 2572', 3): {'Auditor': 'พี่อร'},
 ('มิ.ย. 2572', 3): {'เจ้าหน้าที่จัดซื้อ': 'ภูมิ', 'ผู้จัดการจัดซื้อ': 'พี่อร'},
 ('ก.ค. 2572', 1): {'กรรมการสอบสวน': 'พี่เอก'},
 ('ส.ค. 2572', 1): {'เจ้าหน้าที่ HR': 'ภูมิ', 'หัวหน้าแผนก HR': 'พี่เอก'},
 ('ก.ค. 2572', 3): {'Marketing': 'มายด์'},
 ('ส.ค. 2572', 3): {'เจ้าหน้าที่ธุรการโรงงาน': 'เบล', 'ผู้จัดการโรงงาน': 'พี่ต้น'},
 ('ก.ย. 2572', 1): {'เจ้าหน้าที่การเงิน': 'พี่อร'},
 ('ต.ค. 2572', 1): {'เจ้าหน้าที่วิเคราะห์ธุรกิจ': 'ภูมิ', 'หัวหน้าทีม': 'เบล'},
 ('ก.ย. 2572', 3): {'Project Director': 'พี่ต้น', 'Procurement': 'พี่อร', 'Sales': 'มายด์', 'Marketing': 'เบล', 'เจ้าหน้าที่ Compliance': 'พี่นุ่น'},
 ('ต.ค. 2572', 3): {'วิศวกรจบใหม่': 'ภูมิ', 'วิศวกรอาวุโส': 'เบล'},
}
# year-arc beats shown in the closing scene's picture (no extra voice, so length stays the same)
ARC = {
 ('มี.ค. 2570', 5): 'ฉากหลัง: พี่อรวางแฟ้มลง ยิ้มโล่งใจ เพื่อนร่วมทีมชั้น 12 ส่งกาแฟให้',
 ('ต.ค. 2570', 3): 'ฉากหลัง: เบลเปิด Email "ผลประเมินประจำปี: ผ่าน" ครบหนึ่งปีที่ชั้น 12 แล้วแปะโน้ต 3 คำถามที่จอของตัวเอง',
 ('พ.ย. 2570', 1): 'ฉากหลัง: ป้ายชื่อบนโต๊ะพี่ต้นเปลี่ยนเป็น "ผู้จัดการฝ่ายปฏิบัติการ" กระดานทีมเขียนว่า "ดีลใหญ่ เริ่มแล้ว"',
 ('ต.ค. 2571', 1): 'ฉากหลัง: โอ๊ตกลับเข้าห้องประชุมโครงการใหญ่ เก้าอี้ที่เคยว่างมีคนนั่งแล้ว',
 ('ต.ค. 2571', 3): 'ฉากหลัง: กระดานทีมเขียนว่า "ส่งมอบดีลใหญ่ ✓" ทีมชั้น 12 ปรบมือ',
 ('พ.ย. 2571', 1): 'ฉากหลัง: ภูมิในวันแรกเดินตามเบลไปที่โต๊ะ เบลยื่นโน้ต 3 คำถามให้',
 ('ม.ค. 2572', 3): 'ฉากหลัง: ทีมชั้น 12 กลับมานั่งทำงานด้วยกันตามปกติ ไม่มีใครถามหาชื่อผู้แจ้ง',
 ('ต.ค. 2572', 1): 'ฉากหลัง: ภูมิแปะโน้ต 3 คำถามที่จอของตัวเอง เบลยิ้ม',
 ('ต.ค. 2572', 3): 'ฉากหลัง: กล้องเลื่อนผ่านทุกโต๊ะที่มีโน้ตคำถามก่อนตัดสินใจแปะอยู่ จบที่แก้วพี่ต้นที่สลักใหม่ว่า "งานต้องเดิน...อย่างถูกต้อง"',
}
# industry words -> neutral company words (generic setting)
GENERIC = [
 ('ไซต์สถานีไฟฟ้า', 'ไซต์งาน'), ('สถานีไฟฟ้าแรงสูง', 'พื้นที่ซ่อมบำรุงระบบ'), ('สถานีไฟฟ้า', 'ไซต์งาน'), ('ไซต์โซลาร์ฟาร์ม', 'ไซต์งาน'), ('โซลาร์ฟาร์ม', 'ไซต์ลูกค้า'),
 ('ติดตั้งโซลาร์', 'ติดตั้งระบบ'), ('งานติดโซลาร์', 'งานติดตั้งระบบ'), ('Drawing', 'แบบ'), ('ติดโซลาร์', 'ติดตั้งระบบ'), ('แผงโซลาร์', 'อุปกรณ์'),
 ('น้ำมันหม้อแปลง', 'น้ำมันเครื่องจักร'), ('หม้อแปลง', 'เครื่องจักร'), ('ตู้ไฟฟ้า', 'ตู้ควบคุม'),
 ('เวลาดับไฟ', 'เวลาหยุดระบบ'), ('ดับไฟ', 'หยุดระบบ'),
 ('ไซต์ก่อสร้างไซต์งาน', 'ไซต์ก่อสร้าง'), ('ไซต์โครงการไซต์ลูกค้า', 'ไซต์โครงการลูกค้า'),
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

# ---- characters are shown by role, not by name ("พี่ HR", "พี่จัดซื้อ", "พี่เซลส์" ...) ----
# names stay inside the pipeline (gender particles, gags, arcs) and are swapped for role labels at the end
DEFAULT = {'พี่นุ่น': 'พี่ Compliance', 'พี่ต้น': 'หัวหน้า', 'พี่อร': 'พี่บัญชี', 'พี่เอก': 'พี่ HR',
           'มายด์': 'พี่เซลส์', 'โอ๊ต': 'พี่หน้างาน', 'ก้อง': 'น้องเซลส์', 'ภูมิ': 'น้องใหม่'}
BELL = {1: 'น้องใหม่', 2: 'น้องดิจิทัล', 3: 'พี่ดิจิทัล'}   # เบล: new hire in year 1, mentor in year 3
LABELS = {
 ('พ.ย. 2569', 1): {'โอ๊ต': 'พี่วิศวกร'},
 ('พ.ย. 2569', 3): {'โอ๊ต': 'พี่วิศวกร'},
 ('ธ.ค. 2569', 3): {'เบล': 'น้องวิศวกร'},
 ('ก.พ. 2570', 1): {'เบล': 'น้อง HR'},
 ('ม.ค. 2570', 3): {'มายด์': 'พี่การตลาด'},
 ('ก.พ. 2570', 3): {'โอ๊ต': 'พี่บริการลูกค้า'},
 ('เม.ย. 2570', 1): {'พี่ต้น': 'พี่ PM'},
 ('พ.ค. 2570', 1): {'โอ๊ต': 'พี่ช่าง', 'พี่ต้น': 'หัวหน้าไซต์'},
 ('มิ.ย. 2570', 3): {'พี่ต้น': 'หัวหน้าไซต์'},
 ('ก.ค. 2570', 3): {'โอ๊ต': 'หัวหน้าไซต์', 'พี่ต้น': 'พี่ PM'},
 ('ส.ค. 2570', 1): {'โอ๊ต': 'พี่ฝ่ายธุรกิจ'},
 ('ก.ย. 2570', 1): {'โอ๊ต': 'พี่วิศวกร', 'พี่ต้น': 'พี่ PM'},
 ('ส.ค. 2570', 3): {'พี่อร': 'พี่จัดซื้อ'},
 ('ต.ค. 2570', 1): {'โอ๊ต': 'พี่ช่าง', 'พี่ต้น': 'หัวหน้าช่าง'},
 ('ก.ย. 2570', 3): {'พี่ต้น': 'พี่ PM'},
 ('ต.ค. 2570', 3): {'โอ๊ต': 'พี่วิศวกร'},
 ('พ.ย. 2570', 1): {'พี่ต้น': 'หัวหน้าไซต์'},
 ('ธ.ค. 2570', 1): {'มายด์': 'พี่วิศวกร'},
 ('พ.ย. 2570', 3): {'พี่อร': 'พี่จัดซื้อ'},
 ('ธ.ค. 2570', 3): {'พี่อร': 'พี่จัดซื้อ'},
 ('ก.พ. 2571', 1): {'เบล': 'น้องวิศวกร'},
 ('ม.ค. 2571', 3): {'มายด์': 'พี่ฝ่ายธุรกิจ'},
 ('ก.พ. 2571', 3): {'โอ๊ต': 'พี่ช่าง', 'พี่ต้น': 'หัวหน้าช่าง'},
 ('มี.ค. 2571', 1): {'พี่ต้น': 'หัวหน้าเซลส์'},
 ('เม.ย. 2571', 1): {'เบล': 'น้องวิศวกร'},
 ('เม.ย. 2571', 3): {'พี่ต้น': 'หัวหน้าเซลส์'},
 ('พ.ค. 2571', 1): {'พี่ต้น': 'หัวหน้าทีม'},
 ('มิ.ย. 2571', 1): {'พี่ต้น': 'หัวหน้าไซต์', 'เบล': 'น้องธุรการ'},
 ('พ.ค. 2571', 3): {'เบล': 'น้อง IT'},
 ('มิ.ย. 2571', 3): {'เบล': 'น้อง IT'},
 ('ก.ค. 2571', 1): {'พี่ต้น': 'พี่ PM', 'โอ๊ต': 'พี่วิศวกร'},
 ('ส.ค. 2571', 1): {'พี่อร': 'พี่วางแผนผลิต'},
 ('ก.ค. 2571', 3): {'โอ๊ต': 'พี่ฝ่ายผลิต', 'มายด์': 'พี่ QC'},
 ('ก.ย. 2571', 1): {'โอ๊ต': 'พี่วิศวกร'},
 ('ต.ค. 2571', 1): {'โอ๊ต': 'พี่เซฟตี้'},
 ('ก.ย. 2571', 3): {'เบล': 'น้องวิศวกร'},
 ('ต.ค. 2571', 3): {'ก้อง': 'น้องวิศวกร'},
 ('พ.ย. 2571', 1): {'ภูมิ': 'น้องจัดซื้อ', 'พี่อร': 'พี่จัดซื้อ'},
 ('ธ.ค. 2571', 1): {'พี่อร': 'พี่จัดซื้อ', 'โอ๊ต': 'พี่วิศวกร'},
 ('ธ.ค. 2571', 3): {'โอ๊ต': 'หัวหน้าไซต์'},
 ('ม.ค. 2572', 1): {'พี่ต้น': 'พี่ PM', 'โอ๊ต': 'พี่วิศวกร'},
 ('ก.พ. 2572', 1): {'เบล': 'พี่วิศวกร', 'มายด์': 'พี่ PM'},
 ('ก.พ. 2572', 3): {'พี่ต้น': 'หัวหน้าซ่อมบำรุง', 'พี่อร': 'พี่จัดซื้อ'},
 ('มี.ค. 2572', 1): {'โอ๊ต': 'พี่วิศวกร'},
 ('เม.ย. 2572', 1): {'ภูมิ': 'น้องฝ่ายผลิต', 'พี่ต้น': 'หัวหน้าไลน์'},
 ('เม.ย. 2572', 3): {'เบล': 'พี่ประสานงาน', 'โอ๊ต': 'พี่วิศวกร'},
 ('พ.ค. 2572', 1): {'พี่ต้น': 'พี่ PM'},
 ('มิ.ย. 2572', 1): {'ภูมิ': 'น้องวิศวกร', 'โอ๊ต': 'พี่โฟร์แมน', 'พี่ต้น': 'พี่ PM'},
 ('พ.ค. 2572', 3): {'พี่อร': 'พี่ Audit'},
 ('มิ.ย. 2572', 3): {'ภูมิ': 'น้องจัดซื้อ', 'พี่อร': 'พี่จัดซื้อ'},
 ('ส.ค. 2572', 1): {'ภูมิ': 'น้อง HR'},
 ('ก.ค. 2572', 3): {'มายด์': 'พี่การตลาด'},
 ('ส.ค. 2572', 3): {'เบล': 'พี่ธุรการ', 'พี่ต้น': 'ผู้จัดการโรงงาน'},
 ('ก.ย. 2572', 1): {'พี่อร': 'พี่การเงิน'},
 ('ต.ค. 2572', 1): {'ภูมิ': 'น้องนักวิเคราะห์', 'เบล': 'หัวหน้าทีม'},
 ('ก.ย. 2572', 3): {'พี่ต้น': 'หัวหน้าโครงการ', 'พี่อร': 'พี่จัดซื้อ', 'เบล': 'พี่การตลาด'},
 ('ต.ค. 2572', 3): {'ภูมิ': 'น้องวิศวกร', 'เบล': 'พี่วิศวกร'},
}
# leftovers of the case-version role words that were swapped for a name
FIX = {('พ.ย. 2571', 1): [('พี่อรฝ่าย', 'ผู้จัดการฝ่าย')], ('พ.ค. 2571', 1): [('พี่ต้นมองหน้ากัน', 'ทีมงานมองหน้ากัน')],
       # review 22 ต.ค. 2569: pronouns that did not fit the speaker
       ('ก.ค. 2570', 3): [('ถ้าฉันเซ็นตอนนี้ แปลว่าฉันยืนยัน', 'ถ้าผมเซ็นตอนนี้ แปลว่าผมยืนยัน'), ('ฉันส่งแผนให้แล้ว', 'ผมส่งแผนให้แล้ว')],
       ('พ.ย. 2570', 3): [('ขอบคุณคะ แต่ครอบครัวเรา', 'ขอบคุณค่ะ แต่ครอบครัวเรา')],
       ('ส.ค. 2571', 1): [('ในระบบจะมีชื่อหนูเป็นคนกรอก', 'ในระบบจะมีชื่อเราเป็นคนกรอก'), ('หนูขอบันทึกตามจริงนะคะ', 'เราขอบันทึกตามจริงนะคะ'), ('พี่รับผิดชอบเอง ทั้งทีม', 'ผมรับผิดชอบเอง ทั้งทีม')],
       ('เม.ย. 2572', 3): [('หนูว่าจะซื้อเก็บไว้หน่อย', 'เราว่าจะซื้อเก็บไว้หน่อย')],
       ('ก.ย. 2572', 3): [('เดี๋ยวหนูใช้ฐานลูกค้าเก่า', 'เดี๋ยวเราใช้ฐานลูกค้าเก่า')],
       ('ก.ค. 2572', 1): [('ห้องประชุมคณะพี่เอก', 'ห้องประชุมคณะกรรมการสอบสวน')]}
NAME_RE = {'พี่นุ่น': 'พี่นุ่น', 'พี่ต้น': 'พี่ต้น', 'พี่อร': 'พี่อร', 'พี่เอก': 'พี่เอก(?!สาร|ชน|ภาพ|ลักษณ์)',
           'มายด์': '(?:น้อง|คุณ)?มายด์', 'โอ๊ต': '(?:น้อง|พี่|คุณ)?โอ๊ต', 'เบล': '(?:น้อง|พี่|คุณ)?เบล(?!อ)',
           'ก้อง': '(?<!เสียง)(?:น้อง|คุณ)?ก้อง(?!กังวาน)', 'ภูมิ': '(?:น้อง|คุณ)?ภูมิ(?!ใจ|ภาค|คุ้ม|ศาสตร์|ลำเนา|ประเทศ|ทัศน์|ปัญญา|หลัง|แพ้|ธรรม|ฐาน)'}
LATIN_END = re.compile(r'[A-Za-z]$')

def labels_for(key, date):
    yr = 1 if date < '2027-11' else 2 if date < '2028-11' else 3   # plan years run Nov–Oct
    lab = dict(DEFAULT, เบล=BELL[yr]); lab.update(LABELS.get(key, {}))
    return lab

def relabel(dr, key, date):
    lab = labels_for(key, date)
    blob = json.dumps(dr, ensure_ascii=False)
    for a, b in FIX.get(key, []): blob = blob.replace(a, b)
    present = [n for n in NAME_RE if re.search(NAME_RE[n], blob)]
    used = [lab[n] for n in present]
    assert len(set(used)) == len(used), (key, present, used)
    for n in sorted(present, key=len, reverse=True):
        L = lab[n]
        rep = (lambda m, L=L: L + (' ' if LATIN_END.search(L) and m.string[m.end():m.end() + 1] not in ' "”“:,.)/' else ''))
        blob = re.sub(NAME_RE[n], rep, blob)
    out = json.loads(blob)
    order = [n for n in dr['cast'] if n != 'พี่นุ่น'] + [n for n in present if n not in dr['cast']] + ['พี่นุ่น']
    out['cast'] = [lab[n] + (' (ญ)' if n in FEMALE else ' (ช)') for n in dict.fromkeys(order) if n in lab]
    out['lead'] = lab.get(dr['lead'], dr['lead'])
    return out

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

def apply_smooth(dr, key):
    """story-flow fixes (smooth.py): lead asks Compliance first, silent characters get a line, re-time the clip"""
    E = {no: dict(ch) for no, ch in SMOOTH.get(key, {}).items()}
    if key in ASK:
        no, who, line = ASK[key]
        e = E.setdefault(no, {})
        e.setdefault('vrep', []).append((f'พี่นุ่นคุยกับ{who}ที่มุมกาแฟ', f'{who}เดินมาถามพี่นุ่นที่มุมกาแฟ'))
        e['pre'] = [[who, line]] + e.get('pre', [])
    if not E: return dr
    scenes = [s for p in dr['sb']['parts'] for s in p['scenes']]
    by = {s['no']: s for s in scenes}
    for no, ch in E.items():
        s = by[no]
        a, b = s['time'].split('–'); d0 = tsec(b) - tsec(a)
        old = syl(' '.join(x for _, x in s['audio']))
        if 'visual' in ch: s['visual'] = ch['visual']
        for x, y in ch.get('vrep', []):
            assert x in s['visual'], (key, no, x, s['visual']); s['visual'] = s['visual'].replace(x, y)
        for x, y in ch.get('arep', []):
            hit = [l for l in s['audio'] if x in l[1]]; assert hit, (key, no, x)
            for l in hit: l[1] = l[1].replace(x, y)
        s['audio'] = [list(l) for l in ch.get('pre', [])] + s['audio'] + [list(l) for l in ch.get('post', [])]
        new = syl(' '.join(x for _, x in s['audio']))
        if new != old: s['_d'] = max(4, d0 + (new - old) / 4.0 + (0.5 if new > old else 0))   # added speech at 4 syllables/s + a breath
    t = 0.0
    for s in scenes:
        a, b = s['time'].split('–'); d = s.pop('_d', tsec(b) - tsec(a))
        s['time'] = fmt_t(t) + '–' + fmt_t(t + d); t += d
    dr['est'] = int(round(t))
    return dr

def apply_natural(dr, key, src=None):
    """natural.py: every line reworded into natural spoken Thai (review 23 ต.ค. 2569); keys are 'scene.line' after apply_smooth.
    tight.py (src=TIGHT) is the second pass: shorter, casual workplace Thai"""
    N = (NAT if src is None else src).get(key)
    if not N: return dr
    by = {s['no']: s for p in dr['sb']['parts'] for s in p['scenes']}
    for k, txt in N.items():
        no, j = k.split('.'); no, j = int(no), int(j)
        assert no in by and j < len(by[no]['audio']), (key, k)
        who = by[no]['audio'][j][0]
        quoted = txt.startswith('“')
        assert quoted == (who != 'ผู้บรรยาย'), (key, k, who, txt[:20])
        by[no]['audio'][j][1] = txt
    return dr

def apply_exact(dr, key):
    """tight.py EXACT: lines the user dictated verbatim; every scene line of the episode must be listed (speaker checked)"""
    X = EXACT.get(key)
    if not X: return dr
    by = {s['no']: s for p in dr['sb']['parts'] for s in p['scenes']}
    have = {f"{s['no']}.{j}" for s in by.values() for j in range(len(s['audio']))}
    assert have - {'12.0'} <= set(X) or key != ('พ.ย. 2569', 1), (key, sorted(have - set(X)))
    for k, (who, txt) in X.items():
        no, j = map(int, k.split('.'))
        assert by[no]['audio'][j][0] == who, (key, k, by[no]['audio'][j][0], who)
        by[no]['audio'][j][1] = txt
    return dr

def apply_subs(dr, key):
    """tight.py SUBS: word-level fixes on the final lines (no slang); thai.py: English words in speech become Thai"""
    by = {s['no']: s for p in dr['sb']['parts'] for s in p['scenes']}
    for k, n, a, b in SUBS:
        if k != key: continue
        no, j = map(int, n.split('.'))
        l = by[no]['audio'][j]; assert a in l[1], (key, n, a); l[1] = l[1].replace(a, b)
    for s in by.values():
        for l in s['audio']:
            for a, b in THAI: l[1] = re.sub(r'(?<![A-Za-z@._/-])' + re.escape(a) + r'(?![A-Za-z])', b, l[1])
            l[1] = re.sub(r'(หรือ|ถาม|กับ|แจ้ง|ปรึกษา) ฝ่ายคอมพลายแอนซ์', r'\1ฝ่ายคอมพลายแอนซ์', l[1])
    return dr

FREEZE = re.compile(r'ภาพหยุดนิ่ง|หยุดภาพ|วงนับถอยหลัง|หยุดนิ่ง +|ช็อตหยุดคิด')
def lean_edit(dr, date):
    """review 23 ต.ค. 2569: little post-production per episode — one freeze scene, on-screen text only on the title, the freeze and the end card,
    no graphic overlays; former graphic scenes are filmed (film.py)"""
    scenes = [s for p in dr['sb']['parts'] for s in p['scenes']]
    for s in scenes:
        if (date, s['no']) in FILM: s['visual'] = FILM[(date, s['no'])][3]
        s['visual'] = re.sub(r'\s*ภาพประกอบ:.*?(?= · |$)', '', s['visual'])
    fz = [s for s in scenes if FREEZE.search(s['visual'])]
    assert len(fz) <= 1, (date, [s['no'] for s in fz])
    for s in fz:   # review 27 ต.ค. 2569: the pause-for-thought scene is filmed in Flow (slow push-in, everyone still); editing adds only the question and the 3-2-1 countdown text
        v = re.sub(r'ข้อความบนจอ\s*"[^"]*"\s*', '', s['visual'])
        v = re.sub(r'\s*(พร้อม)?วงนับถอยหลัง 3 วินาที', '', v)
        v = re.sub(r'ภาพหยุดนิ่ง:?\s*(ที่)?|\s*หยุดนิ่ง|หยุดภาพ(ที่)?\s*', ' ', v).strip(' ·,')
        v = re.sub(r'\s+', ' ', v)
        s['visual'] = 'ช็อตหยุดคิด (สร้างใน Flow): ' + v + ' · ทุกคนในภาพนิ่ง กล้องค่อย ๆ ดันเข้า ผู้บรรยายถามคำถามชวนคิด'
        s['screen'] = []   # no question card or countdown (review 27 ต.ค. 2569): the narrator asks, the subtitle shows it
    # review 27 ต.ค. 2569: no end-card text (the narrator already says it, the subtitle shows it); kept as dr['summary'] for the YouTube description
    for s in scenes:
        if (date, s['no']) in SCREEN: s['screen'] = [[(s['screen'][0][0] if s['screen'] else 'ข้อความบนจอ'), x] for x in SCREEN[(date, s['no'])]]
    dr['summary'] = next((x for _, x in scenes[-1]['screen']), '')
    keep = {scenes[0]['no']} | {no for (dt, no) in SCREEN if dt == date and no != scenes[-1]['no']}
    for s in scenes:
        if s['no'] not in keep: s['screen'] = []
    if any(k[0] == date for k in DROP):
        for p in dr['sb']['parts']: p['scenes'] = [s for s in p['scenes'] if (date, s['no']) not in DROP]
        dr['sb']['parts'] = [p for p in dr['sb']['parts'] if p['scenes']]
        t = 0.0
        for n, s in enumerate((s for p in dr['sb']['parts'] for s in p['scenes']), 1):
            a, b = s['time'].split('–'); d = tsec(b) - tsec(a)
            s['no'] = n; s['time'] = fmt_t(t) + '–' + fmt_t(t + d); t += d
        dr['est'] = int(round(t))
    return dr

PACE = 4.5          # syllables per second: brisk, natural Thai (review 22 ต.ค. 2569: every episode ≤ 2 minutes, faster storytelling)
MAX_EP = 118        # seconds, leaves room under the 2-minute cap
def pace(dr):
    """re-time every scene from its speech: brisk pace, short breath between scenes, countdown scenes keep 3 s of countdown"""
    scenes = [s for p in dr['sb']['parts'] for s in p['scenes']]
    D = []
    for s in scenes:
        n = syl(' '.join(x for _, x in s['audio']))
        cd = False   # review 27 ต.ค. 2569: no on-screen countdown any more, the pause scene is timed by its narration
        d = n / PACE + (0.6 if n else 0)
        D.append(max(d, 4.5 if cd else 3.0 if n else 2.5))
    tot = sum(D)
    if tot > MAX_EP:                        # still long: trim the breathing room evenly
        pad = sum(max(0, d - n) for d, n in zip(D, [syl(' '.join(x for _, x in s['audio'])) / PACE for s in scenes]))
        k = max(0.0, 1 - (tot - MAX_EP) / pad) if pad else 1
        D = [n + (d - n) * k for d, n in zip(D, [syl(' '.join(x for _, x in s['audio'])) / PACE for s in scenes])]
    t = 0.0
    for s, d in zip(scenes, D):
        s['time'] = fmt_t(t) + '–' + fmt_t(t + d); t += d
    dr['est'] = int(round(t))
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
    for d in sorted(D, key=lambda d: d.get('moved_from') or d.get('date') or ''):   # original order keeps each episode's end gag (reorder 27 ต.ค. 2569)
        if not d.get('w') or not d.get('sb'): continue
        dr = build(d)
        if dr.get('est') is None: dr['est'] = d.get('est')
        dr = apply_real(dr, (d['m'], d['w'])); dr = apply_smooth(dr, (d['m'], d['w'])); dr = apply_natural(dr, (d['m'], d['w'])); dr = apply_natural(dr, (d['m'], d['w']), TIGHT); dr = apply_subs(dr, (d['m'], d['w'])); dr = apply_exact(dr, (d['m'], d['w'])); dr = pace(dr); add_gag(dr, (d['m'], d['w']))
        if (d['m'], d['w']) in ARC: dr['arc'] = ARC[(d['m'], d['w'])].split(': ', 1)[1]
        dr = relabel(dr, (d['m'], d['w']), d['date']); dr = lean_edit(dr, d['date']); dr['script'] = script_of(dr)
        if dr.get('est') is None: dr['est'] = d.get('est')
        d['drama'] = dr; n += 1
    import flow; flow.attach(D)   # Google Flow shot data (flow_en.txt)
    json.dump(D, open(path, 'w'), ensure_ascii=False, indent=1)
    print('drama built for', n, 'clips')
