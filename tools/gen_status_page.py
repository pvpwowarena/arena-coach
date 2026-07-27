#!/usr/bin/env python3
"""Сгенерировать живую страницу статуса проекта → status.html.

Собирает в одну самодостаточную HTML-страницу (RU, тёмная):
  • живой индикатор прода (client-side fetch /health, автообновление);
  • % готовности к запуску — чеклист из docs/prod-status.json (правится руками в репо);
  • % покрытия вариаций по бракетам (2v2 / 3v3 / 5v5): KB-драфты + advice-сиды;
  • карточки наших составов и матрицы покрытия по всем класс-комбинациям врагов.

Источники данных: kb/drafts, kb/hypotheses, kb/matchups, kb/compositions.json,
tools/advice_seed.json, docs/prod-status.json, git HEAD. Всё пересчитывается
на каждом запуске — страница пересобирается в vps-deploy.sh при каждом деплое
(т.е. при каждом push в main) и кладётся в /var/www/arena-coach/status.html.

Локальный превью:  python tools/gen_status_page.py -o /tmp/status.html
Stdlib only, Python 3.10+. Переиспользует логику tools/coverage_matrix.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import itertools
import json
import subprocess
from pathlib import Path

import coverage_matrix as cm  # same-dir import (tools/)

REPO = cm.REPO
RU_CLASS = {
    "warrior": "Вар",
    "paladin": "Пал",
    "hunter": "Хант",
    "rogue": "Рога",
    "priest": "Прист",
    "shaman": "Шам",
    "mage": "Маг",
    "warlock": "Лок",
    "druid": "Друид",
}
CLASS_COLOR = {
    "Вар": "#C79C6E",
    "Пал": "#F58CBA",
    "Хант": "#ABD473",
    "Рога": "#FFF569",
    "Прист": "#FFFFFF",
    "Шам": "#0070DE",
    "Маг": "#69CCF0",
    "Лок": "#9482C9",
    "Друид": "#FF7D0A",
}
# Прозвища класс-комбинаций 3v3 (ключ — sorted classkey)
NICK3 = {
    ("druid", "warlock", "warrior"): "WLD",
    ("priest", "rogue", "warlock"): "RLP",
    ("druid", "rogue", "warlock"): "RLD",
    ("mage", "priest", "rogue"): "RMP (зеркало)",
    ("mage", "priest", "warlock"): "MLP",
    ("priest", "shaman", "warlock"): "Shadowplay",
    ("mage", "priest", "shaman"): "Маг+Прист+РШам (даблхил)",
    ("mage", "priest", "warrior"): "WMP",
    ("druid", "hunter", "priest"): "Хант+Дисц+Друид",
}
NICK_OUR = {
    ("druid", "mage", "rogue"): "RMD",
    ("druid", "rogue", "warlock"): "RLD",
}
GLYPH = {"kb": "✓", "hyp": "Г", "adv": "А", "todo": "·"}
TIER_RU = {
    "kb": "KB-драфт (sourced, идёт игрокам)",
    "hyp": "гипотеза (карантин, игрокам не идёт)",
    "adv": "advice-сид (офлайн-разбор из кэша советов)",
    "todo": "нет покрытия",
}


def ru_key(classkey: tuple[str, ...]) -> str:
    return "+".join(RU_CLASS[c] for c in classkey)


def chips(classkey_or_names) -> str:
    names = [RU_CLASS.get(c, c) for c in classkey_or_names]
    return "".join(
        f'<span class="chip"><i style="background:{CLASS_COLOR[n]}"></i>{n}</span>' for n in names
    )


def load_advice() -> tuple[dict, dict]:
    """({(bracket, our_classkey): set(enemy_classkey)}, {(bracket, our_classkey): n_seeds})."""
    path = REPO / "tools" / "advice_seed.json"
    cover: dict = {}
    counts: dict = {}
    if not path.is_file():
        return cover, counts
    for seed in json.loads(path.read_text(encoding="utf-8")):
        our = cm._classkey(seed["our"])
        enemy = tuple(sorted(c.lower() for c, _spec in seed.get("enemies", [])))
        key = (seed.get("bracket", "?"), our)
        cover.setdefault(key, set()).add(enemy)
        counts[key] = counts.get(key, 0) + 1
    return cover, counts


def git_info() -> tuple[str, str]:
    try:
        head = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        date = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%cs"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        return head or "n/a", date or ""
    except Exception:  # noqa: BLE001 — страница важнее причины (нет git и т.п.)
        return "n/a", ""


def cell_html(comp_label: str, enemy_label: str, tiers: list[str]) -> str:
    primary = tiers[0] if tiers else "todo"
    tip = f"{comp_label} vs {enemy_label} · " + (
        " + ".join(TIER_RU[t] for t in tiers) if tiers else TIER_RU["todo"]
    )
    return f'<td><span class="cl {primary}" data-tip="{html.escape(tip, quote=True)}">{GLYPH[primary]}</span></td>'


def bracket_matrix(size: int, ours: list, sourced, hypo, adv_cover, bracket: str):
    """Строки матрицы + агрегаты. ours: [(slug, label)]."""
    enemies = list(itertools.combinations_with_replacement(cm.CLASSES, size))
    rows = []
    totals = {lbl: {"kb": 0, "hyp": 0, "adv": 0, "todo": 0, "live": 0} for _, lbl in ours}
    prev_first = None
    for enemy in enemies:
        key = tuple(sorted(enemy))
        label = ru_key(enemy)
        first = RU_CLASS[enemy[0]]
        if first != prev_first:
            ncols = len(ours) + 1
            rows.append(
                f'<tr class="grp"><td colspan="{ncols}">'
                f'<i style="background:{CLASS_COLOR[first]}"></i>{first} + …</td></tr>'
            )
            prev_first = first
        cells = []
        for slug, lbl in ours:
            ok = cm._classkey(slug)
            tiers = []
            if (ok, key) in sourced:
                tiers.append("kb")
            if (ok, key) in hypo:
                tiers.append("hyp")
            if key in adv_cover.get((bracket, ok), set()):
                tiers.append("adv")
            totals[lbl][tiers[0] if tiers else "todo"] += 1
            # «живая» ячейка = бот реально ответит: sourced-драфт ИЛИ advice-сид
            # (гипотеза сама по себе игрокам не идёт, но advice поверх неё — идёт)
            if "kb" in tiers or "adv" in tiers:
                totals[lbl]["live"] += 1
            cells.append(cell_html(lbl, label, tiers))
        rows.append(f"<tr><th>{label}</th>{''.join(cells)}</tr>")
    return rows, totals, len(enemies)


def matrix_3v3_covered(ours, sourced, hypo, adv_cover):
    """Компактная матрица 3v3: только покрытые тройки (полная — простыня из 165)."""
    covered: set = set()
    for slug, _lbl in ours:
        ok = cm._classkey(slug)
        covered |= {e for o, e in sourced if o == ok} | {e for o, e in hypo if o == ok}
        covered |= adv_cover.get(("3v3", ok), set())
    rows = []
    for key in sorted(covered, key=lambda k: (NICK3.get(k) is None, [cm.CLASSES.index(c) for c in k])):
        nick = NICK3.get(key)
        label = nick or ru_key(key)
        sub = f"<small>{ru_key(key)}</small>" if nick else ""
        cells = []
        for slug, lbl in ours:
            ok = cm._classkey(slug)
            tiers = []
            if (ok, key) in sourced:
                tiers.append("kb")
            if (ok, key) in hypo:
                tiers.append("hyp")
            if key in adv_cover.get(("3v3", ok), set()):
                tiers.append("adv")
            cells.append(cell_html(lbl, label, tiers))
        rows.append(f"<tr><th>{label}{sub}</th>{''.join(cells)}</tr>")
    return rows, len(covered)


def bar(covered_pct: float, kb_pct: float) -> str:
    """Двухслойный прогресс-бар: зелёный KB + синий advice поверх."""
    return (
        '<div class="bar">'
        f'<i class="b-adv" style="width:{covered_pct:.1f}%"></i>'
        f'<i class="b-kb" style="width:{kb_pct:.1f}%"></i>'
        "</div>"
    )


def pct(a: int, b: int) -> float:
    return 100.0 * a / b if b else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", default="status.html", help="куда писать HTML")
    args = ap.parse_args()

    sourced = cm._scan(cm.DRAFTS)
    hypo = cm._scan(cm.HYPO)
    sourced_exact = cm._scan_exact(cm.DRAFTS)
    hypo_exact = cm._scan_exact(cm.HYPO)
    adv_cover, adv_counts = load_advice()
    comps = json.loads((REPO / "kb" / "compositions.json").read_text(encoding="utf-8"))
    head, head_date = git_info()

    n_drafts = sum(1 for p in cm.DRAFTS.glob("*.md") if p.name.lower() != "readme.md")
    n_hypo = sum(1 for p in cm.HYPO.glob("*.md") if p.name.lower() != "readme.md")
    matchups_dir = REPO / "kb" / "matchups"
    n_canon = len(list(matchups_dir.glob("*.md"))) if matchups_dir.is_dir() else 0

    # ── матрицы и агрегаты ────────────────────────────────────────────────────
    rows2, tot2, n_pairs2 = bracket_matrix(2, cm.OUR_2V2, sourced, hypo, adv_cover, "2v2")
    rows3, n_covered3 = matrix_3v3_covered(cm.OUR_3V3, sourced, hypo, adv_cover)

    cells2_total = n_pairs2 * len(cm.OUR_2V2)
    cells2_kb = sum(t["kb"] for t in tot2.values())
    cells2_live = sum(t["live"] for t in tot2.values())  # что реально отдаст бот

    n_triples = len(list(itertools.combinations_with_replacement(cm.CLASSES, 3)))
    cells3_total = n_triples * len(cm.OUR_3V3)
    cells3_kb = cells3_live = 0
    tot3 = {}
    for slug, lbl in cm.OUR_3V3:
        ok = cm._classkey(slug)
        kb_c = len({e for o, e in sourced if o == ok})
        adv_extra = len(adv_cover.get(("3v3", ok), set()) - {e for o, e in sourced if o == ok})
        tot3[lbl] = {"kb": kb_c, "adv": adv_extra}
        cells3_kb += kb_c
        cells3_live += kb_c + adv_extra

    # 5v5 — вариаций нет нигде; если появятся (драфты/сиды с bracket=5v5), покажем счётчик
    n_5v5 = sum(1 for (br, _), n in adv_counts.items() if br == "5v5" for _ in range(n))
    live_total = cells2_live + cells3_live
    cells_total = cells2_total + cells3_total

    # ── чеклист прода ────────────────────────────────────────────────────────
    ps_path = REPO / "docs" / "prod-status.json"
    phases, launch = [], []
    if ps_path.is_file():
        ps = json.loads(ps_path.read_text(encoding="utf-8"))
        phases = ps.get("phases", [])
        launch = ps.get("launch", [])
    launch_done = sum(1 for i in launch if i.get("done"))
    phases_done = sum(1 for i in phases if i.get("done"))

    def check_items(items: list) -> str:
        out = []
        for i in items:
            mark = '<b class="ok">✓</b>' if i.get("done") else '<b class="no">○</b>'
            note = f' <small>— {html.escape(str(i.get("note", "")))}</small>' if i.get("note") else ""
            out.append(f"<li>{mark} {html.escape(str(i.get('name', '?')))}{note}</li>")
        return "\n".join(out)

    # ── карточки составов ────────────────────────────────────────────────────
    def card2(slug: str, lbl: str) -> str:
        ok = cm._classkey(slug)
        human = comps.get("our_comps", {}).get(slug, {}).get("human", slug)
        t = tot2[lbl]
        files = sum(1 for c, _v in sourced_exact if c == slug)
        seeds = adv_counts.get(("2v2", ok), 0)
        spec = "".join(
            ' <span class="cl kb" style="width:auto;padding:0 5px">✓ спек: vs Рога+СПрист</span>'
            for vs_spec, _l, _n in cm.SPEC_VARIANTS_2V2
            if (slug, vs_spec) in sourced_exact
        )
        return (
            f'<div class="card"><div class="nm">{lbl}</div><div class="hm">{html.escape(human)}</div>'
            f"{chips(ok)}"
            f'<div class="cnt"><b class="kb">✓{t["kb"]}</b> <b class="hyp">Г{t["hyp"]}</b> '
            f'<b class="adv">А{t["adv"]}</b> из {n_pairs2} пар · {files} драфтов · {seeds} сидов'
            f"{spec}</div></div>"
        )

    def card3(slug: str, lbl: str) -> str:
        ok = cm._classkey(slug)
        human = comps.get("our_comps_3v3", {}).get(slug, {}).get("human", slug)
        t = tot3[lbl]
        files = sum(1 for c, _v in sourced_exact if c == slug)
        seeds = adv_counts.get(("3v3", ok), 0)
        covered = t["kb"] + t["adv"]
        return (
            f'<div class="card"><div class="nm">{lbl}</div><div class="hm">{html.escape(human)}</div>'
            f"{chips(ok)}"
            f'<div class="cnt"><b class="kb">✓{t["kb"]}</b> <b class="adv">А{t["adv"]}</b>'
            f" · покрыто {covered} из {n_triples} троек · {files} драфтов · {seeds} сидов</div></div>"
        )

    cards2 = "".join(card2(s, l) for s, l in cm.OUR_2V2)
    cards3 = "".join(card3(s, l) for s, l in cm.OUR_3V3)

    # advice-only наши составы (есть только в сид-слое, вне канона compositions.json)
    canon_keys = {cm._classkey(s) for s, _ in cm.OUR_2V2} | {cm._classkey(s) for s, _ in cm.OUR_3V3}
    ghost_cards = []
    for (br, ok), n in sorted(adv_counts.items()):
        if ok in canon_keys or br == "2v2":
            continue
        nick = NICK_OUR.get(ok, ru_key(ok))
        enemies = " · ".join(ru_key(e) for e in sorted(adv_cover.get((br, ok), set())))
        ghost_cards.append(
            f'<div class="card ghost"><div class="nm">{nick}</div>'
            f'<div class="hm">{br} — только advice-слой (вне канона)</div>{chips(ok)}'
            f'<div class="cnt"><b class="adv">А{n}</b> · vs: {enemies}</div></div>'
        )
    ghosts = "".join(ghost_cards)

    # ── итоговые проценты ────────────────────────────────────────────────────
    live_pct = pct(live_total, cells_total)
    launch_pct = pct(launch_done, len(launch))
    canon_pct = pct(n_canon, n_canon + n_drafts)

    spec_cells = sum(
        1
        for vs_spec, _l, _n in cm.SPEC_VARIANTS_2V2
        for slug, _lbl in cm.OUR_2V2
        if (slug, vs_spec) in sourced_exact
    )

    gen_at = dt.datetime.now(dt.timezone.utc)
    gen_str = gen_at.strftime("%d.%m.%Y %H:%M UTC")

    tpl = TEMPLATE
    repl = {
        "__GEN__": gen_str,
        "__HEAD__": html.escape(head),
        "__HEAD_DATE__": html.escape(head_date),
        "__LAUNCH_PCT__": f"{launch_pct:.0f}",
        "__LAUNCH_DONE__": str(launch_done),
        "__LAUNCH_TOTAL__": str(len(launch)),
        "__PHASES_DONE__": str(phases_done),
        "__PHASES_TOTAL__": str(len(phases)),
        "__PHASES__": check_items(phases),
        "__LAUNCH__": check_items(launch),
        "__LIVE_PCT__": f"{live_pct:.0f}",
        "__LIVE_N__": str(live_total),
        "__CELLS_N__": str(cells_total),
        "__CANON_PCT__": f"{canon_pct:.0f}",
        "__CANON_N__": str(n_canon),
        "__DRAFTS_N__": str(n_drafts),
        "__HYPO_N__": str(n_hypo),
        "__BAR2__": bar(pct(cells2_live, cells2_total), pct(cells2_kb, cells2_total)),
        "__P2_LIVE__": f"{pct(cells2_live, cells2_total):.0f}",
        "__P2_KB__": f"{pct(cells2_kb, cells2_total):.0f}",
        "__C2_LIVE__": str(cells2_live),
        "__C2_TOTAL__": str(cells2_total),
        "__BAR3__": bar(pct(cells3_live, cells3_total), pct(cells3_kb, cells3_total)),
        "__P3_LIVE__": f"{pct(cells3_live, cells3_total):.0f}",
        "__P3_KB__": f"{pct(cells3_kb, cells3_total):.0f}",
        "__C3_LIVE__": str(cells3_live),
        "__C3_TOTAL__": str(cells3_total),
        "__N5V5__": str(n_5v5),
        "__CARDS2__": cards2,
        "__CARDS3__": cards3,
        "__GHOSTS__": ghosts,
        "__ROWS2__": "\n".join(rows2),
        "__ROWS3__": "\n".join(rows3),
        "__N_COVERED3__": str(n_covered3),
        "__N_TRIPLES__": str(n_triples),
        "__N_REST3__": str(n_triples - n_covered3),
        "__SPEC_CELLS__": str(spec_cells),
        "__H2COLS__": "".join(f"<th>{lbl}</th>" for _s, lbl in cm.OUR_2V2),
        "__H3COLS__": "".join(f"<th>{lbl}</th>" for _s, lbl in cm.OUR_3V3),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
    print(f"status page → {out}  ({len(tpl)} bytes; live {live_pct:.0f}%, launch {launch_pct:.0f}%)")
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Arena Coach — статус проекта</title>
<style>
:root{color-scheme:dark;
 --page:#0d0d0d;--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#898781;
 --line:rgba(255,255,255,.10);--grid:#2c2c2a;
 --kb:#0ca30c;--hyp:#fab219;--adv:#3987e5;--todo:#55544f;--bad:#d03b3b}
*{box-sizing:border-box;margin:0}
body{background:var(--page);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:0 20px 48px}
.wrap{max-width:880px;margin:0 auto}
nav{position:sticky;top:0;z-index:5;background:rgba(13,13,13,.92);backdrop-filter:blur(4px);
 border-bottom:1px solid var(--grid);margin:0 -20px 22px;padding:10px 20px}
nav .in{max-width:880px;margin:0 auto;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
nav b{font-size:15px}
nav a{color:var(--ink2);text-decoration:none;font-size:12.5px;border:1px solid var(--line);
 border-radius:99px;padding:2px 10px}
nav a:hover{color:var(--ink)}
#hdot{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;color:var(--ink2);margin-left:auto}
#hdot i{width:9px;height:9px;border-radius:99px;background:var(--muted);display:inline-block}
#hdot.on i{background:var(--kb);box-shadow:0 0 6px rgba(12,163,12,.8)}
#hdot.off i{background:var(--bad)}
header .sub{color:var(--muted);font-size:12.5px;margin-top:4px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0 10px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.tile .k{font-size:11px;letter-spacing:.6px;color:var(--muted);text-transform:uppercase}
.tile .v{font-size:26px;font-weight:700;margin:2px 0 3px}
.tile .s{font-size:12px;color:var(--ink2)}
.bar{position:relative;height:8px;border-radius:99px;background:var(--grid);overflow:hidden;margin:8px 0 6px}
.bar i{position:absolute;left:0;top:0;bottom:0;border-radius:99px}
.b-adv{background:var(--adv)} .b-kb{background:var(--kb)}
.brackets{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10px}
.brk{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:11px 14px}
.brk .t{display:flex;justify-content:space-between;font-size:13px}
.brk .t b{font-weight:700}
.brk .d{font-size:11.5px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:14px;align-items:center;background:var(--surface);
 border:1px solid var(--line);border-radius:10px;padding:9px 14px;margin:12px 0 8px;font-size:12.5px;color:var(--ink2)}
.legend .cl{margin-right:6px}
section{margin:34px 0}
h2{font-size:16px;font-weight:650;margin-bottom:3px}
.note{color:var(--muted);font-size:12.5px;margin-bottom:14px}
.cols{display:grid;grid-template-columns:1fr 1.4fr;gap:10px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:13px 16px}
.panel h3{font-size:13px;margin-bottom:8px;color:var(--ink)}
.panel ul{list-style:none;font-size:12.5px;color:var(--ink2)}
.panel li{padding:3px 0;border-bottom:1px dashed var(--grid)}
.panel li:last-child{border-bottom:none}
.panel li small{color:var(--muted)}
.ok{color:var(--kb)} .no{color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:10px;margin-bottom:18px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.card .nm{font-weight:700;font-size:15px}
.card .hm{color:var(--muted);font-size:11.5px;margin-bottom:8px}
.card.ghost{border-style:dashed;background:transparent}
.chip{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);border-radius:99px;
 padding:1px 8px 1px 6px;font-size:11.5px;color:var(--ink2);margin:0 4px 4px 0}
.chip i{width:8px;height:8px;border-radius:99px;display:inline-block}
.cnt{font-size:12px;color:var(--ink2);margin-top:6px}
.cnt b{font-weight:700;margin-right:2px}
.cnt b.kb{color:var(--kb)} .cnt b.hyp{color:var(--hyp)} .cnt b.adv{color:var(--adv)}
table{border-collapse:collapse;width:100%;background:var(--surface);border:1px solid var(--line);
 border-radius:12px;overflow:hidden;font-variant-numeric:tabular-nums}
table{display:block}
thead,tbody{display:table;width:100%;table-layout:fixed}
th,td{padding:3px 6px;text-align:center;font-weight:400}
thead th{font-size:12px;color:var(--ink2);font-weight:650;padding:8px 6px;border-bottom:1px solid var(--line)}
thead th:first-child{text-align:left;padding-left:14px}
tbody th{text-align:left;font-size:12.5px;color:var(--ink2);padding-left:14px;white-space:nowrap}
tbody th small{color:var(--muted);font-size:10.5px;margin-left:6px}
thead th:first-child,tbody th{width:38%}
tr.grp td{text-align:left;padding:7px 6px 3px 14px;font-size:10.5px;letter-spacing:.5px;
 text-transform:uppercase;color:var(--muted);border-top:1px solid var(--grid)}
tr.grp td i{width:7px;height:7px;border-radius:99px;display:inline-block;margin-right:6px}
.cl{display:inline-flex;min-width:26px;height:20px;border-radius:4px;align-items:center;
 justify-content:center;font-size:11px;font-weight:700;cursor:default}
.cl.kb{color:var(--kb);background:rgba(12,163,12,.14);border:1px solid rgba(12,163,12,.45)}
.cl.hyp{color:var(--hyp);background:rgba(250,178,25,.12);border:1px solid rgba(250,178,25,.45)}
.cl.adv{color:var(--adv);background:rgba(57,135,229,.13);border:1px solid rgba(57,135,229,.45)}
.cl.todo{color:var(--todo);background:transparent;border:1px solid var(--grid)}
.specrow{font-size:12.5px;color:var(--ink2);background:var(--surface);border:1px solid var(--line);
 border-top:none;border-radius:0 0 12px 12px;padding:8px 14px}
table.m2{border-radius:12px 12px 0 0}
.empty{background:var(--surface);border:1px dashed var(--line);border-radius:12px;padding:18px 20px;color:var(--ink2)}
.empty .z{font-size:24px;font-weight:700;color:var(--muted)}
footer{margin-top:34px;color:var(--muted);font-size:11.5px;border-top:1px solid var(--grid);padding-top:12px}
#tip{position:fixed;pointer-events:none;background:#26262a;border:1px solid var(--line);color:var(--ink);
 font-size:12px;padding:5px 9px;border-radius:7px;max-width:340px;display:none;z-index:9;
 box-shadow:0 4px 14px rgba(0,0,0,.5)}
@media(max-width:660px){.tiles,.brackets,.cols{grid-template-columns:1fr}}
</style></head><body>
<nav><div class="in"><b>Arena Coach</b>
 <a href="#prod">Прод</a><a href="#s2">2×2</a><a href="#s3">3×3</a><a href="#s5">5×5</a>
 <span id="hdot"><i></i><span id="htxt">проверяю прод…</span></span>
</div></nav>
<div class="wrap">

<header>
 <h1 style="font-size:20px">Статус проекта: покрытие вариаций и готовность прода</h1>
 <div class="sub">WoW TBC Classic Anniversary 2.4.3 · данные на коммит <code>__HEAD__</code> от __HEAD_DATE__ ·
 страница пересобирается при каждом деплое</div>
</header>

<div class="tiles">
 <div class="tile"><div class="k">Готовность к запуску</div><div class="v">__LAUNCH_PCT__%</div>
  <div class="bar"><i class="b-kb" style="width:__LAUNCH_PCT__%"></i></div>
  <div class="s">__LAUNCH_DONE__ из __LAUNCH_TOTAL__ пунктов чеклиста · фазы __PHASES_DONE__/__PHASES_TOTAL__</div></div>
 <div class="tile"><div class="k">Вариации покрыты</div><div class="v">__LIVE_PCT__%</div>
  <div class="bar"><i class="b-adv" style="width:__LIVE_PCT__%"></i></div>
  <div class="s">__LIVE_N__ из __CELLS_N__ класс-ячеек (2×2 + 3×3): бот ответит из KB или advice-кэша</div></div>
 <div class="tile"><div class="k">Канон (approve)</div><div class="v">__CANON_PCT__%</div>
  <div class="bar"><i class="b-kb" style="width:__CANON_PCT__%"></i></div>
  <div class="s">__CANON_N__ одобрено · __DRAFTS_N__ драфтов ждут approve · __HYPO_N__ гипотез в карантине</div></div>
</div>

<div class="brackets">
 <div class="brk"><div class="t"><span>2 × 2</span><b>__P2_LIVE__%</b></div>__BAR2__
  <div class="d">KB __P2_KB__% + advice = __C2_LIVE__/__C2_TOTAL__ ячеек</div></div>
 <div class="brk"><div class="t"><span>3 × 3</span><b>__P3_LIVE__%</b></div>__BAR3__
  <div class="d">KB __P3_KB__% + advice = __C3_LIVE__/__C3_TOTAL__ ячеек</div></div>
 <div class="brk"><div class="t"><span>5 × 5</span><b>0%</b></div>
  <div class="bar"></div><div class="d">сетапов нет — бракет не покрыт</div></div>
</div>

<div class="legend">
 <span><span class="cl kb">✓</span>KB-драфт — есть источник, идёт игрокам</span>
 <span><span class="cl hyp">Г</span>гипотеза — карантин, не идёт</span>
 <span><span class="cl adv">А</span>advice-сид — офлайн-разбор из кэша</span>
 <span><span class="cl todo">·</span>пусто</span>
 <span style="color:var(--muted)">в ячейке — старший слой; наведи курсор — видно все</span>
</div>

<section id="prod">
 <h2>Прод</h2>
 <div class="note">Чеклист правится в <code>docs/prod-status.json</code> — отметил пункт, запушил, страница пересчиталась.</div>
 <div class="cols">
  <div class="panel"><h3>Фазы (__PHASES_DONE__/__PHASES_TOTAL__)</h3><ul>
__PHASES__
  </ul></div>
  <div class="panel"><h3>До запуска (__LAUNCH_DONE__/__LAUNCH_TOTAL__)</h3><ul>
__LAUNCH__
  </ul></div>
 </div>
</section>

<section id="s2">
 <h2>2 × 2 — наши сетапы</h2>
 <div class="note">45 вражеских класс-пар на каждый состав. Спек-ячейки: __SPEC_CELLS__ (сверх матрицы).</div>
 <div class="cards">__CARDS2__</div>
 <table class="m2">
  <thead><tr><th>Враги \\ Наши</th>__H2COLS__</tr></thead>
  <tbody>
__ROWS2__
  </tbody>
 </table>
 <div class="specrow"><b>Спек-варианты</b> (матч по точному составу, сверх класс-ячеек): покрыто __SPEC_CELLS__ — vs Рога+Шадоу-прист (Shadow ≠ Disc)</div>
</section>

<section id="s3">
 <h2>3 × 3 — наши сетапы</h2>
 <div class="note">В матрице — только покрытые тройки (__N_COVERED3__ из __N_TRIPLES__); остальные __N_REST3__ пока пустые.</div>
 <div class="cards">__CARDS3__ __GHOSTS__</div>
 <table>
  <thead><tr><th>Враги \\ Наши</th>__H3COLS__</tr></thead>
  <tbody>
__ROWS3__
  </tbody>
 </table>
</section>

<section id="s5">
 <h2>5 × 5</h2>
 <div class="empty"><div class="z">Пусто</div>
 Сетапов для 5v5 нет ни в каноне (compositions.json), ни в KB, ни в advice-слое (сидов: __N5V5__).
 В бою бот даст только эвристику незнакомых сетапов Phase 4.7 (килл-таргет по классам + угрозы).</div>
</section>

<footer>Ячейка = класс-уровень (спеки врагов сведены к классам; спек-варианты — отдельно).
Слои: KB-драфт → гипотеза → advice-сид. Сгенерировано __GEN__ · <code>tools/gen_status_page.py</code> ·
данные: kb/, tools/advice_seed.json, docs/prod-status.json.</footer>
</div>
<div id="tip"></div>
<script>
(function(){
var tip=document.getElementById('tip');
document.addEventListener('mouseover',function(e){var t=e.target.closest('[data-tip]');
 if(!t){tip.style.display='none';return} tip.textContent=t.dataset.tip;tip.style.display='block'});
document.addEventListener('mousemove',function(e){if(tip.style.display==='none')return;
 var w=tip.offsetWidth,h=tip.offsetHeight,x=e.clientX+12,y=e.clientY+14;
 if(x+w>innerWidth-8)x=e.clientX-w-10; if(y+h>innerHeight-8)y=e.clientY-h-10;
 tip.style.left=x+'px';tip.style.top=y+'px'});
var dot=document.getElementById('hdot'),txt=document.getElementById('htxt');
function fmt(s){s=Math.floor(s);var d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);
 return (d?d+'д ':'')+(h?h+'ч ':'')+m+'м'}
function ping(){fetch('/health',{cache:'no-store'}).then(function(r){return r.json()})
 .then(function(j){if(j&&j.status==='ok'){dot.className='on';txt.textContent='прод онлайн · аптайм '+fmt(j.uptime_s||0)}
  else{dot.className='off';txt.textContent='прод отвечает, но не ok'}})
 .catch(function(){dot.className='off';txt.textContent='нет связи с прод (/health)'})}
ping();setInterval(ping,60000);
})();
</script>
</body></html>"""


if __name__ == "__main__":
    raise SystemExit(main())
