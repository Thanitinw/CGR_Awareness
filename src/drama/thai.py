"""review 23 ต.ค. 2569: every spoken line in Thai — English words become Thai (or Thai spelling); acronyms stay (AI, NDA, DPO ...)."""
THAI = [
 ('Human Rights Red Flag', 'สัญญาณเตือนด้านสิทธิมนุษยชน'), ('Red Flag', 'สัญญาณเตือน'),
 (' หรือ Subject to Contract', ''), ('Privacy Notice', 'ประกาศความเป็นส่วนตัว'), ('ข้อ Notice', 'ข้อการแจ้งในสัญญา'), ('Notice', 'การแจ้งในสัญญา'),
 ('Public AI', 'AI สาธารณะ'), ('Data Owner', 'เจ้าของข้อมูล'), ('Data Minimization', 'การใช้ข้อมูลเท่าที่จำเป็น'),
 ('Need-to-know คือให้เฉพาะคนที่ต้องรู้ Least Privilege คือให้สิทธิ์เท่าที่จำเป็น', 'หลักคือให้เฉพาะคนที่ต้องรู้ และให้สิทธิ์เท่าที่จำเป็น'),
 ('Public เปิดได้ Internal ใช้ภายใน Confidential เฉพาะคนเกี่ยวข้อง Restricted เฉพาะคนที่ได้รับอนุญาต', 'เปิดเผยได้ ใช้ภายใน ลับเฉพาะคนเกี่ยวข้อง และลับมากเฉพาะคนที่ได้รับอนุญาต'),
 ('ระดับ Confidential', 'ระดับลับ'), ('Management Override', 'การที่ผู้บริหารข้ามการควบคุม'), ('Inside Information', 'ข้อมูลภายใน'), ('Retaliation', 'การตอบโต้คนแจ้ง'),
 ('Risk Register', 'ทะเบียนความเสี่ยง'), ('Near Miss', 'เหตุเกือบเกิด'), ('Carbon Neutral', 'คาร์บอนนิวทรัล'), ('Success Fee', 'ค่าตอบแทนตามผลสำเร็จ'),
 ('Short Sale', 'ชอร์ตเซล'), ('Scope Creep', 'งานงอก'), ('Use Case', 'กรณีใช้งาน'), ('Incident Report', 'รายงานเหตุ'),
 ('Supplier Engineer', 'วิศวกรซัพพลายเออร์'), ('Supplier', 'ซัพพลายเออร์'), ('Vendor', 'เวนเดอร์'), ('Email', 'อีเมล'), ('ฝ่าย Compliance', 'ฝ่ายคอมพลายแอนซ์'), ('Compliance', 'ฝ่ายคอมพลายแอนซ์'),
 ('Invoice', 'ใบแจ้งหนี้'), ('Sponsor', 'สปอนเซอร์'), ('ลงทะเบียน Warranty', 'ลงทะเบียนรับประกัน'), ('ฟอร์ม Warranty', 'ฟอร์มรับประกัน'), ('Warranty', 'การรับประกัน'),
 ('Notebook', 'โน้ตบุ๊ก'), ('Copy', 'ก๊อปปี้'), ('Actual', 'ตัวเลขจริง'), ('Forecast', 'ประมาณการ'), ('Library', 'ไลบรารี'), ('Template', 'เทมเพลต'),
 ('Benchmark', 'เบนช์มาร์ก'), ('บัญชี Margin', 'บัญชีมาร์จิน'), ('Margin', 'มาร์จิน'), ('Consultant', 'ที่ปรึกษา'), ('Requirement', 'ข้อกำหนด'), ('Review', 'รีวิว'),
 ('Rating', 'ผลประเมิน'), ('Software', 'ซอฟต์แวร์'), ('Algorithm', 'อัลกอริทึม'), ('Campaign', 'แคมเปญ'), ('Promotion', 'โปรโมชัน'), ('Bug', 'บั๊ก'),
 ('Progress', 'ความคืบหน้า'), ('Complaint', 'เรื่องร้องเรียน'), ('Risk', 'ความเสี่ยง'), ('Server', 'เซิร์ฟเวอร์'), ('Test', 'เทสต์'), ('Remote', 'รีโมต'),
 ('คู่มือ Training', 'คู่มืออบรม'), ('Training', 'อบรม'), ('Flash Drive', 'แฟลชไดรฟ์'), ('Drive', 'ไดรฟ์'), ('Greenwashing', 'การฟอกเขียว'), ('Deepfake', 'ดีปเฟก'),
 ('Phishing', 'ฟิชชิง'), ('Tender', 'งานประมูล'), ('ใส่ Red', 'ใส่สีแดง'), ('เข้า Red', 'เข้าสีแดง'), ('LINE', 'ไลน์'), ('IT', 'ไอที'),
]
