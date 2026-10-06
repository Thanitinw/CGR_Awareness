/* =========================================================================
   report.js — หน้า Report Progress: KPI, Timeline (Gantt), งานที่ต้องติดตาม,
   จำนวนคลิปต่อขั้น และสถานะ Assessment
   อ่านอย่างเดียวจาก data/progress.js — แผน/กำหนดเสร็จคำนวณใน core.js
   ========================================================================= */
(function (GRC) {
  "use strict";
  const { el, config: C } = GRC;
  const $ = id => document.getElementById(id);
  const CLIPS = GRC.clips, TODAY = GRC.today;
  const pct = (n, d) => d ? Math.round(n / d * 100) : 0;

  $("asof").textContent = "ข้อมูล ณ วันที่ " + TODAY.toLocaleDateString("th-TH", { day: "numeric", month: "long", year: "numeric" });

  /* ===================== KPIs ===================== */
  const done = CLIPS.filter(GRC.isDone);
  const active = CLIPS.filter(d => !GRC.isDone(d) && GRC.statusOf(d).key !== C.defaultStatus);
  const late = CLIPS.filter(d => GRC.lateDays(d) > 0);
  const flagged = CLIPS.filter(d => GRC.trackOf(d).flag === "revise");
  const next = CLIPS.filter(d => !GRC.isDone(d)).sort((a, b) => a.pub - b.pub)[0];
  [[`${done.length}/${CLIPS.length}`, "เผยแพร่แล้ว", `${pct(done.length, CLIPS.length)}% ของทั้งโครงการ`],
   [active.length, "กำลังดำเนินการ", "เริ่มแล้ว ยังไม่เผยแพร่"],
   [late.length, "ล่าช้ากว่าแผน", late.length ? "ดูรายการด้านล่าง" : "ไม่มีงานล่าช้า"],
   [flagged.length, "ต้องแก้ไข", "ถูกตีกลับ"],
   [next ? GRC.fmtDate(next.pub) : "–", "เผยแพร่ครั้งถัดไป", next ? `${next.id} · ${next.topic}` : "ครบทุกคลิปแล้ว"]]
    .forEach(([n, l, s]) => $("rkpi").append(el("div", { class: "kpi" }, el("b", { text: n }), el("span", { text: l }), el("small", { text: s }))));

  /* ===================== Tooltip ===================== */
  const tip = $("tip");
  function bindTip(node, html) {
    node.addEventListener("mouseenter", () => { tip.innerHTML = ""; tip.append(...html()); tip.hidden = false; });
    node.addEventListener("mousemove", e => {
      const x = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
      tip.style.left = x + "px"; tip.style.top = (e.clientY + 14) + "px";
    });
    node.addEventListener("mouseleave", () => { tip.hidden = true; });
  }

  /* ===================== Gantt ===================== */
  const PH = C.phases.map(p => ({ ...p, orders: GRC.clipStatuses.filter(s => s.phase === p.key).map(s => s.order) }));
  // ช่วงงานตามแผน (วันนับจากวันเผยแพร่ Main ของเดือน)
  const SPAN = { content: [-70, -35], production: [-35, -7], publish: [-7, C.microOffsetDays + 1] };

  const wStart = new Date(TODAY.getFullYear(), TODAY.getMonth() - 1, 1);
  const wEnd = new Date(TODAY.getFullYear(), TODAY.getMonth() + 5, 1);
  const total = wEnd - wStart;
  const pos = date => Math.max(0, Math.min(100, (date - wStart) / total * 100));

  const months = [...new Set(CLIPS.map(d => d.m))].map(m => CLIPS.filter(d => d.m === m))
    .filter(cs => GRC.addDays(cs[0].monthPub, SPAN.content[0]) < wEnd && GRC.addDays(cs[0].monthPub, SPAN.publish[1]) > wStart);

  const gantt = $("gantt");
  const monthTicks = [];
  for (let d = new Date(wStart); d < wEnd; d = new Date(d.getFullYear(), d.getMonth() + 1, 1)) monthTicks.push(d);
  const todayLine = withLabel => el("div", { class: "g-today", style: `left:${pos(TODAY)}%` }, withLabel ? el("span", { text: "วันนี้" }) : null);
  const ticks = withLabel => monthTicks.map(d => el("div", { class: "g-mo", style: `left:${pos(d)}%`,
    text: withLabel ? d.toLocaleDateString("th-TH", { month: "short", year: "2-digit" }) : null }));

  gantt.append(el("div", { class: "g-row head" }, el("div", { class: "g-lab", text: "เดือนเผยแพร่ / เรื่อง" }),
    el("div", { class: "g-track" }, ...ticks(true), todayLine(true)), el("div", { class: "g-st", text: "สถานะ" })));

  months.forEach(cs => {
    const main = cs.find(d => d.kind === "main") || cs[0], micro = cs.find(d => d.kind === "micro");
    const P = main.monthPub;
    const ords = cs.map(d => GRC.statusOf(d).order);
    const minO = Math.min(...ords), maxO = Math.max(...ords);
    const allDone = cs.every(GRC.isDone);
    const lateClips = cs.filter(d => GRC.lateDays(d) > 0);
    const latePhases = new Set(lateClips.map(d => GRC.statusOf(d).phase || "content"));

    const track = el("div", { class: "g-track" }, ...ticks(false));
    PH.forEach(ph => {
      const [a, b] = SPAN[ph.key];
      const s = GRC.addDays(P, a), e = GRC.addDays(P, b);
      if (e <= wStart || s >= wEnd) return;
      const lo = Math.min(...ph.orders), hi = Math.max(...ph.orders);
      const state = allDone || minO > hi ? "done" : (maxO >= lo && minO <= hi) ? "current" : "future";
      const stLabel = { done: "เสร็จแล้ว", current: "กำลังทำ", future: "ยังไม่ถึง" }[state];
      const isLate = state !== "done" && latePhases.has(ph.key);
      const bar = el("div", { class: `g-bar ${state}${isLate ? " late" : ""}`,
        style: `--ph:var(--ph-${ph.key});left:${pos(s)}%;width:${pos(e) - pos(s)}%`, "aria-label": `${main.m} ${ph.label} ${stLabel}` });
      bindTip(bar, () => [el("b", { text: `${main.m} · ${ph.label}` }),
        `ตามแผน ${GRC.fmtDate(s)} – ${GRC.fmtDate(GRC.addDays(e, -1))}`, el("br"), `สถานะช่วงนี้: ${stLabel}`,
        isLate ? el("br") : null, isLate ? "⚠ มีงานล่าช้าในช่วงนี้" : ""]);
      track.append(bar);
    });
    [main, micro].filter(Boolean).forEach(d => {
      if (d.pub < wStart || d.pub >= wEnd) return;
      const dot = el("div", { class: "g-pub", style: `left:${pos(d.pub)}%`, "aria-label": `${d.id} เผยแพร่ ${GRC.fmtDate(d.pub)}` });
      bindTip(dot, () => [el("b", { text: `${d.id} · ${d.kind === "main" ? "Main Story" : "Micro"}` }), `เผยแพร่ ${GRC.fmtDate(d.pub)}`, el("br"), GRC.statusOf(d).label]);
      track.append(dot);
    });
    track.append(todayLine(false));

    const st = el("div", { class: "g-st" });
    cs.forEach(d => st.append(el("span", {}, el("span", { class: "cid", text: (d.kind === "main" ? "Main " : "Micro ") }), GRC.statusBadge(d))));
    const worstLate = lateClips.sort((a, b) => GRC.lateDays(b) - GRC.lateDays(a))[0];
    if (worstLate) st.append(GRC.lateBadge(worstLate));
    cs.forEach(d => { const f = GRC.flagBadge(d); if (f) st.append(f); });

    gantt.append(el("div", { class: "g-row" },
      el("div", { class: "g-lab" }, el("b", { text: `${main.m} · ${cs.map(d => d.id).join(" / ")}` }),
        el("a", { href: `plan.html#${main.id}`, text: main.topic })),
      track, st));
  });

  const gl = $("glegend");
  C.phases.forEach(p => gl.append(el("span", {}, el("i", { style: `--ph:var(--ph-${p.key})` }), p.label)));
  gl.append(el("span", {}, el("i", { style: "--ph:var(--ph-content);background:repeating-linear-gradient(135deg,var(--ph) 0 6px,transparent 6px 10px)" }), "ลายทาง = กำลังทำ"),
    el("span", {}, el("i", { style: "--ph:var(--ph-content);opacity:.28" }), "จาง = ยังไม่ถึง"),
    el("span", {}, el("i", { style: "--ph:transparent;outline:2px solid var(--st-critical)" }), "⚠ กรอบแดง = ล่าช้า"),
    el("span", {}, "● วันเผยแพร่"), el("span", {}, "┆ วันนี้"));

  /* ===================== Watch list ===================== */
  const soon = GRC.addDays(TODAY, 28);
  const watch = CLIPS.filter(d => !GRC.isDone(d) &&
    (GRC.lateDays(d) > 0 || GRC.trackOf(d).flag || GRC.dueOf(d) <= soon))
    .sort((a, b) => GRC.lateDays(b) - GRC.lateDays(a) || GRC.dueOf(a) - GRC.dueOf(b));
  if (!watch.length) $("watch").append(el("p", { class: "empty", text: "ไม่มีงานล่าช้าหรือถึงกำหนดใน 4 สัปดาห์" }));
  else {
    const tb = el("tbody");
    watch.forEach(d => {
      const t = GRC.trackOf(d);
      tb.append(el("tr", {},
        el("td", { class: "num" }, el("a", { href: `plan.html#${d.id}`, text: d.id })),
        el("td", { class: "num", text: GRC.fmtDate(d.pub) }),
        el("td", { text: d.topic }),
        el("td", {}, GRC.statusBadge(d), " ", GRC.flagBadge(d), " ", GRC.lateBadge(d)),
        el("td", { class: "num", text: GRC.fmtDate(GRC.dueOf(d)) }),
        el("td", { text: t.owner || "–" }),
        el("td", { text: t.note || "" })));
    });
    $("watch").append(el("table", { class: "tt" },
      el("thead", {}, el("tr", {}, ...["รหัส", "เผยแพร่", "หัวข้อ", "สถานะ", "ขั้นนี้ควรเสร็จ", "ผู้รับผิดชอบ", "หมายเหตุ"].map(h => el("th", { text: h })))), tb));
  }

  /* ===================== Status distribution ===================== */
  let fy = "all";
  function drawDist() {
    const fb = $("sfy");
    fb.innerHTML = "";
    [["all", "ทั้ง 3 ปี"], ...GRC.fiscalYears.map(f => [f, `ปีงบ ${f}`])].forEach(([v, l]) => {
      const c = el("button", { class: "chip", "aria-pressed": String(fy === v), text: l });
      c.addEventListener("click", () => { fy = v; drawDist(); });
      fb.append(c);
    });
    const set = CLIPS.filter(d => fy === "all" || d.fy === fy);
    const box = $("sdist");
    box.innerHTML = "";
    const max = Math.max(1, ...GRC.clipStatuses.map(s => set.filter(d => GRC.statusOf(d).key === s.key).length));
    let lastPhase;
    GRC.clipStatuses.forEach(s => {
      if (s.phase !== lastPhase) {
        lastPhase = s.phase;
        const p = C.phases.find(x => x.key === s.phase);
        box.append(el("div", { class: "ph-head" }, el("span", { class: "sw", style: `background:var(--ph-${s.tone})` }), p ? p.label : "ยังไม่เริ่ม"));
      }
      const n = set.filter(d => GRC.statusOf(d).key === s.key).length;
      const row = el("div", { class: "sbar", style: `--st:var(--ph-${s.tone})` },
        el("span", {}, s.label, s.ifReview ? el("span", { class: "ph", text: " (เฉพาะ 9 เรื่อง)" }) : null),
        el("div", { class: "track" }, n ? el("div", { class: "fill", style: `width:${n / max * 100}%` }) : null),
        el("span", { class: "n", text: n }));
      bindTip(row, () => [el("b", { text: s.label }), `${n} คลิป · ${pct(n, set.length)}% ของ ${set.length} คลิป`]);
      box.append(row);
    });
    const fl = C.flags.map(f => `${f.icon} ${f.label} ${set.filter(d => GRC.trackOf(d).flag === f.key).length}`).join(" · ");
    box.append(el("p", { class: "note", text: `สถานะพิเศษ: ${fl} · ล่าช้า ${set.filter(d => GRC.lateDays(d) > 0).length}` }));
  }
  drawDist();

  /* ===================== Assessment ===================== */
  const tb = el("tbody");
  GRC.episodes.filter(d => d.kind === "assess").forEach(d => {
    const t = GRC.trackOf(d);
    tb.append(el("tr", {},
      el("td", { class: "num" }, el("a", { href: `plan.html#${d.id}`, text: d.id })),
      el("td", { text: d.m }),
      el("td", {}, GRC.statusBadge(d), " ", GRC.flagBadge(d)),
      el("td", { text: t.owner || "–" }),
      el("td", { text: t.note || "" })));
  });
  $("assess").append(el("table", { class: "tt" },
    el("thead", {}, el("tr", {}, ...["รหัส", "เดือน", "สถานะ", "ผู้รับผิดชอบ", "หมายเหตุ"].map(h => el("th", { text: h })))), tb));
})(window.GRC);
