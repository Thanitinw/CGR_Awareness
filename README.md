# GRC in Action — แผนสื่อสาร 3 ปี

ระบบแผนงานคลิปสั้นให้ความรู้พนักงาน (ต.ค. 2569 – ก.ย. 2572) และติดตามความคืบหน้าการผลิต
เปิดใช้งานโดยดับเบิลคลิก `index.html` หรือเปิดผ่าน Live Server ก็ได้

## หน้าต่าง ๆ

| ไฟล์ | เมนู | เนื้อหา |
|---|---|---|
| `index.html` | Introduction | ที่มาโครงการ จังหวะต่อเดือน กลุ่มเนื้อหา วงจรผลิต |
| `plan.html` | Action Plan | ปฏิทิน 72 คลิป รายการคลิป และสคริปต์ (เปิดตรงได้ด้วย `plan.html#C05`) |
| `report.html` | Report Progress | KPI, Timeline (Gantt) เดือนที่แล้วถึง 4 เดือนข้างหน้า, งานที่ต้องติดตาม, จำนวนคลิปต่อขั้น, Assessment |

ทดสอบรายงานเสมือนอยู่วันอื่นได้ด้วย `report.html?today=2026-12-01`

## โครงสร้างไฟล์

```
index.html · plan.html · report.html   หน้าเว็บ (โครง HTML เท่านั้น)
assets/
  css/styles.css         ธีม สี layout ทั้งหมด (สีช่วงงาน: --ph-*)
  js/core.js             data layer ที่ทุกหน้าใช้: รวมข้อมูล วันเผยแพร่ สถานะ ความล่าช้า badge
  js/layout.js           ส่วนหัว เมนู ส่วนท้าย (เพิ่มเมนูใหม่ที่ PAGES ในไฟล์นี้)
  js/intro.js            หน้า Introduction
  js/plan.js             หน้า Action Plan + หน้าต่างสคริปต์
  js/report.js           หน้า Report Progress
data/
  config.js              ค่าคงที่: เดือนปีงบ ขั้นตอนงาน + กำหนดเสร็จ (dueDays) สถานะพิเศษ วันเผยแพร่
  groups.js              6 กลุ่มเนื้อหา
  episodes/fyYYYY-qN.js  เนื้อหาคลิป แยกตามไตรมาสของปีงบ (Q1 = ต.ค.–ธ.ค.)
  progress.js            ข้อมูลติดตามความคืบหน้า (แก้ไฟล์นี้บ่อยที่สุด)
```

ทุกหน้าโหลด: config → groups → episodes (เรียงตามเวลา) → progress → core → layout → สคริปต์ของหน้า
ถ้าเพิ่มไฟล์ episodes ใหม่ ต้องเพิ่มบรรทัด `<script>` ในทั้ง 3 หน้า

> ใช้ `<script>` ธรรมดาแทน `fetch()`/ES modules โดยตั้งใจ เพื่อให้เปิดจากไฟล์ (`file://`) ได้โดยไม่ต้องมี server

## รหัสคลิป (id)

| รหัส | ความหมาย |
|---|---|
| `C01` – `C72` | คลิปเรียงตามลำดับเผยแพร่ (เลขคี่ = Main Story สัปดาห์ที่ 1, เลขคู่ = Micro สัปดาห์ที่ 3) |
| `AS-2569`, `AS-2570`, `AS-2571` | CGR Awareness Assessment ประจำปี (พ.ย.) ตามปีงบ |

**id ห้ามเปลี่ยน** — `progress.js` ผูกกับ id ถ้าย้ายเดือนของหัวข้อ ให้แก้ `m`/`slot` และคง id เดิม

## ขั้นตอนงาน

วันเผยแพร่: Main = วันจันทร์แรกของเดือน (W1), Micro = +14 วัน (W3)
"ควรเสร็จภายใน" = วันเผยแพร่ Main ของเดือน + dueDays (ปรับได้ใน `config.js`)

| ช่วง | status | แสดงเป็น | ควรเสร็จก่อนเผยแพร่ |
|---|---|---|---|
| ยังไม่เริ่ม | `planned` | วางแผน | 70 วัน (เริ่มเขียน) |
| เนื้อหา | `draft` | Draft Script | 56 วัน |
| | `content_review` | ตรวจเนื้อหา | 42 วัน |
| | `legal_review` | ตรวจ Legal/Compliance (เฉพาะ 9 เรื่องที่ติดป้าย) | 42 วัน |
| | `final` | Final Script | 35 วัน |
| ผลิต | `shooting` | ถ่ายทำ (Main + Micro พร้อมกัน) | 21 วัน |
| | `editing` | ตัดต่อ | 10 วัน |
| | `vdo_approval` | Approve VDO | 7 วัน |
| เผยแพร่ | `ready` | พร้อมเผยแพร่ (อัปโหลด Unlisted แล้ว) | 3 วัน (Micro +14) |
| | `published` | เผยแพร่แล้ว | วันเผยแพร่ |

สถานะพิเศษ (`flag`) ใช้คู่กับ status ใดก็ได้: `revise` = ต้องแก้ไข, `hold` = พักไว้/เลื่อน (ไม่นับเป็นล่าช้า)
Assessment ใช้ชุดแยก: `planned` → `prep` → `review` → `open` → `closed` → `reported`

## อัปเดตความคืบหน้า

แก้ `data/progress.js` แล้วรีเฟรชหน้า (คลิปที่ไม่มีในไฟล์ = วางแผน)

```js
GRC.progress = {
  "C01": { status: "published", publishedAt: "2026-10-05", youtube: "https://youtu.be/xxxx", views: 1250 },
  "C03": { status: "legal_review", owner: "ทีม CGR", updated: "2026-10-06" },
  "C05": { status: "draft", flag: "revise", note: "Legal ขอแก้ตัวอย่าง Email" },
};
```

ฟิลด์ทั้งหมดอธิบายไว้ที่หัวไฟล์ `progress.js`

## แก้เนื้อหาคลิป

แก้ในไฟล์ `data/episodes/` ของไตรมาสนั้น ฟิลด์หลัก: `id`, `m` (เช่น `"ต.ค. 2569"`), `slot`, `fmt`
(ขึ้นต้น `Main Story` / `Micro Reinforcement`), `cat` (ต้องสะกดตรงกับ `groups.js`), `topic`, `story`,
`script` (`[0:00–0:08 | ชื่อช่วง]` ตามด้วย `ผู้พูด: ข้อความ`), `key`, `note`, `est` (วินาที)

## ตรวจข้อมูล

F12 → Console: `core.js` เตือน `[GRC data]` เมื่อพบ id ซ้ำ/ขาด เดือนผิด หมวดไม่อยู่ในกลุ่ม
หรือ `progress.js` อ้าง id/status/flag ที่ไม่มี

## แนวทางต่อยอด

- **หน้าแก้ไขสถานะผ่านฟอร์ม** — ต้องเลือกที่เก็บข้อมูลก่อน: ในเบราว์เซอร์ + Export, Google Sheet / SharePoint,
  หรือเว็บบน claude.ai ที่มีฐานข้อมูลกลาง; โครงสร้างข้อมูล (key = id) ใช้ต่อได้ทุกทาง
- **วันที่ทำจริงของแต่ละขั้น** — เมื่อมีฟอร์ม ให้บันทึกประวัติการเปลี่ยนสถานะ แล้วแสดงแท่ง "ของจริง" คู่กับแผนใน Timeline
