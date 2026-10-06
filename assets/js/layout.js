/* =========================================================================
   layout.js — ส่วนหัว เมนู และส่วนท้ายที่ทุกหน้าใช้ร่วมกัน
   แต่ละหน้าใส่ <body data-page="..."> และ <div class="wrap"> ไว้ แล้วไฟล์นี้จะเติมให้
   เพิ่มหน้าใหม่: เพิ่มรายการใน PAGES แล้วสร้างไฟล์ html ตามแบบหน้าอื่น
   ========================================================================= */
(function (GRC) {
  "use strict";
  const { el } = GRC;

  const PAGES = [
    { key: "intro",  href: "index.html",  label: "Introduction" },
    { key: "plan",   href: "plan.html",   label: "Action Plan" },
    { key: "report", href: "report.html", label: "Report Progress" }
  ];

  const current = document.body.dataset.page;
  const wrap = document.querySelector(".wrap");

  const header = el("header", {},
    el("span", { class: "eyebrow", text: "CGR Awareness · แผนสื่อสาร 3 ปี" }),
    el("h1", { text: "GRC in Action" }),
    el("p", { class: "lead", text: "คลิปสั้นเล่าเป็นเรื่องราว ส่งถึงพนักงานในกลุ่มบริษัททุก 2 สัปดาห์ผ่าน YouTube และ LINE เพื่อให้ทุกคนรู้เรื่องพื้นฐานด้านธรรมาภิบาล ความเสี่ยง และการปฏิบัติตามกฎเกณฑ์ที่ควรรู้" }),
    el("span", { class: "period", text: "ต.ค. 2569 → ก.ย. 2572 · ทุก 2 สัปดาห์" }));

  const nav = el("nav", { class: "tabs", "aria-label": "เมนู" },
    ...PAGES.map(p => el("a", { class: "tab", href: p.href, "aria-current": p.key === current ? "page" : null, text: p.label })));

  wrap.prepend(header, nav);
  wrap.append(el("footer", { text: "ที่มา: GRC in Action – แผนสื่อสาร 3 ปี แบบทุก 2 สัปดาห์ (ต.ค. 2569 – ก.ย. 2572)" }));
})(window.GRC);
