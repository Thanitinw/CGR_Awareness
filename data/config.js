/* =========================================================================
   config.js — ค่าคงที่ของระบบ (เดือนปีงบ, รูปแบบคลิป, ขั้นตอนติดตามงาน)
   โหลดเป็นไฟล์แรก: ทุกไฟล์ใช้ namespace เดียวกันคือ window.GRC
   ========================================================================= */
window.GRC = window.GRC || {};

GRC.config = {
  // ลำดับเดือนในปีงบประมาณ (ต.ค. → ก.ย.)
  months: ["ต.ค.","พ.ย.","ธ.ค.","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย."],

  // ชื่อหมวดของกิจกรรมประเมินประจำปี (ไม่ใช่คลิป)
  assessCategory: "การประเมิน CGR Awareness ประจำปี",

  kinds: {
    main:   { label: "Main Story", week: "W1" },
    micro:  { label: "Micro",      week: "W3" },
    assess: { label: "Assessment", week: "พ.ย." }
  },

  // ชื่อหมวดแบบย่อ ใช้บนปฏิทิน
  shortCat: {
    "กฎหมายและการบริหารสัญญา":"กฎหมาย/สัญญา",
    "การต่อต้านการทุจริตคอร์รัปชัน":"ต่อต้านคอร์รัปชัน",
    "การทุจริตและการควบคุมภายใน":"ควบคุมภายใน",
    "ความขัดแย้งทางผลประโยชน์":"COI",
    "การแข่งขันทางการค้าอย่างเป็นธรรม":"แข่งขันเป็นธรรม",
    "การคุ้มครองข้อมูลส่วนบุคคล":"PDPA",
    "ความมั่นคงปลอดภัยสารสนเทศและ AI":"InfoSec & AI",
    "การแจ้งเบาะแสและข้อร้องเรียน":"แจ้งเบาะแส",
    "ทรัพย์สินทางปัญญา":"IP",
    "สิทธิมนุษยชน":"สิทธิมนุษยชน",
    "ข้อมูลภายในและการซื้อขายหลักทรัพย์":"Insider",
    "ความปลอดภัย อาชีวอนามัย และสภาพแวดล้อมการทำงาน":"OHS",
    "ธรรมาภิบาลและการตัดสินใจเชิงจริยธรรม":"ธรรมาภิบาล"
  },

  /* ---------- ติดตามความคืบหน้า ----------
     ช่วงงาน (phase) — สีอยู่ใน styles.css (--ph-<key>) */
  phases: [
    { key: "content",    label: "ช่วงเนื้อหา" },
    { key: "production", label: "ช่วงผลิต" },
    { key: "publish",    label: "ช่วงเผยแพร่" }
  ],

  /* ขั้นตอนของคลิป (data/progress.js → "status") เรียงตามลำดับงานจริง
     dueDays  = ต้องทำขั้นนี้ "เสร็จ" ก่อนวันเผยแพร่ Main Story ของเดือนกี่วัน (ลบ = ก่อน)
                ใช้คำนวณแผนและหาคลิปล่าช้า — ปรับตามความเร็วจริงของทีม
     ifReview = ใช้เฉพาะเรื่องที่หมายเหตุระบุว่าต้องตรวจ Legal/Compliance (เรื่องอื่นข้ามขั้นนี้) */
  statuses: [
    { key: "planned",        label: "วางแผน",               phase: null,         dueDays: -70 },
    { key: "draft",          label: "Draft Script",          phase: "content",    dueDays: -56 },
    { key: "content_review", label: "ตรวจเนื้อหา",           phase: "content",    dueDays: -42 },
    { key: "legal_review",   label: "ตรวจ Legal/Compliance", phase: "content",    dueDays: -42, ifReview: true },
    { key: "final",          label: "Final Script",          phase: "content",    dueDays: -35 },
    { key: "shooting",       label: "ถ่ายทำ",                phase: "production", dueDays: -21 },
    { key: "editing",        label: "ตัดต่อ",                 phase: "production", dueDays: -10 },
    { key: "vdo_approval",   label: "Approve VDO",           phase: "production", dueDays: -7 },
    { key: "ready",          label: "พร้อมเผยแพร่",           phase: "publish",    dueDays: -3 },
    { key: "published",      label: "เผยแพร่แล้ว",            phase: "publish",    dueDays: 0 }
  ],
  defaultStatus: "planned",

  /* สถานะพิเศษ ใช้คู่กับ status ได้ทุกขั้น (progress.js → "flag") */
  flags: [
    { key: "revise", label: "ต้องแก้ไข",     icon: "↺", tone: "critical" },
    { key: "hold",   label: "พักไว้/เลื่อน", icon: "⏸", tone: "hold" }
  ],

  /* ขั้นตอนของ CGR Awareness Assessment (ไม่ใช่วิดีโอ จึงใช้ชุดแยก) */
  assessStatuses: [
    { key: "planned",  label: "วางแผน" },
    { key: "prep",     label: "เตรียมข้อสอบ" },
    { key: "review",   label: "ตรวจข้อสอบ" },
    { key: "open",     label: "เปิดทำแบบประเมิน" },
    { key: "closed",   label: "ปิดรับ" },
    { key: "reported", label: "สรุปผลแล้ว" }
  ],

  /* วันเผยแพร่: สัปดาห์ที่ 1 = วันจันทร์แรกของเดือน, สัปดาห์ที่ 3 = +14 วัน
     (0=อาทิตย์ 1=จันทร์ … 6=เสาร์) */
  publishWeekday: 1,
  microOffsetDays: 14
};
