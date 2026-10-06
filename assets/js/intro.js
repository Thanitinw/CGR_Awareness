/* =========================================================================
   intro.js — หน้า Introduction: KPI และการ์ดกลุ่มเนื้อหา
   ========================================================================= */
(function (GRC) {
  "use strict";
  const { el } = GRC;
  const $ = id => document.getElementById(id);
  const DATA = GRC.episodes, CLIPS = GRC.clips, MAINS = GRC.mains;

  // ลิงก์เก่าแบบแท็บ (index.html#plan) → ไปหน้าใหม่
  if (/^#(plan|scripts)$/.test(location.hash)) { location.replace("plan.html"); return; }

  [[CLIPS.length, "คลิปตลอด 3 ปี"], [MAINS.length + " + " + (CLIPS.length - MAINS.length), "Main Story + Micro"],
   [24, "คลิปต่อปี (ทุก 2 สัปดาห์)"], [DATA.filter(d => d.kind === "assess").length, "รอบ CGR Awareness Assessment"]]
    .forEach(([n, l]) => $("kpis").append(el("div", { class: "kpi" }, el("b", { text: n }), el("span", { text: l }))));
  $("rv").textContent = MAINS.filter(d => d.review).length;

  // one card per group: what it protects, Code of Conduct EP link, references
  const max = Math.max(...GRC.groups.flatMap(g => g.cats.map(c => MAINS.filter(d => d.cat === c).length)));
  GRC.groups.forEach(g => {
    const tot = MAINS.filter(d => d.g === g.id).length;
    const box = el("div", { class: "group", style: `--c:var(--${g.id})` },
      el("h3", {}, el("span", { class: "sw", style: `background:var(--${g.id})` }), g.name),
      el("p", { class: "gmeta num", text: `${tot} เรื่อง · ${Math.round(tot / MAINS.length * 100)}% ของทั้งหมด` }),
      el("p", { class: "gprot" }, el("b", { text: "ปกป้อง: " }), g.protects));
    g.cats.map(c => [c, MAINS.filter(d => d.cat === c).length]).sort((a, b) => b[1] - a[1]).forEach(([c, n]) =>
      box.append(el("div", { class: "bar-row" }, el("span", { text: c }),
        el("div", { class: "track" }, el("div", { class: "fill", style: `width:${n / max * 100}%;background:var(--${g.id})` })),
        el("span", { class: "n", text: n }))));
    box.append(el("p", { class: "gep", text: "คู่มือจรรยาบรรณ: " + g.ep }));
    const ul = el("ul", { class: "grefs" });
    g.refs.forEach(r => ul.append(el("li", { text: r })));
    box.append(el("details", { class: "gref" }, el("summary", { text: "อ้างอิง (" + g.refs.length + ")" }), ul));
    $("cats").append(box);
  });
})(window.GRC);
