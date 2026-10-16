"""ตั้งหรือเปลี่ยนรหัสผ่านสำหรับแก้ไขสตอรีบอร์ด (สำหรับผู้ดูแลเท่านั้น — ทำบนเครื่อง ไม่ใช่บนหน้าเว็บ)

ใช้:  pip install cryptography
      python3 tools/set_editor_password.py
แล้ว commit + push ไฟล์ src/editor-key.json ขึ้น branch main

token: GitHub fine-grained token · Repository access เฉพาะ repo นี้ · Contents = Read and write
"""
import base64, getpass, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'editor-key.json')

def seal(token: str, password: str) -> dict:
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
    ct = AESGCM(key).encrypt(iv, token.encode(), None)  # ciphertext + tag (same layout as WebCrypto)
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b(salt), "iv": b(iv), "ct": b(ct)}

if __name__ == '__main__':
    token = os.environ.get('GIA_TOKEN') or getpass.getpass('GitHub token: ').strip()
    pw = os.environ.get('GIA_PASSWORD') or getpass.getpass('รหัสผ่านใหม่ (อย่างน้อย 12 ตัวอักษร): ')
    if not os.environ.get('GIA_PASSWORD') and getpass.getpass('ยืนยันรหัสผ่าน: ') != pw:
        sys.exit('รหัสผ่านทั้งสองครั้งไม่ตรงกัน')
    if len(pw) < 12:
        sys.exit('รหัสผ่านต้องยาวอย่างน้อย 12 ตัวอักษร')
    json.dump(seal(token, pw), open(OUT, 'w'), indent=1)
    print('บันทึกแล้ว:', os.path.normpath(OUT), '→ commit และ push ขึ้น main')
