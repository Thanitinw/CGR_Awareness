# Governance in Action — แผนสื่อสาร 3 ปี

คลิปสั้นให้ความรู้ด้านธรรมาภิบาลสำหรับพนักงานในกลุ่มบริษัท ต.ค. 2569 – ก.ย. 2572
71 คลิป · อังคารที่ 1 และ 3 ของเดือน เวลา 17:00 น. · ส่งลิงก์ YouTube (Unlisted) ในกลุ่ม LINE

เปิดใช้งาน: ดับเบิลคลิก `index.html` (ไฟล์เดียว ไม่ต้องมี server)

แท็บ: Introduction · Responsibility · Action Plan (ปฏิทิน + สตอรีบอร์ด/สคริปต์ทุกคลิป) · Measurement

## แก้ไขเนื้อหา

```
src/rows9.json     ข้อมูลคลิปทั้งหมด (หัวข้อ สคริปต์ สตอรีบอร์ด เจ้าของเนื้อหา วันเผยแพร่)
src/body3.html     โครงหน้าเว็บ + สคริปต์แสดงผล
src/tpl.html       ส่วนหัวและสไตล์หลัก
src/build_page.py  รวมไฟล์ด้านบนเป็น index.html
```

แก้ไฟล์ใน `src/` แล้วรัน `python3 src/build_page.py` เพื่อสร้าง `index.html` ใหม่

## แก้สตอรีบอร์ดจากหน้าเว็บ

1. เปิดหน้าเว็บจาก GitHub Pages (หรือไฟล์ `index.html` บนเครื่อง) → เปิดคลิป → ปุ่ม **✎ แก้ไข**
2. ใส่รหัสผ่านสำหรับแก้ไข (ขอจากผู้ดูแล) → แก้ ภาพ / Keyword บนจอ / เสียง เพิ่มหรือลบฉากได้
3. กด **บันทึกขึ้น Git** → หน้าเว็บ commit `src/rows9.json` และ `index.html` เข้า branch `main` ทันที (เวลาแต่ละฉากคำนวณใหม่อัตโนมัติ)

ตั้งหรือเปลี่ยนรหัสผ่าน (ผู้ดูแลเท่านั้น ทำบนเครื่อง ไม่มีบนหน้าเว็บ):
`pip install cryptography` แล้ว `python3 tools/set_editor_password.py` → ใส่ GitHub fine-grained token
(Repository access: เฉพาะ repo นี้ · Permissions: Contents = Read and write) และรหัสผ่านอย่างน้อย 12 ตัวอักษร
→ commit + push `src/editor-key.json` · token ถูกเข้ารหัสด้วยรหัสผ่าน (PBKDF2 + AES-GCM) ก่อนเก็บ

> `src/rows9.json` ใน repo คือข้อมูลล่าสุดเสมอ (รวมการแก้จากหน้าเว็บ) ก่อนแก้ไฟล์ใน `src/` บนเครื่อง ให้ `git pull` ก่อนทุกครั้ง
