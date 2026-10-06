/* =========================================================================
   plan.js — หน้า Action Plan: ปฏิทิน รายการคลิป และหน้าต่างสคริปต์
   ลิงก์ตรงไปคลิป: plan.html#C05 (เปิดสคริปต์) / plan.html#AS-2569 (เปิดแถว)
   ========================================================================= */
(function (GRC) {
  "use strict";
  const { el, config: C } = GRC;
  const DATA = GRC.episodes, CLIPS = GRC.clips, FYS = GRC.fiscalYears;
  const $ = id => document.getElementById(id);
  const KIND = { main: "Main Story", micro: "Micro", assess: "Assessment" };

  /* ===================== Calendar + register ===================== */
  const lg = $("legend");
  GRC.groups.forEach(g => lg.append(el("span", {}, el("span", { class: "sw", style: `background:var(--${g.id})` }), g.name)));
  lg.append(el("span", {}, el("span", { class: "sw", style: "background:transparent;border:1px dashed var(--assess)" }), "CGR Awareness Assessment"));

  const state = { year: "all", group: "all", fmt: "all" };

  // calendar: one block per fiscal year, explicit month + year on every row
  function drawCal() {
    const cal = $("cal");
    cal.innerHTML = "";
    FYS.filter(fy => state.year === "all" || fy === state.year).forEach(fy => {
      const blk = el("div", { class: "yr" });
      blk.append(el("div", { class: "yr-h" }, el("b", { text: `ปีงบประมาณ ${fy}` }), el("span", { text: `ต.ค. ${fy} – ก.ย. ${fy + 1} · 24 คลิป` })));
      blk.append(el("div", { class: "tl-head" }, el("div", { text: "เดือน / ปี" }),
        el("div", {}, el("b", { text: "สัปดาห์ที่ 1" }), "Main Story · ประมาณ 2 นาที"),
        el("div", {}, el("b", { text: "สัปดาห์ที่ 3" }), "Micro Reinforcement · ไม่เกิน 1 นาที")));
      C.months.forEach((m, mi) => {
        const items = DATA.filter(d => d.fy === fy && d.mi === mi);
        if (!items.length) return;
        const yr = mi <= 2 ? fy : fy + 1;
        const date = el("div", { class: "tl-date" }, el("span", { class: "mm", text: m }), el("span", { class: "yy", text: String(yr) }));
        const as = items.find(d => d.kind === "assess");
        if (as) {
          const b = el("button", { class: "as", text: "CGR Awareness Assessment" });
          b.addEventListener("click", () => openRow(as));
          date.append(b);
        }
        const row = el("div", { class: "tl-row" }, date);
        ["main", "micro"].forEach(k => {
          const d = items.find(x => x.kind === k);
          const cell = el("div", { class: "tl-cell" });
          if (d) {
            const b = el("button", { class: "clip " + k, style: `--c:${GRC.colorOf(d.cat)}`, "data-g": d.g, "data-k": k,
              "aria-label": `${m} ${yr} ${KIND[k]} ${d.topic}` },
              el("span", { class: "wkl", text: k === "main" ? "สัปดาห์ที่ 1 · Main Story" : "สัปดาห์ที่ 3 · Micro" }),
              el("span", { class: "ct" }, d.fmt.includes("เปิดตัว") ? "คลิปเปิดตัว · ไม่เกิน 3 นาที" : GRC.shortCat(d.cat),
                GRC.statusBadge(d), GRC.flagBadge(d), GRC.lateBadge(d)),
              el("span", { text: d.topic }));
            b.addEventListener("click", () => showScript(d.i));
            cell.append(b);
          }
          row.append(cell);
        });
        blk.append(row);
      });
      cal.append(blk);
    });
  }

  function chips(id, opts, key) {
    const box = $(id);
    box.innerHTML = "";
    opts.forEach(([v, label, col]) => {
      const c = el("button", { class: "chip", "aria-pressed": String(state[key] === v) },
        col ? el("span", { class: "sw", style: `background:${col}` }) : null, label);
      c.addEventListener("click", () => { state[key] = v; render(); });
      box.append(c);
    });
  }
  const yl = (a, b) => el("span", { class: "yl" }, el("b", { text: a }), el("small", { text: b }));

  function render() {
    chips("yearf", [["all", yl("ทั้ง 3 ปี", `ต.ค. ${FYS[0]} – ก.ย. ${FYS[FYS.length - 1] + 1}`)],
      ...FYS.map(f => [f, yl(`ปีงบ ${f}`, `ต.ค. ${f} – ก.ย. ${f + 1}`)])], "year");
    chips("fmtf", [["all", "ทุกรูปแบบ"], ["main", "Main Story (W1)"], ["micro", "Micro Reinforcement (W3)"], ["assess", "Assessment"]], "fmt");
    chips("groupf", [["all", "ทุกกลุ่ม"], ...GRC.groups.map(g => [g.id, g.name, `var(--${g.id})`])], "group");

    const list = $("list");
    list.innerHTML = "";
    const rows = DATA.filter(d => (state.year === "all" || d.fy === state.year) &&
      (state.fmt === "all" || d.kind === state.fmt) && (state.group === "all" || d.g === state.group));
    rows.forEach(d => {
      const s = el("summary", { style: `--c:${GRC.colorOf(d.cat)}` },
        el("span", { class: "m" }, d.m, el("small", { text: d.slot })),
        el("span", { class: "stripe" }),
        el("span", { class: "t" }, el("small", { text: d.cat }), d.topic),
        el("span", { class: "tags" },
          el("span", { class: "fmt " + d.kind, text: d.kind === "assess" ? "Assessment" : `${KIND[d.kind]} · ${d.dur}` }),
          el("span", {}, el("span", { class: "cid", text: d.id + " · " }), GRC.statusBadge(d)),
          GRC.flagBadge(d), GRC.lateBadge(d)));
      const cols = [el("div", {}, el("h4", { text: d.kind === "micro" ? "Micro Reminder" : "Key Message / Red Flag" }), el("p", { text: d.keyMsg || "–" }))];
      if (d.action) cols.push(el("div", {}, el("h4", { text: "สิ่งที่พนักงานควรทำ" }), el("p", { text: d.action })));
      const last = el("div", {}, el("h4", { text: "หมายเหตุก่อนผลิต" }), el("p", { text: d.note || "–" }));
      if (d.kind !== "assess") {
        const b = el("button", { class: "to-script", text: "อ่านสคริปต์ →" });
        b.addEventListener("click", () => showScript(d.i));
        last.append(b);
      }
      cols.push(last);
      list.append(el("details", { id: "ep-" + d.id }, s,
        el("div", { class: "body", style: cols.length === 2 ? "grid-template-columns:2fr 1fr" : null }, ...cols)));
    });
    if (!rows.length) list.append(el("div", { class: "empty", text: "ไม่มีคลิปในตัวกรองนี้" }));

    drawCal();
    document.querySelectorAll(".clip").forEach(b => b.classList.toggle("dim",
      (state.group !== "all" && b.dataset.g !== state.group) || (state.fmt !== "all" && b.dataset.k !== state.fmt)));
  }

  function openRow(d) {
    Object.assign(state, { year: "all", group: "all", fmt: "all" });
    render();
    const det = $("ep-" + d.id);
    det.open = true;
    det.scrollIntoView({ block: "start" });
    det.querySelector("summary").focus({ preventScroll: true });
  }

  /* ===================== Script modal ===================== */
  const dlg = $("dlg"), sheet = $("sheet");

  function parseStory(s) {
    return s.split("\n").map(l => {
      const k = l.indexOf(":");
      return k > 0 && k < 30 ? [l.slice(0, k).trim(), l.slice(k + 1).trim()] : ["", l.trim()];
    }).filter(x => x[1]);
  }

  // script format: "[0:00–0:08 | cue]" lines, then "ผู้พูด: ข้อความ" lines
  function renderScript(s) {
    const box = el("div", { class: "script" });
    let cur = null, curWho = null;
    s.split("\n").forEach(raw => {
      const l = raw.trim();
      if (!l) { cur = null; curWho = null; return; }
      const cue = l.match(/^\[(.+)\]$/);
      if (cue) {
        const p = cue[1].split(" | ");
        box.append(el("div", { class: "cue" }, p.length > 1 ? el("span", { class: "tc", text: p[0] }) : null, el("span", { text: p[p.length - 1] })));
        cur = null; curWho = null;
        return;
      }
      const sp = l.match(/^([^:“"\[]{1,40}):\s*(.*)$/);
      let who = curWho, text = l;
      if (sp) { who = sp[1].trim(); text = sp[2]; }
      if (!cur || who !== curWho) {
        const kind = who === "ข้อความบนจอ" ? "scr" : who === "ฉาก" ? "dir" : (!who || who.includes("ผู้บรรยาย")) ? "nar" : "dia";
        cur = el("div", { class: "line " + kind }, el("span", { class: "who", text: who === "ข้อความบนจอ" ? "บนจอ" : who || "" }), el("div", { class: "say" }));
        box.append(cur);
        curWho = who;
      }
      if (text) {
        const say = cur.querySelector(".say"), last = say.lastElementChild;
        const list = /^[⚑✓]/.test(text) || who === "ข้อความบนจอ";
        if (last && !list && !last.dataset.list) last.textContent += " " + text;
        else { const p = el("p", { text }); if (list) p.dataset.list = "1"; say.append(p); }
      }
    });
    return box;
  }

  // tracking box — plan dates are computed; other fields show only if present in progress.js
  function trackBox(d) {
    const t = GRC.trackOf(d);
    const cell = (h, ...v) => el("div", {}, el("h4", { text: h }), ...v);
    const items = [cell("สถานะ", GRC.statusBadge(d), GRC.flagBadge(d), GRC.lateBadge(d)),
      cell("วันเผยแพร่ตามแผน", el("span", { class: "num", text: GRC.fmtDate(d.pub) }))];
    if (!GRC.isDone(d)) items.push(cell("ขั้นนี้ควรเสร็จภายใน", el("span", { class: "num", text: GRC.fmtDate(GRC.dueOf(d)) })));
    if (t.owner) items.push(cell("ผู้รับผิดชอบ", el("span", { text: t.owner })));
    if (t.publishedAt) items.push(cell("เผยแพร่จริง", el("span", { class: "num", text: GRC.fmtDate(new Date(t.publishedAt + "T00:00:00")) })));
    if (t.scriptUrl) items.push(cell("ไฟล์สคริปต์", el("a", { href: t.scriptUrl, target: "_blank", rel: "noopener", text: "เปิดไฟล์ ↗" })));
    if (t.youtube) items.push(cell("YouTube", el("a", { href: t.youtube, target: "_blank", rel: "noopener", text: "เปิดคลิป ↗" })));
    if (t.views != null) items.push(cell("ยอดวิว", el("span", { class: "num", text: Number(t.views).toLocaleString("th-TH") })));
    if (t.avgWatchSec != null) items.push(cell("เวลาดูเฉลี่ย", el("span", { class: "num", text: GRC.mmss(t.avgWatchSec) })));
    if (t.note) items.push(cell("หมายเหตุติดตาม", el("span", { text: t.note })));
    return el("div", { class: "track-box" }, ...items);
  }

  function showScript(i) {
    const d = DATA[i];
    const idx = CLIPS.findIndex(x => x.i === i);
    sheet.innerHTML = "";
    sheet.style.setProperty("--c", GRC.colorOf(d.cat));

    let storyEl;
    if (d.kind === "main") {
      storyEl = el("div", { class: "story" });
      parseStory(d.story).forEach(([k, v]) => storyEl.append(el("div", {}, el("h4", { text: k || "ฉาก" }), el("span", { text: v }))));
    } else {
      storyEl = el("div", { class: "hook" }, el("h4", { text: "Hook / ภาพประกอบ" }), el("span", { text: d.story }));
    }

    const p = GRC.pairOf(d);
    let pairEl = null;
    if (p) {
      const b = el("button", { text: p.topic });
      b.addEventListener("click", () => showScript(p.i));
      pairEl = el("p", { class: "pair" }, d.kind === "main" ? "คลิปต่อยอดในสัปดาห์ที่ 3: " : "ต่อยอดจาก Main Story: ", b);
    }

    const side = d.action
      ? el("div", { class: "side" },
          el("div", {}, el("h4", { text: "Key Message / Red Flag" }), el("p", { text: d.keyMsg })),
          el("div", {}, el("h4", { text: "สิ่งที่พนักงานควรทำ" }), el("p", { text: d.action })),
          el("div", {}, el("h4", { text: "หมายเหตุก่อนผลิต" }), el("p", { text: d.note })))
      : el("div", { class: "side two" },
          el("div", {}, el("h4", { text: "Micro Reminder" }), el("p", { text: d.keyMsg })),
          el("div", {}, el("h4", { text: "หมายเหตุก่อนผลิต" }), el("p", { text: d.note })));

    const prev = el("button", { text: "← คลิปก่อนหน้า" }), next = el("button", { text: "คลิปถัดไป →" });
    prev.disabled = idx === 0;
    next.disabled = idx === CLIPS.length - 1;
    prev.addEventListener("click", () => showScript(CLIPS[idx - 1].i));
    next.addEventListener("click", () => showScript(CLIPS[idx + 1].i));

    sheet.append(
      el("div", { class: "sheet-head" },
        el("div", { class: "meta" },
          el("span", { class: "fmt " + d.kind, text: `${KIND[d.kind]} · ${d.dur}` }),
          d.est ? el("span", { class: "num est", text: `ยาวประมาณ ${GRC.mmss(d.est)} นาที` }) : null,
          el("span", { class: "num", text: `${d.id} · คลิป ${idx + 1} / ${CLIPS.length} · ${d.m} ${d.slot}` }),
          el("span", { class: "pill", text: d.cat }),
          d.review ? el("span", { class: "flag", text: "ตรวจถ้อยคำก่อนผลิต" }) : null),
        el("h2", { id: "dlg-title", text: d.topic }), pairEl),
      trackBox(d), storyEl, renderScript(d.script), side, el("div", { class: "pager" }, prev, next));

    if (!dlg.open) { try { dlg.showModal(); } catch (e) { dlg.setAttribute("open", ""); } }
    dlg.scrollTop = 0;
  }
  dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
  $("dlg-x").addEventListener("click", () => dlg.close());

  /* ===================== Boot ===================== */
  render();
  function openFromHash() {
    const d = GRC.byId[decodeURIComponent(location.hash.slice(1))];
    if (!d) return;
    if (d.kind === "assess") openRow(d); else showScript(d.i);
  }
  openFromHash();
  window.addEventListener("hashchange", openFromHash);
})(window.GRC);
