/* =========================================================================
   core.js — data layer ที่ทุกหน้าใช้ร่วมกัน:
   รวมข้อมูลจาก data/*.js, คำนวณฟิลด์, วันเผยแพร่, สถานะ/ความล่าช้า,
   ตรวจความถูกต้องของข้อมูล และตัวช่วยสร้าง element/badge
   ========================================================================= */
(function (GRC) {
  "use strict";
  const C = GRC.config;
  const DAY = 864e5;

  /* ---------- helpers ---------- */
  GRC.el = function (tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null) continue;
      if (k === "style") e.style.cssText = v;
      else if (k === "text") e.textContent = v;
      else e.setAttribute(k, v);
    }
    kids.forEach(c => c != null && e.append(c));
    return e;
  };
  GRC.mmss = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  GRC.addDays = (date, n) => new Date(date.getTime() + n * DAY);
  GRC.daysBetween = (a, b) => Math.round((b - a) / DAY);
  GRC.fmtDate = d => d.toLocaleDateString("th-TH", { day: "numeric", month: "short", year: "2-digit" });

  // "วันนี้" — ทดสอบย้อนหลัง/ล่วงหน้าได้ด้วย ?today=2026-12-01
  GRC.today = (function () {
    const q = new URLSearchParams(location.search).get("today");
    const t = q ? new Date(q + "T00:00:00") : new Date();
    return new Date(t.getFullYear(), t.getMonth(), t.getDate());
  })();

  /* ---------- groups / categories ---------- */
  GRC.groupOf = cat => cat === C.assessCategory ? null : GRC.groups.find(g => g.cats.includes(cat));
  GRC.colorOf = cat => cat === C.assessCategory ? "var(--assess)" : `var(--${GRC.groupOf(cat).id})`;
  GRC.shortCat = cat => C.shortCat[cat] || cat;

  /* ---------- normalize episodes ----------
     ฟิลด์ที่คำนวณเพิ่ม: i, mi (เดือนในปีงบ 0=ต.ค.), fy, kind (main|micro|assess), dur, g,
     review (ต้องตรวจ Legal/Compliance), keyMsg, action, monthPub (วันเผยแพร่ Main ของเดือน), pub */
  GRC.episodes.forEach((d, i) => {
    d.i = i;
    const [mon, yr] = d.m.split(" ");
    d.mi = C.months.indexOf(mon);
    d.fy = d.mi <= 2 ? +yr : +yr - 1; // ปีงบตั้งชื่อตามปีที่เริ่ม: ต.ค. 2569 – ก.ย. 2570 = ปีงบ 2569
    d.kind = d.fmt.startsWith("Main") ? "main" : d.fmt.startsWith("Micro") ? "micro" : "assess";
    d.dur = (d.fmt.split("\n")[1] || "").trim();
    d.g = GRC.groupOf(d.cat)?.id || "assess";
    d.review = d.kind === "main" && /Legal|Compliance/.test(d.note);
    const k = d.key.split(/\n*แนวทางที่พนักงานควรทำ\s*:\s*\n?/);
    d.keyMsg = k[0].trim();
    d.action = (k[1] || "").trim();
    // วันเผยแพร่: วันจันทร์แรกของเดือน (W1), Micro +14 วัน (W3)
    const ce = +yr - 543, jsMonth = (d.mi + 9) % 12;
    const first = new Date(ce, jsMonth, 1);
    d.monthPub = GRC.addDays(first, (C.publishWeekday - first.getDay() + 7) % 7);
    d.pub = d.kind === "micro" ? GRC.addDays(d.monthPub, C.microOffsetDays) : d.monthPub;
  });

  GRC.byId = Object.fromEntries(GRC.episodes.map(d => [d.id, d]));
  GRC.clips = GRC.episodes.filter(d => d.kind !== "assess");
  GRC.mains = GRC.episodes.filter(d => d.kind === "main");
  GRC.fiscalYears = [...new Set(GRC.episodes.map(d => d.fy))];
  GRC.pairOf = d => GRC.episodes.find(x => x.m === d.m && x.kind === (d.kind === "main" ? "micro" : "main"));

  /* ---------- tracking ---------- */
  const mk = (list, toneOf) => Object.fromEntries(list.map((s, order) => [s.key, { ...s, order, tone: toneOf(s, order) }]));
  const CLIP_ST = mk(C.statuses, s => s.phase || "planned");
  const ASSESS_TONE = ["planned", "content", "content", "production", "production", "publish"];
  const ASSESS_ST = mk(C.assessStatuses, (s, i) => ASSESS_TONE[Math.min(i, ASSESS_TONE.length - 1)]);
  const FLAGS = Object.fromEntries(C.flags.map(f => [f.key, f]));
  GRC.clipStatuses = C.statuses.map(s => CLIP_ST[s.key]);
  GRC.assessStatuses = C.assessStatuses.map(s => ASSESS_ST[s.key]);

  GRC.trackOf = d => GRC.progress[d.id] || {};
  GRC.statusOf = d => {
    const map = d.kind === "assess" ? ASSESS_ST : CLIP_ST;
    return map[GRC.trackOf(d).status] || map[C.defaultStatus];
  };
  GRC.flagOf = d => FLAGS[GRC.trackOf(d).flag] || null;
  GRC.isDone = d => d.kind === "assess" ? GRC.statusOf(d).key === "reported" : GRC.statusOf(d).key === "published";

  // กำหนดเสร็จของขั้นปัจจุบัน (Micro เลื่อนขั้นเผยแพร่ไป W3)
  GRC.dueOf = d => {
    if (d.kind === "assess") return null;
    const s = GRC.statusOf(d);
    const shift = d.kind === "micro" && s.phase === "publish" ? C.microOffsetDays : 0;
    return GRC.addDays(d.monthPub, s.dueDays + shift);
  };
  // จำนวนวันที่ล่าช้า (0 = ไม่ล่าช้า); คลิปที่พักไว้หรือเผยแพร่แล้วไม่นับ
  GRC.lateDays = d => {
    if (d.kind === "assess" || GRC.isDone(d) || GRC.trackOf(d).flag === "hold") return 0;
    return Math.max(0, GRC.daysBetween(GRC.dueOf(d), GRC.today));
  };

  /* ---------- badges ---------- */
  GRC.statusBadge = d => {
    const s = GRC.statusOf(d);
    return GRC.el("span", { class: "status", style: `--st:var(--ph-${s.tone})`, text: s.label });
  };
  GRC.flagBadge = d => {
    const f = GRC.flagOf(d);
    return f ? GRC.el("span", { class: "flagb", style: `--st:var(--st-${f.tone})`, "data-icon": f.icon, text: f.label }) : null;
  };
  GRC.lateBadge = d => {
    const n = GRC.lateDays(d);
    return n ? GRC.el("span", { class: "flagb", style: "--st:var(--st-critical)", "data-icon": "⚠", text: `ล่าช้า ${n} วัน` }) : null;
  };

  /* ---------- validation (ดูผลใน DevTools → Console) ---------- */
  (function validate() {
    const warn = (...a) => console.warn("[GRC data]", ...a);
    const seen = new Set();
    GRC.episodes.forEach(d => {
      if (!d.id) warn("record ไม่มี id:", d.m, d.topic);
      else if (seen.has(d.id)) warn("id ซ้ำ:", d.id);
      seen.add(d.id);
      if (d.mi < 0) warn(d.id, "เดือนไม่ถูกต้อง:", d.m);
      if (d.cat !== C.assessCategory && !GRC.groupOf(d.cat)) warn(d.id, "หมวดไม่อยู่ในกลุ่มใด:", d.cat);
    });
    Object.entries(GRC.progress).forEach(([id, p]) => {
      const d = GRC.byId[id];
      if (!d) return warn("progress.js อ้าง id ที่ไม่มี:", id);
      const map = d.kind === "assess" ? ASSESS_ST : CLIP_ST;
      if (p.status && !map[p.status]) warn(id, "status ไม่รู้จัก:", p.status);
      if (p.flag && !FLAGS[p.flag]) warn(id, "flag ไม่รู้จัก:", p.flag);
    });
  })();
})(window.GRC);
