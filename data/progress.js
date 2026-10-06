/* =========================================================================
   progress.js — ข้อมูลติดตามความคืบหน้า (แยกจากเนื้อหาคลิปโดยเจตนา)
   -------------------------------------------------------------------------
   key = id ของคลิปใน data/episodes (เช่น "C01", "AS-2569")
   คลิปที่ไม่มีในนี้ = "วางแผน" โดยอัตโนมัติ
   วันตามแผนและกำหนดเสร็จแต่ละขั้น ระบบคำนวณเองจากวันเผยแพร่ (ดู config.js → dueDays)

   ฟิลด์ (ใส่เฉพาะที่มี ไม่ต้องครบ):
     status       ขั้นปัจจุบันของคลิป:
                    planned · draft · content_review · legal_review · final ·
                    shooting · editing · vdo_approval · ready · published
                  ของ Assessment (AS-xxxx):
                    planned · prep · review · open · closed · reported
     flag         สถานะพิเศษ (ไม่ใส่ = ปกติ): "revise" (ต้องแก้ไข) · "hold" (พักไว้/เลื่อน)
     owner        ผู้รับผิดชอบ
     note         หมายเหตุสั้น ๆ (เช่น เหตุผลที่ต้องแก้ไข)
     scriptUrl    ลิงก์ไฟล์สคริปต์ล่าสุด
     publishedAt  วันที่เผยแพร่จริง "YYYY-MM-DD" (ค.ศ.)
     youtube      ลิงก์ YouTube
     views        ยอดวิว (ตัวเลข) · avgWatchSec เวลาดูเฉลี่ย (วินาที)
     updated      วันที่อัปเดตข้อมูลนี้ "YYYY-MM-DD"

   ตัวอย่าง:
     "C03": { status: "legal_review", owner: "ทีม CGR", updated: "2026-10-06" },
     "C05": { status: "draft", flag: "revise", note: "Legal ขอแก้ตัวอย่าง Email" },
   ========================================================================= */
window.GRC = window.GRC || {};

GRC.progress = {

};
