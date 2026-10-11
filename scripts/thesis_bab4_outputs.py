#!/usr/bin/env python3
"""
Thesis BAB 4 outputs for the open-loop campaign: Indonesian figures, table cells and derived numbers.

Inputs: the Part 12 results written by scripts/analyze_openloop_campaign.py (analysis/part12/results.json) and, for
the timeline figures and the configuration checks, the run folders read through that script's own parsers. Nothing
here is a new statistical analysis: the derived numbers are differences, shares, counts and sets taken from the Part 12
results or read from the stored run data, each written with its inputs to derived.json.

Number format follows the thesis (Indonesian): decimal comma, thousands dot, true minus sign.

Run on Windows with the bundled interpreter (reads the campaign folder, writes only to --out):
  PYTHONUTF8=1 tools/python312/python.exe scripts/thesis_bab4_outputs.py
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_openloop_campaign as aoc  # noqa: E402  (sets PILOT_OPENLOOP_DIR to the campaign folder)

po = aoc.po
SERVICES, PATTERNS, CONFIGS, AUTOSCALED = po.SERVICES, po.PATTERNS, po.CONFIGS, po.AUTOSCALED
PART12 = po.PILOT_DIR / "analysis" / "part12"
PART12_ORIGINAL_SLO = po.PILOT_DIR / "analysis" / "part12-slo-awal"   # same analysis with the frozen SLOs
# SLO sensitivity (thesis 4.6.5): auth's SLO comes from closed-loop B2 at a higher load than the open-loop peak, so it
# is varied over a range; shipping is shown at the analysis value and at the value frozen before the campaign.
SENSITIVITY_SLO_MS = {"auth-service": [900, 1000, 1100, 1200, 1300, 1400, 1500], "shipping-rate-service": [1000, 1200]}
THRESHOLD = {"auth-service": 5, "shipping-rate-service": 15}
CPU_TARGET = {"h1": 80, "h2": 50}
PATTERN_ID = {"gradual": "gradual", "spike": "spike", "oscillating": "oscillating"}
OUTCOME_ID = {"O1_slo_s": "O1", "O2_error_pct": "O2"}

# ── number format ────────────────────────────────────────────────────────────

MINUS = "−"


def num(x, d=0):
    """Indonesian number: thousands dot, decimal comma, true minus; None -> en dash."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    s = f"{abs(x):,.{d}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return (MINUS if x < 0 and float(s.replace(".", "").replace(",", ".")) != 0 else "") + s


def signed(x, d=0):
    if x is None:
        return "–"
    if float(f"{abs(x):.{d}f}") == 0:
        return num(0.0, d)
    return ("+" if x > 0 else MINUS) + num(abs(x), d)


def cell_range(a, d):
    return f"{num(a['median'], d)} [{num(a['min'], d)}–{num(a['max'], d)}]"


DECIMALS = {"O1_slo_s": 0, "O2_error_pct": 2, "O3_goodput_rps": 2, "O4_first_up_s": 1, "O4_first_new_ready_s": 1,
            "O5_replica_s": 0, "O5_cpu_core_s": 1}


def vd_label(a12):
    """Vargha & Delaney (2000) magnitude of A12: |A - 0.5| < 0.06 negligible, < 0.14 small, < 0.21 medium."""
    d = abs(a12 - 0.5)
    return "dapat diabaikan" if d < 0.06 else "kecil" if d < 0.14 else "sedang" if d < 0.21 else "besar"


# ── derived numbers ──────────────────────────────────────────────────────────

def a2_row(A2, service, pattern, outcome, contrast):
    return next(r for r in A2 if r["service"] == service and r["pattern"] == pattern and r["outcome"] == outcome
                and r["contrast"] == contrast)


def non_dominated(points, key, configs):
    out = []
    for c in configs:
        v = points[c]
        if not any(points[o]["O1"] <= v["O1"] and points[o][key] <= v[key]
                   and (points[o]["O1"] < v["O1"] or points[o][key] < v[key]) for o in configs if o != c):
            out.append(c)
    return out


def read_text(path):
    return path.read_text(errors="ignore") if path.exists() else ""


def spec_block(text):
    m = re.search(r"^spec:\n(.*?)^status:", text, re.S | re.M)
    return m.group(1) if m else ""


def config_evidence(runs):
    """What the stored objects of every run say, counted over the runs of each config and service."""
    ev = defaultdict(lambda: defaultdict(int))
    for r in runs:
        key = f"{r['service']}|{r['config']}"
        run_dir = po.PILOT_DIR / r["run_dir"]
        meta = po.load_json(run_dir / "metadata.json") or {}
        lp, so = meta.get("load_profile") or {}, meta.get("service_overrides") or {}
        e = ev[key]
        e["runs"] += 1
        e[f"overlay={so.get('code_overlay_sha')}"] += 1
        e[f"cap={so.get('max_inflight_requests')}"] += 1
        e[f"k6={lp.get('k6_image')}"] += 1
        e[f"vus={lp.get('pre_allocated_vus')}/{lp.get('max_vus')}"] += 1
        e[f"no_reuse={lp.get('no_connection_reuse')}"] += 1
        e[f"timeout={lp.get('request_timeout')}"] += 1
        e[f"rates={lp.get('base_rate')}->{lp.get('peak_rate')}"] += 1
        e[f"exit={meta.get('k6_exit_code')}"] += 1
        if r["service"] == "auth-service":
            pa = meta.get("preauth_tokens") or {}
            e[f"preauth={pa.get('enabled')}/{pa.get('count')}"] += 1
            if "PREAUTH_USED tokens=120" in read_text(run_dir / "k6-output.log"):
                e["log PREAUTH_USED tokens=120"] += 1
        spec = spec_block(read_text(run_dir / "hpa-status.yaml"))
        if r["config"] in ("h1", "h2"):
            m = re.search(r"averageUtilization: (\d+)", spec)
            e[f"cpu_target={m.group(1) if m else None}"] += 1
            e[f"behavior_block={'yes' if 'behavior:' in spec else 'no'}"] += 1
        if r["config"] == "h3":
            m = re.search(r'name: (\S+)\n\s+target:\n\s+averageValue: "?(\d+)"?', spec)
            e[f"metric={m.group(1) if m else None}/{m.group(2) if m else None}"] += 1
        if r["config"] == "k1":
            ks = read_text(run_dir / "keda-status.yaml")
            th = re.search(r'threshold: "?(\d+)"?', ks)
            pi = re.search(r"pollingInterval: (\d+)", ks)
            cd = re.search(r"cooldownPeriod: (\d+)", ks)
            e[f"keda threshold={th.group(1) if th else None} polling={pi.group(1) if pi else None} "
              f"cooldown={cd.group(1) if cd else None}"] += 1
            m = re.search(r"name: (s\d+-prometheus)\n(?:.*\n)*?\s+averageValue: \"?(\d+)\"?", spec)
            e[f"managed_hpa_metric={m.group(1) if m else None}/{m.group(2) if m else None}"] += 1
        if r["config"] in ("h2", "h3", "k1"):
            down = re.search(r"scaleDown:\n(?:.*\n)*?\s+stabilizationWindowSeconds: (\d+)", spec)
            up = re.search(r"scaleUp:\n(?:.*\n)*?\s+stabilizationWindowSeconds: (\d+)", spec)
            e[f"windows down={down.group(1) if down else None} up={up.group(1) if up else None}"] += 1
    return {k: dict(v) for k, v in ev.items()}


def cpu_reading_refresh(runs):
    """Seconds between changes of the HPA's CPU reading inside the KPI window (snapshots ~6.1 s apart), pooled over
    the H1/H2 runs. (Blueprint Parts 08/11 quote 61.4 s and 82% from an earlier, unsaved computation; this one is the
    reproducible figure.)"""
    gaps, n_runs = [], 0
    lo, hi = po.LOAD_WINDOW
    for r in runs:
        if r["config"] not in ("h1", "h2"):
            continue
        n_runs += 1
        snaps = aoc.hpa_snapshots(po.PILOT_DIR / r["run_dir"], r["service"])
        t0 = r["t_start"]
        snaps = [s for s in snaps if t0 + lo <= s["ts"] <= t0 + hi and s["reading"] is not None]
        changes = [b["ts"] for a, b in zip(snaps, snaps[1:]) if b["reading"] != a["reading"]]
        gaps += [b - a for a, b in zip(changes, changes[1:])]
    g = np.array(gaps)
    return {"runs": n_runs, "gaps": int(len(g)), "median_s": float(np.median(g)),
            "share_50_70": float(np.mean((g >= 50) & (g <= 70))), "p10_s": float(np.percentile(g, 10)),
            "p90_s": float(np.percentile(g, 90))}


def peak_start_pods(runs):
    """Ready pods at the start of each oscillating peak hold (k6 t 130, 310, 490 s)."""
    out = {}
    for r in runs:
        if r["pattern"] != "oscillating" or r["config"] not in AUTOSCALED:
            continue
        pods = aoc.pod_records(po.PILOT_DIR / r["run_dir"])
        out[f"{r['service']}|{r['config']}|{r['rep']}"] = [aoc.ready_count(pods, r["t_start"] + t)
                                                         for t in (130.0, 310.0, 490.0)]
    by_cfg = defaultdict(list)
    for k, v in out.items():
        by_cfg[k.split("|")[1]].append(v)
    summary = {c: {"runs": len(v), "peak2_min": min(x[1] for x in v), "peak2_max": max(x[1] for x in v),
                   "peak3_min": min(x[2] for x in v), "peak3_max": max(x[2] for x in v),
                   "runs_one_pod_at_peaks_2_and_3": sum(1 for x in v if x[1] == 1 and x[2] == 1)}
               for c, v in by_cfg.items()}
    return {"per_run": out, "per_config": summary}


# ── SLO: validation against B2 and sensitivity ───────────────────────────────

def run_key(r):
    return f"{r['service']}|{r['pattern']}|{r['config']}|{r['rep']}"


def bin_p95(runs):
    """p95 of every 10 s bin of the KPI window (failed requests infinite) and the window p95, per run, through the
    analysis script's own window statistics; O1 at any SLO is then 10 s x the bins above it."""
    out = {}
    for r in runs:
        run_dir = po.PILOT_DIR / r["run_dir"]
        meta = po.load_json(run_dir / "metadata.json") or {}
        raw = po.Raw.load(run_dir, meta["run_id"])
        t0 = r["t_start"]
        ws = po.window_stats(raw, raw.scn_id(f"openloop_{r['pattern']}"), t0 + po.LOAD_WINDOW[0],
                             t0 + po.LOAD_WINDOW[1], po.timeout_ms_of(meta), slo_ms=math.inf, rel0=t0)
        out[run_key(r)] = {"bins": [b["p95"] for b in ws["slo_bins"]], "window_p95": ws["p95_ms"]}
    return out


def o1_at(bins, slo):
    return 10.0 * sum(1 for p in bins if p is None or p > slo)


def slo_validation(runs, bins, slo_ms):
    """How often healthy B2 is above the SLO: window p95 per pattern and the share of its 10 s bins over the SLO."""
    out = {}
    for s in SERVICES:
        per_pattern, all_bins = {}, []
        for p in PATTERNS:
            rs = [r for r in runs if r["service"] == s and r["pattern"] == p and r["config"] == "b2"]
            bb = [x for r in rs for x in bins[run_key(r)]["bins"] if x is not None]
            all_bins += bb
            per_pattern[p] = {"window_p95_min": min(bins[run_key(r)]["window_p95"] for r in rs),
                              "window_p95_max": max(bins[run_key(r)]["window_p95"] for r in rs),
                              "bins": len(bb), "bins_over_slo": sum(1 for x in bb if x > slo_ms[s])}
        out[s] = {"slo_ms": slo_ms[s], "patterns": per_pattern, "bins": len(all_bins),
                  "bins_over_slo": sum(1 for x in all_bins if x > slo_ms[s])}
    return out


def slo_sensitivity(runs, bins, slo_ms, A2):
    """The planned O1 contrasts, medians and gap closed recomputed at other SLO values (exploratory)."""
    out = {}
    for s in SERVICES:
        rows = []
        for slo in SENSITIVITY_SLO_MS[s]:
            o1 = defaultdict(dict)
            for r in runs:
                if r["service"] == s:
                    o1[(r["pattern"], r["config"])][r["rep"]] = o1_at(bins[run_key(r)]["bins"], slo)
            row = {"slo_ms": slo, "analysis_slo": slo == slo_ms[s], "patterns": {}, "significant": []}
            for p in PATTERNS:
                vals = {c: [o1[(p, c)][k] for k in sorted(o1[(p, c)])] for c in CONFIGS}
                med = {c: aoc.med(vals[c]) for c in CONFIGS}
                tests = []
                for a, b, factor in aoc.CONTRASTS:
                    _, pv = aoc.rank_sum_test(vals[a], vals[b])
                    tests.append({"factor": factor, "contrast": f"{a} vs {b}", "diff_b_minus_a": med[b] - med[a],
                                  "A12_a_gt_b": aoc.a12(vals[a], vals[b]), "p": pv})
                for t, h in zip(tests, aoc.holm([t["p"] for t in tests])):
                    t["p_holm"] = h
                    t["significant"] = h < 0.05
                    if t["significant"]:
                        row["significant"].append(f"{p}|{t['factor']}")
                best = min(med[c] for c in AUTOSCALED)
                row["patterns"][p] = {
                    "medians": med, "tests": tests,
                    "gap_closed": {c: (med["b1"] - med[c]) / (med["b1"] - med["b2"]) for c in AUTOSCALED},
                    "best_autoscalers": [c for c in AUTOSCALED if med[c] == best]}
            if row["analysis_slo"]:   # must reproduce the Part 12 results exactly
                for t in A2:
                    if t["service"] == s and t["outcome"] == "O1_slo_s":
                        mine = next(x for x in row["patterns"][t["pattern"]]["tests"] if x["contrast"] == t["contrast"])
                        assert abs(mine["p_holm"] - t["p_holm"]) < 1e-12, (s, t["pattern"], t["contrast"])
            rows.append(row)
        out[s] = rows
    return out


def original_slo_results():
    """Shipping O1 under the SLO frozen before the campaign (1200 ms), for the appendix."""
    path = PART12_ORIGINAL_SLO / "results.json"
    if not path.exists():
        return None
    res = json.loads(path.read_text(encoding="utf-8"))["analyses"]
    return {"slo_ms": res["slo_ms"],
            "A1_O1": {k: v["O1_slo_s"] for k, v in res["A1"].items()},
            "A2_O1": [t for t in res["A2"] if t["outcome"] == "O1_slo_s"]}


def holm_family_sensitivity(A2):
    """The plan corrects within families of three tests (one per service x pattern x outcome). Smallest Holm-adjusted p
    and number of significant tests when the same 36 p values are corrected in wider families: the 12 tests of each
    factor, or all 36 together."""
    out = {"smallest_raw_p": min(t["p"] for t in A2),
           "family_of_3": {"tests": len(A2), "significant": sum(1 for t in A2 if t["significant_0.05"]),
                           "smallest_p_holm": min(t["p_holm"] for t in A2)}}
    for factor in sorted({t["factor"] for t in A2}):
        adj = aoc.holm([t["p"] for t in A2 if t["factor"] == factor])
        out[f"factor|{factor}"] = {"tests": len(adj), "significant": sum(1 for a in adj if a <= 0.05),
                                   "smallest_p_holm": min(adj)}
    adj = aoc.holm([t["p"] for t in A2])
    out["all_36"] = {"tests": len(adj), "significant": sum(1 for a in adj if a <= 0.05), "smallest_p_holm": min(adj)}
    return out


def session_metric_contrasts(runs):
    """Metric contrast (median H3 - median H2) within each cluster session, per service x pattern x outcome; the
    session medians are those of Lampiran C (reps 1-2 and 3-5)."""
    out = {}
    for s in SERVICES:
        for p in PATTERNS:
            for o in ("O1_slo_s", "O2_error_pct"):
                row = {}
                for name, reps in (("session1", aoc.SESSION_1), ("session2", aoc.SESSION_2)):
                    med = {c: float(np.median([r[o] for r in runs if r["service"] == s and r["pattern"] == p
                                               and r["config"] == c and int(r["rep"]) in reps])) for c in ("h2", "h3")}
                    row[name] = med["h3"] - med["h2"]
                out[f"{s}|{p}|{OUTCOME_ID[o]}"] = row
    return out


def _ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    ranks, i = [0.0] * len(x), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def outcome_overlap(runs):
    """How much O1 and O3 overlap with O2: failed requests count as infinite latency in O1, and with open-loop load and
    no dropped iterations O3 is the offered rate times (1 - O2)."""
    ra, rb = _ranks([r["O1_slo_s"] for r in runs]), _ranks([r["O2_error_pct"] for r in runs])
    rho = float(np.corrcoef(ra, rb)[0, 1])
    window = po.LOAD_WINDOW[1] - po.LOAD_WINDOW[0]
    dev = max(abs(r["O3_goodput_rps"] - r["requests"] / window * (1 - r["O2_error_pct"] / 100)) for r in runs)
    return {"runs": len(runs), "spearman_O1_O2": rho, "O3_max_abs_dev_rps": dev, "window_s": window}


def x_review(X):
    """Numbers quoted in the thesis from the exploratory analyses X1-X5 of the Part 12 script (added after the review)."""
    x1 = {f"{r['service']}|{r['pattern']}|{r['outcome']}|{r['factor']}": r for r in X["X1"]}
    engine = [r for r in X["X2"] if r["factor"] == "engine"]
    bounds = {}
    for scope, rows in (("all", engine), ("shipping-rate-service",
                                          [r for r in engine if r["service"] == "shipping-rate-service"])):
        for o in ("O1_slo_s", "O2_error_pct"):
            sel = [r for r in rows if r["outcome"] == o]
            bounds[f"{scope}|{OUTCOME_ID[o]}"] = [min(r["hl_low"] for r in sel), max(r["hl_high"] for r in sel)]
    return {"X1": x1, "engine_hl_bounds": bounds, "hl_coverage": X["X2"][0]["hl_coverage"],
            "session_agreement": X["X3"]["agreement"], "placement": X["X4"], "cpu_curve": X["X5"]}


def derive(res, runs):
    A1, A2, A3, A4, S, A5 = (res[k] for k in ("A1", "A2", "A3", "A4", "S", "A5"))
    d = {"inputs": {"results": "analysis/part12/results.json (scripts/analyze_openloop_campaign.py)"}}

    # decomposition (metric H2 -> H3, engine H3 -> K1) and tuning (H1 -> H2), per service x pattern x outcome
    dec = []
    for s in SERVICES:
        for p in PATTERNS:
            for o in ("O1_slo_s", "O2_error_pct"):
                row = {"service": s, "pattern": p, "outcome": OUTCOME_ID[o]}
                for name, a, b in (("metric", "h2", "h3"), ("engine", "h3", "k1"), ("tuning", "h1", "h2")):
                    t = a2_row(A2, s, p, o, f"{a} vs {b}")
                    row[name] = {"median_a": t["median_a"], "median_b": t["median_b"],
                                 "diff_b_minus_a": t["median_b"] - t["median_a"], "U_a": t["U_a"], "p": t["p"],
                                 "p_holm": t["p_holm"], "A12_a_gt_b": t["A12_a_gt_b"],
                                 "vd_size": vd_label(t["A12_a_gt_b"]), "significant": t["significant_0.05"]}
                if o == "O1_slo_s":
                    g = A3[f"{s}|{p}"]
                    row["gap_share_points"] = {
                        "metric": 100 * (g["h3"]["gap_closed"] - g["h2"]["gap_closed"]),
                        "engine": 100 * (g["k1"]["gap_closed"] - g["h3"]["gap_closed"]),
                        "tuning": 100 * (g["h2"]["gap_closed"] - g["h1"]["gap_closed"])}
                dec.append(row)
    d["decomposition"] = dec
    larger = sum(1 for r in dec if abs(r["metric"]["diff_b_minus_a"]) > abs(r["engine"]["diff_b_minus_a"]))
    ties = sum(1 for r in dec if abs(r["metric"]["diff_b_minus_a"]) == abs(r["engine"]["diff_b_minus_a"]))
    d["metric_vs_engine"] = {
        "comparisons": len(dec), "metric_larger": larger, "ties": ties,
        "significant": {f: sum(1 for r in dec if r[f]["significant"]) for f in ("metric", "engine", "tuning")},
        "engine_abs_diff_max": {"O1": max(abs(r["engine"]["diff_b_minus_a"]) for r in dec if r["outcome"] == "O1"),
                                "O2": max(abs(r["engine"]["diff_b_minus_a"]) for r in dec if r["outcome"] == "O2")},
        "engine_a12_range": [min(r["engine"]["A12_a_gt_b"] for r in dec), max(r["engine"]["A12_a_gt_b"] for r in dec)],
        "engine_vd_sizes": {lbl: sum(1 for r in dec if r["engine"]["vd_size"] == lbl)
                            for lbl in ("dapat diabaikan", "kecil", "sedang", "besar")},
        "engine_direction": {"h3_better": sum(1 for r in dec if r["engine"]["A12_a_gt_b"] < 0.5),
                             "k1_better": sum(1 for r in dec if r["engine"]["A12_a_gt_b"] > 0.5),
                             "tie": sum(1 for r in dec if r["engine"]["A12_a_gt_b"] == 0.5)},
        "engine_smallest_p": min(r["engine"]["p"] for r in dec),
        "engine_smallest_p_holm": min(r["engine"]["p_holm"] for r in dec),
    }

    # against the running system (B1) and the over-provisioned baseline (B2), cell medians
    vs = []
    for s in SERVICES:
        for p in PATTERNS:
            b1 = {o: A1[f"{s}|{p}|b1"][o]["median"] for o in ("O1_slo_s", "O2_error_pct", "O3_goodput_rps")}
            b2 = {o: A1[f"{s}|{p}|b2"][o]["median"] for o in ("O1_slo_s", "O2_error_pct", "O3_goodput_rps",
                                                              "O5_replica_s", "O5_cpu_core_s")}
            row = {"service": s, "pattern": p, "B1": b1, "B2": b2, "autoscalers": {}}
            for c in AUTOSCALED:
                a = A1[f"{s}|{p}|{c}"]
                row["autoscalers"][c] = {
                    "O1": a["O1_slo_s"]["median"], "O2": a["O2_error_pct"]["median"],
                    "O3": a["O3_goodput_rps"]["median"],
                    "replica_share_of_B2": a["O5_replica_s"]["median"] / b2["O5_replica_s"],
                    "cpu_share_of_B2": a["O5_cpu_core_s"]["median"] / b2["O5_cpu_core_s"],
                    "gap_closed": A3[f"{s}|{p}"][c]["gap_closed"]}
            vs.append(row)
    d["vs_baselines"] = vs
    all_a = [a for r in vs for a in r["autoscalers"].values()]
    d["vs_baselines_summary"] = {
        "B1_O1_range": [min(r["B1"]["O1_slo_s"] for r in vs), max(r["B1"]["O1_slo_s"] for r in vs)],
        "B1_O2_range": [min(r["B1"]["O2_error_pct"] for r in vs), max(r["B1"]["O2_error_pct"] for r in vs)],
        "autoscaler_O1_range": [min(a["O1"] for a in all_a), max(a["O1"] for a in all_a)],
        "autoscaler_O2_range": [min(a["O2"] for a in all_a), max(a["O2"] for a in all_a)],
        "replica_share_range": [min(a["replica_share_of_B2"] for a in all_a), max(a["replica_share_of_B2"] for a in all_a)],
        "cpu_share_range": [min(a["cpu_share_of_B2"] for a in all_a), max(a["cpu_share_of_B2"] for a in all_a)],
        "gap_closed_range_by_pattern": {
            p: [min(r["autoscalers"][c]["gap_closed"] for r in vs if r["pattern"] == p for c in AUTOSCALED),
                max(r["autoscalers"][c]["gap_closed"] for r in vs if r["pattern"] == p for c in AUTOSCALED)]
            for p in PATTERNS},
    }

    # Pareto sets with and without the baselines
    fronts = {}
    for s in SERVICES:
        for p in PATTERNS:
            pts = A5[f"{s}|{p}"]["points"]
            fronts[f"{s}|{p}"] = {
                "all_replica_s": A5[f"{s}|{p}"]["non_dominated"]["replica_s"],
                "all_cpu_core_s": A5[f"{s}|{p}"]["non_dominated"]["cpu_core_s"],
                "autoscalers_replica_s": non_dominated(pts, "replica_s", AUTOSCALED),
                "autoscalers_cpu_core_s": non_dominated(pts, "cpu_core_s", AUTOSCALED),
                "best_O1": sorted(c for c in AUTOSCALED if pts[c]["O1"] == min(pts[x]["O1"] for x in AUTOSCALED)),
                "least_replica_s": min(AUTOSCALED, key=lambda c: pts[c]["replica_s"])}
    d["pareto"] = fronts

    # time to scale: first new pod Ready minus first scale-up, every autoscaled run
    lags = [r["O4_first_new_ready_s"] - r["O4_first_up_s"] for r in runs
            if r["config"] in AUTOSCALED and r["O4_first_up_s"] is not None and r["O4_first_new_ready_s"] is not None]
    d["ready_lag"] = {"runs": len(lags), "min": min(lags), "median": float(np.median(lags)), "max": max(lags)}

    # robustness gate, reps 1-2 (O1 and O2 per run)
    gate = {}
    for r in runs:
        if r["rep"] in (1, 2):
            gate.setdefault(f"{r['service']}|{r['pattern']}|{r['config']}", {})[r["rep"]] = {
                "O1": r["O1_slo_s"], "O2": r["O2_error_pct"]}
    d["gate_reps_1_2"] = gate

    # offered load: requests in the KPI window per cell (open loop: the same for every config)
    req = defaultdict(list)
    for r in runs:
        req[f"{r['service']}|{r['pattern']}"].append(r["requests"])
    d["window_requests"] = {k: {"min": min(v), "max": max(v)} for k, v in req.items()}

    # what the failed requests were: immediate 503 rejections (load shedding), timeouts, other failures
    comp = {}
    for name, cfgs in (("B1", ("b1",)), ("B2", ("b2",)), ("CPU", ("h1", "h2")), ("laju permintaan", ("h3", "k1"))):
        for s in SERVICES:
            rs = [r for r in runs if r["service"] == s and r["config"] in cfgs]
            fail = sum(r["requests"] * r["O2_error_pct"] / 100 for r in rs)
            shed = sum(r["requests"] * r["shed_pct"] / 100 for r in rs)
            tout = sum(r["requests"] * r["timeout_pct"] / 100 for r in rs)
            comp[f"{s}|{name}"] = {"failed": round(fail), "shed_share": shed / fail if fail else None,
                                   "timeout_share": tout / fail if fail else None}
    d["error_composition"] = comp
    d["scale_changes_auth_osc_h2"] = {r["rep"]: r["scale_changes"] for r in runs if r["service"] == "auth-service"
                                      and r["pattern"] == "oscillating" and r["config"] == "h2" and r["rep"] in (1, 2)}

    d["cpu_reading_refresh"] = cpu_reading_refresh(runs)
    d["peak_start_pods"] = peak_start_pods(runs)
    d["anti_phase"] = {f"{r['service']}|{r['pattern']}|{r['config']}|{r['rep']}": r["anti_phase_times_s"]
                       for r in runs if r["anti_phase_downs"]}
    d["checks"] = {"runs": len(runs), "inexact_scale_times": sum(r["inexact_scale_times"] for r in runs),
                   "scale_ups_before_onset": sum(r["scale_ups_before_onset"] for r in runs),
                   "raw_md5_verified": sum(1 for r in runs if r["raw_md5_verified"]),
                   "cpu_samples": [min(r["cpu_samples"] for r in runs), max(r["cpu_samples"] for r in runs)]}
    d["config_evidence"] = config_evidence(runs)
    d["A4_cpu_vs_rate"] = A4["cpu_vs_rate"]
    d["session_sign_tests"] = S["sign_tests"]
    bins = bin_p95(runs)
    d["slo_ms"] = res["slo_ms"]
    d["slo_validation"] = slo_validation(runs, bins, res["slo_ms"])
    d["slo_sensitivity"] = slo_sensitivity(runs, bins, res["slo_ms"], A2)
    d["original_slo"] = original_slo_results()
    d["holm_family_sensitivity"] = holm_family_sensitivity(A2)
    d["session_metric_contrasts"] = session_metric_contrasts(runs)
    d["outcome_overlap"] = outcome_overlap(runs)
    d["x_review"] = x_review(res["X"])
    return d


# ── table cells (Indonesian format) ──────────────────────────────────────────

def tables(res, d):
    A1, A3, A4, S = res["A1"], res["A3"], res["A4"], res["S"]
    T = {}
    # gate after reps 1-2: O1 rep 1 / rep 2
    rows = []
    for c in CONFIGS:
        row = [c.upper()]
        for s in SERVICES:
            for p in PATTERNS:
                g = d["gate_reps_1_2"][f"{s}|{p}|{c}"]
                row.append(f"{num(g[1]['O1'])}/{num(g[2]['O1'])}")
        rows.append(row)
    T["gate_o1"] = rows
    # O1, O2, O3 per service: config x pattern, median [min-max]
    for o in ("O1_slo_s", "O2_error_pct", "O3_goodput_rps"):
        for s in SERVICES:
            T[f"{o}|{s}"] = [[c.upper()] + [cell_range(A1[f"{s}|{p}|{c}"][o], DECIMALS[o]) for p in PATTERNS]
                             for c in CONFIGS]
    # O4 first scale-up, autoscalers only: service x pattern rows, configs as columns
    T["O4_first_up_s"] = [[s, p] + [cell_range(A1[f"{s}|{p}|{c}"]["O4_first_up_s"], 1) for c in AUTOSCALED]
                          for s in SERVICES for p in PATTERNS]
    # O5 medians: service x pattern rows, configs as columns
    for o in ("O5_replica_s", "O5_cpu_core_s"):
        T[o] = [[s, p] + [num(A1[f"{s}|{p}|{c}"][o]["median"], DECIMALS[o]) for c in CONFIGS]
                for s in SERVICES for p in PATTERNS]
    # A3 gap closed
    T["gap_closed"] = [[s, p, num(A3[f"{s}|{p}"]["B1"]), num(A3[f"{s}|{p}"]["B2"])]
                       + [num(100 * A3[f"{s}|{p}"][c]["gap_closed"], 1) + "%" for c in AUTOSCALED]
                       for s in SERVICES for p in PATTERNS]
    # decomposition: metric (H2 -> H3) and engine (H3 -> K1)
    def eff(e, outcome):
        dd = 0 if outcome == "O1" else 2
        sig = "*" if e["significant"] else ""
        return [signed(e["diff_b_minus_a"], dd), num(e["A12_a_gt_b"], 2), num(e["p_holm"], 4) + sig]
    T["decomposition"] = [[r["service"], r["pattern"], r["outcome"]] + eff(r["metric"], r["outcome"])
                          + eff(r["engine"], r["outcome"]) for r in d["decomposition"]]
    T["tuning"] = [[r["service"], r["pattern"], r["outcome"],
                    num(r["tuning"]["median_a"], 0 if r["outcome"] == "O1" else 2),
                    num(r["tuning"]["median_b"], 0 if r["outcome"] == "O1" else 2),
                    num(r["tuning"]["A12_a_gt_b"], 2),
                    num(r["tuning"]["p_holm"], 4) + ("*" if r["tuning"]["significant"] else "")]
                   for r in d["decomposition"]]
    # A4 tests
    T["dispersion_tests"] = [[OUTCOME_ID[r["outcome"]], {"range": "rentang", "mad": "MAD"}[r["dispersion"]],
                              num(r["median_cpu"], 0 if r["outcome"] == "O1_slo_s" else 2),
                              num(r["median_rate"], 0 if r["outcome"] == "O1_slo_s" else 2),
                              num(r["U_cpu"], 1), num(r["p"], 4), num(r["A12_cpu_gt_rate"], 2)]
                             for r in A4["cpu_vs_rate"]]
    # session sign tests
    T["session"] = [[k.split("|")[0].replace("autoscaled", "autoscaler"), OUTCOME_ID[k.split("|")[1]],
                     str(v["cells"]), str(v["session1_worse"]), str(v["session1_better"]), str(v["ties"]),
                     num(v["p_two_sided"], 4)] for k, v in S["sign_tests"].items()]
    # Pareto sets
    T["pareto_sets"] = [[s, p, ", ".join(c.upper() for c in d["pareto"][f"{s}|{p}"]["all_replica_s"]),
                         ", ".join(c.upper() for c in d["pareto"][f"{s}|{p}"]["all_cpu_core_s"])]
                        for s in SERVICES for p in PATTERNS]
    # lampiran: every run, every test, per-cell dispersion and session medians
    T["runs"] = [[r["service"], r["pattern"], r["config"].upper(), str(r["rep"]), num(r["O1_slo_s"]),
                  num(r["O2_error_pct"], 2), num(r["O3_goodput_rps"], 2), num(r["O4_first_up_s"], 1),
                  num(r["O4_first_new_ready_s"], 1), num(r["O5_replica_s"]), num(r["O5_cpu_core_s"], 1)]
                 for r in sorted(res["_runs"], key=lambda r: (SERVICES.index(r["service"]),
                                                              PATTERNS.index(r["pattern"]),
                                                              CONFIGS.index(r["config"]), r["rep"]))]
    T["a2_full"] = [[r["service"], r["pattern"], OUTCOME_ID[r["outcome"]], r["contrast"].upper().replace(" VS ", " vs "),
                     f"{num(r['median_a'], 0 if r['outcome'] == 'O1_slo_s' else 2)} vs "
                     f"{num(r['median_b'], 0 if r['outcome'] == 'O1_slo_s' else 2)}",
                     num(r["U_a"], 1), num(r["p"], 4), num(r["p_holm"], 4) + ("*" if r["significant_0.05"] else ""),
                     num(r["A12_a_gt_b"], 2)] for r in res["A2"]]
    T["dispersion_cells"] = []
    for s in SERVICES:
        for p in PATTERNS:
            for c in AUTOSCALED:
                k = f"{s}|{p}|{c}"
                dd = A4["dispersion"][k]
                T["dispersion_cells"].append([s, p, c.upper(), num(dd["O1_slo_s"]["range"]), num(dd["O1_slo_s"]["mad"]),
                                              num(dd["O2_error_pct"]["range"], 2), num(dd["O2_error_pct"]["mad"], 2),
                                              ", ".join(str(x) for x in A4["anti_phase"][k])])
    T["session_cells"] = []
    for s in SERVICES:
        for p in PATTERNS:
            for c in CONFIGS:
                k = f"{s}|{p}|{c}"
                v = S["cells"][k]
                T["session_cells"].append([s, p, c.upper(),
                                           f"{num(v['O1_slo_s']['session1_median'])} / {num(v['O1_slo_s']['session2_median'])}",
                                           f"{num(v['O2_error_pct']['session1_median'], 2)} / "
                                           f"{num(v['O2_error_pct']['session2_median'], 2)}"])
    # lampiran H (exploratory, after the review): O4 contrasts, HL intervals with the session split, CPU curve
    X = res["X"]
    T["x1"] = [[r["service"], r["pattern"], r["outcome"], r["factor"], signed(r["hl_shift"], 1),
                num(r["p_holm"], 4) + ("*" if r["significant_0.05"] else "")] for r in X["X1"]]
    T["x2"] = []
    for h, s in zip(X["X2"], X["X3"]["contrasts"]):
        dd = 0 if h["outcome"] == "O1_slo_s" else 2
        T["x2"].append([h["service"], h["pattern"], OUTCOME_ID[h["outcome"]], h["contrast"].upper().replace(" VS ", " → "),
                        f"{signed(h['hl_shift'], dd)} [{signed(h['hl_low'], dd)}; {signed(h['hl_high'], dd)}]",
                        signed(s["session1"], dd), signed(s["session2"], dd)])
    T["x5"] = [[s, p["source"], num(p["rate_per_pod"], 2), num(p["cpu_m_per_pod"]),
                num(100 * p["cpu_m_per_pod"] / X["X5"][s]["cpu_request_m"]) + "%"]
               for s in SERVICES for p in sorted(X["X5"][s]["points"], key=lambda p: p["rate_per_pod"])]
    return T


# ── figures ──────────────────────────────────────────────────────────────────

INK, INK2, MUTED, GRID, AXIS, SHADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#efeeea"
ORANGE, BLUE = "#eb6834", "#2a78d6"          # validated pair (dataviz validator, light, white surface)
GOOD, BAD = "#0ca30c", "#d03b3b"             # status: succeeded / failed requests
COLOR = {"b1": "#a3a19b", "b2": "#52514e", "h1": ORANGE, "h2": ORANGE, "h3": BLUE, "k1": BLUE}
MARKER = {"b1": "v", "b2": "P", "h1": "o", "h2": "s", "h3": "D", "k1": "^"}
WIDTH_IN = 14.5 / 2.54                       # A4 text width (left 4 cm, right 2.5 cm)


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "Times New Roman", "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8, "legend.frameon": False,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False,
        "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
        "mathtext.fontset": "custom", "mathtext.rm": "Times New Roman", "mathtext.it": "Times New Roman:italic",
        "mathtext.bf": "Times New Roman:bold", "savefig.dpi": 300, "figure.dpi": 100,
    })
    return plt


def fmt_axis(ax, axis="y", d=0):
    from matplotlib.ticker import FuncFormatter
    f = FuncFormatter(lambda v, _p: num(v, d))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def it(word):
    """Italic word inside a matplotlib label (English terms in the Indonesian text)."""
    return r"$\mathit{" + word + "}$"


def save(fig, path):
    fig.savefig(path, dpi=300, facecolor="white")


def fig_schedule(plt, runs_by_cell, path):
    fig, axes = plt.subplots(3, 2, figsize=(WIDTH_IN, 5.0), sharex=True)
    for j, s in enumerate(SERVICES):
        r = runs_by_cell[(s, "spike", "b2")][1]
        lp = (po.load_json(po.PILOT_DIR / r["run_dir"] / "metadata.json") or {})["load_profile"]
        base, peak = lp["base_rate"], lp["peak_rate"]
        for i, p in enumerate(PATTERNS):
            ax = axes[i][j]
            t, rate, tt = [0.0], [float(base)], 0.0
            for dur, target in po.rate_stages(p, base, peak):
                tt += dur
                t.append(tt)
                rate.append(float(target))
            ax.axvspan(*po.LOAD_WINDOW, color=SHADE, lw=0, zorder=0)
            ax.plot(t, rate, color=INK, lw=1.3, solid_joinstyle="round", zorder=3)
            ax.set_xlim(0, 720)
            ax.set_ylim(0, peak * 1.22)
            ax.set_xticks([0, 120, 240, 360, 480, 600, 720])
            ax.grid(axis="y")
            fmt_axis(ax, "y")
            ax.text(0.015, 0.97, p, transform=ax.transAxes, ha="left", va="top", style="italic")
            if i == 0:
                ax.set_title(s, style="italic", pad=15)
                ax.text(0.5, 1.03, f"dasar {num(base)}, puncak {num(peak)} permintaan/detik", transform=ax.transAxes,
                        ha="center", va="bottom", fontsize=8, color=INK2)
            if i == 2:
                ax.set_xlabel("Waktu k6 (detik)")
    fig.supylabel("Laju kedatangan terjadwal (permintaan/detik)", fontsize=9, x=0.015)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=SHADE, edgecolor="none", label="Jendela analisis (detik ke-120 hingga ke-540)")],
               loc="lower center", ncol=1, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0.02, 0.05, 1, 1))
    save(fig, path)
    plt.close(fig)


def fig_o1(plt, runs_by_cell, A1, path):
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH_IN, 4.5), sharey=True)
    offs = np.array([-0.24, -0.12, 0.0, 0.12, 0.24])
    for i, s in enumerate(SERVICES):
        for j, p in enumerate(PATTERNS):
            ax = axes[i][j]
            for x, c in enumerate(CONFIGS):
                reps = runs_by_cell[(s, p, c)]
                vals = [reps[k]["O1_slo_s"] for k in sorted(reps)]
                ax.scatter(x + offs, vals, marker=MARKER[c], s=13, facecolor=COLOR[c], edgecolor="white",
                           linewidth=0.5, zorder=3)
                m = A1[f"{s}|{p}|{c}"]["O1_slo_s"]["median"]
                ax.hlines(m, x - 0.34, x + 0.34, color=INK, lw=0.9, zorder=2)
            ax.set_xticks(range(len(CONFIGS)), [c.upper() for c in CONFIGS])
            ax.set_xlim(-0.6, len(CONFIGS) - 0.4)
            ax.set_ylim(-15, 440)
            ax.set_yticks([0, 100, 200, 300, 400])
            ax.grid(axis="y")
            fmt_axis(ax, "y")
            ax.tick_params(axis="x", length=0)
            if i == 0:
                ax.set_title(p, style="italic")
            if j == 0:
                ax.set_ylabel("Detik di atas SLO (O1)")
                ax.annotate(s, xy=(-0.42, 0.5), xycoords="axes fraction", rotation=90, ha="center", va="center",
                            style="italic")
    handles = [Line2D([], [], marker="v", ls="", color=COLOR["b1"], label="B1"),
               Line2D([], [], marker="P", ls="", color=COLOR["b2"], label="B2"),
               Line2D([], [], marker="o", ls="", color=ORANGE, label="H1"),
               Line2D([], [], marker="s", ls="", color=ORANGE, label="H2"),
               Line2D([], [], marker="D", ls="", color=BLUE, label="H3"),
               Line2D([], [], marker="^", ls="", color=BLUE, label="K1"),
               Line2D([], [], color=INK, lw=0.9, label="median lima " + it("run"))]
    fig.legend(handles=handles, loc="lower center", ncol=7, bbox_to_anchor=(0.5, 0.0), handletextpad=0.3,
               columnspacing=1.0)
    fig.tight_layout(rect=(0.04, 0.06, 1, 1))
    save(fig, path)
    plt.close(fig)


def run_series(run, service, pattern):
    run_dir = po.PILOT_DIR / run["run_dir"]
    meta = po.load_json(run_dir / "metadata.json") or {}
    lp = meta.get("load_profile") or {}
    t0 = run["t_start"]
    raw = po.Raw.load(run_dir, meta["run_id"])
    sid = raw.scn_id(f"openloop_{pattern}")
    start = raw.e_end - raw.e_ms / 1000.0 - t0
    m = raw.e_scn == sid
    edges = np.arange(0, 721, 10)
    ok = np.histogram(start[m & raw.e_ok], edges)[0] / 10
    bad = np.histogram(start[m & ~raw.e_ok], edges)[0] / 10
    sched_t, sched_r, tt = [0.0], [float(lp["base_rate"])], 0.0
    for dur, target in po.rate_stages(pattern, lp["base_rate"], lp["peak_rate"]):
        tt += dur
        sched_t.append(tt)
        sched_r.append(float(target))
    snaps = aoc.hpa_snapshots(run_dir, service)
    pods = aoc.pod_records(run_dir)
    grid = np.arange(0, 720, 1.0)
    return {"edges": edges, "ok": ok, "bad": bad, "sched_t": sched_t, "sched_r": sched_r,
            "ts": [sn["ts"] - t0 for sn in snaps], "reading": [sn["reading"] for sn in snaps],
            "desired": [sn["desired"] for sn in snaps], "grid": grid,
            "ready": [aoc.ready_count(pods, t0 + g) for g in grid]}


def fig_timeline(plt, columns, path, metric_label, reading_label, mark_peak_starts=False):
    """columns: list of (run, service, config, pattern, column title, target). Rows: load, metric reading, replicas."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import MaxNLocator
    fig, axes = plt.subplots(3, len(columns), figsize=(WIDTH_IN, 5.9), sharex=True, sharey="row")
    xlim = (100, 560)
    ready_color = INK2
    for col, (run, service, config, pattern, title, target) in enumerate(columns):
        ser = run_series(run, service, pattern)
        color = COLOR[config]
        for row in range(3):
            ax = axes[row][col]
            for a, b in po.PEAK_WINDOWS[pattern]:
                ax.axvspan(a, b, color=SHADE, lw=0, zorder=0)
            ax.set_xlim(*xlim)
            ax.grid(axis="y")
        ax = axes[0][col]
        x = ser["edges"][:-1] + 0.8
        ax.bar(x, ser["ok"], width=8.4, align="edge", color=GOOD, alpha=0.45, lw=0, zorder=2)
        ax.bar(x, ser["bad"], width=8.4, align="edge", bottom=ser["ok"], color=BAD, lw=0, zorder=2)
        ax.plot(ser["sched_t"], ser["sched_r"], color=INK, lw=1.0, zorder=3)
        ax.set_ylim(0, max(ser["sched_r"]) * 1.12)
        ax.set_title(title, fontsize=8.5)
        fmt_axis(ax, "y")
        ax = axes[1][col]
        ax.step(ser["ts"], ser["reading"], where="post", color=color, lw=1.3, zorder=3)
        ax.axhline(target, color=MUTED, lw=0.8, ls=(0, (4, 2)), zorder=2)
        ax.text(xlim[0] + 3, target, f"target {num(target)}", ha="left", va="bottom", fontsize=7.5, color=INK2)
        fmt_axis(ax, "y")
        ax = axes[2][col]
        ax.step(ser["ts"], ser["desired"], where="post", color=color, lw=1.4, zorder=3)
        ax.plot(ser["grid"], ser["ready"], color=ready_color, lw=1.0, zorder=4)
        for t in run.get("anti_phase_times_s") or []:
            ax.plot(t, 5.45, marker="v", color=BAD, ms=4, zorder=5, clip_on=False)
        if mark_peak_starts:
            for t in (310, 490):
                ax.plot(t, ser["ready"][int(t)], marker="o", ms=5, markerfacecolor="white",
                        markeredgecolor=INK, markeredgewidth=1.0, zorder=6)
        ax.set_ylim(0, 5.8)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xticks([120, 210, 310, 390, 490, 540])
        ax.set_xlabel("Waktu k6 (detik)")
    axes[0][0].set_ylabel("Permintaan/detik")
    axes[1][0].set_ylabel(metric_label)
    axes[2][0].set_ylabel("Jumlah replika")
    handles = [Line2D([], [], color=INK, lw=1.0, label="laju terjadwal"),
               Patch(facecolor=GOOD, alpha=0.45, label="permintaan berhasil"),
               Patch(facecolor=BAD, label="permintaan gagal"),
               Line2D([], [], color=COLOR[columns[0][2]], lw=1.3, label=reading_label),
               Line2D([], [], color=MUTED, lw=0.8, ls=(0, (4, 2)), label="target"),
               Line2D([], [], color=COLOR[columns[0][2]], lw=1.4, label="replika yang diinginkan HPA"),
               Line2D([], [], color=ready_color, lw=1.0, label=it("pod") + " " + it("Ready")),
               Patch(facecolor=SHADE, label="jendela puncak")]
    if any(c[0].get("anti_phase_times_s") for c in columns):
        handles.append(Line2D([], [], marker="v", ls="", color=BAD, ms=4,
                              label=it("scale") + "-" + it("down") + " saat puncak"))
    if mark_peak_starts:
        handles.append(Line2D([], [], marker="o", ls="", ms=5, markerfacecolor="white", markeredgecolor=INK,
                              label=it("pod") + " " + it("Ready") + " pada awal puncak 2 dan 3"))
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0), handletextpad=0.4,
               columnspacing=1.2)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    save(fig, path)
    plt.close(fig)


# Label offsets (points) for the Pareto panels, chosen by hand for these fixed data so that no label sits on a marker
# or a frontier segment; every label also carries a short leader line to its own point.
LABEL_OFFSETS = {
    "auth-service|gradual": {"B1": (6, 7), "H1": (6, 7), "H2": (-10, 0), "H3": (10, 10), "K1": (10, -10), "B2": (6, 0)},
    "auth-service|spike": {"B1": (6, 7), "H1": (-10, 0), "H2": (-10, 0), "K1": (8, 12), "H3": (-6, -12), "B2": (6, 0)},
    "auth-service|oscillating": {"B1": (6, 7), "H3": (0, 12), "K1": (-10, -10), "H2": (0, -14), "H1": (8, -10),
                                 "B2": (6, 0)},
    "shipping-rate-service|gradual": {"B1": (6, 7), "H1": (6, 7), "H2": (6, 8), "H3": (8, 10), "K1": (6, -10),
                                      "B2": (6, 0)},
    "shipping-rate-service|spike": {"B1": (6, 7), "H1": (-8, 8), "H2": (0, 10), "K1": (8, 12), "H3": (-6, -12),
                                    "B2": (6, 0)},
    "shipping-rate-service|oscillating": {"B1": (6, 7), "H3": (10, 10), "K1": (10, -4), "H2": (-10, 0),
                                          "H1": (6, -10), "B2": (6, 0)},
}


def label_points(ax, offsets, pts):
    for name, (x, y) in pts.items():
        dx, dy = offsets[name]
        ha = "left" if dx > 0 else "right" if dx < 0 else "center"
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=7.5,
                    color=INK, zorder=6,
                    arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.5, "shrinkA": 1, "shrinkB": 4})


def fig_pareto(plt, A5, path):
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH_IN, 4.9), sharex=True, sharey=True)
    for i, s in enumerate(SERVICES):
        for j, p in enumerate(PATTERNS):
            ax = axes[i][j]
            v = A5[f"{s}|{p}"]
            pts, nd = v["points"], v["non_dominated"]["replica_s"]
            front = sorted(nd, key=lambda c: pts[c]["replica_s"])
            fx, fy = [], []
            for k, c in enumerate(front):
                if k:
                    fx.append(pts[c]["replica_s"])
                    fy.append(fy[-1])
                fx.append(pts[c]["replica_s"])
                fy.append(pts[c]["O1"])
            ax.plot(fx, fy, color=INK2, lw=0.8, zorder=2)
            for c in CONFIGS:
                filled = c in nd
                ax.scatter(pts[c]["replica_s"], pts[c]["O1"], marker=MARKER[c], s=30,
                           facecolor=COLOR[c] if filled else "white", edgecolor=COLOR[c], linewidth=1.1, zorder=4)
            ax.set_xlim(0, 2650)
            ax.set_ylim(-70, 470)
            ax.set_xticks([0, 1000, 2000])
            ax.set_yticks([0, 100, 200, 300, 400])
            ax.grid(True)
            fmt_axis(ax, "x")
            fmt_axis(ax, "y")
            if i == 0:
                ax.set_title(p, style="italic")
            if j == 0:
                ax.set_ylabel("Detik di atas SLO (median)")
                ax.annotate(s, xy=(-0.45, 0.5), xycoords="axes fraction", rotation=90, ha="center", va="center",
                            style="italic")
            if i == 1:
                ax.set_xlabel("Replika-detik " + it("pod") + " " + it("Ready"))
    handles = [Line2D([], [], marker="o", ls="", markerfacecolor=INK2, markeredgecolor=INK2, label="tidak terdominasi"),
               Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=INK2, label="terdominasi"),
               Line2D([], [], color=INK2, lw=0.8, label="batas Pareto"),
               Line2D([], [], marker="v", ls="", color=COLOR["b1"], label="B1"),
               Line2D([], [], marker="P", ls="", color=COLOR["b2"], label="B2"),
               Line2D([], [], marker="o", ls="", color=ORANGE, label="H1"),
               Line2D([], [], marker="s", ls="", color=ORANGE, label="H2"),
               Line2D([], [], marker="D", ls="", color=BLUE, label="H3"),
               Line2D([], [], marker="^", ls="", color=BLUE, label="K1")]
    fig.legend(handles=handles, loc="lower center", ncol=9, bbox_to_anchor=(0.5, 0.0), handletextpad=0.25,
               columnspacing=0.8)
    fig.tight_layout(rect=(0.04, 0.06, 1, 1))
    for i, s in enumerate(SERVICES):
        for j, p in enumerate(PATTERNS):
            pts = A5[f"{s}|{p}"]["points"]
            label_points(axes[i][j], LABEL_OFFSETS[f"{s}|{p}"],
                         {c.upper(): (pts[c]["replica_s"], pts[c]["O1"]) for c in CONFIGS})
    save(fig, path)
    plt.close(fig)


def figures(res, runs, out_dir):
    plt = setup_matplotlib()
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    cells = defaultdict(dict)
    for r in runs:
        cells[(r["service"], r["pattern"], r["config"])][r["rep"]] = r
    fig_schedule(plt, cells, fig_dir / "gambar_4_1_jadwal_beban.png")
    fig_o1(plt, cells, res["A1"], fig_dir / "gambar_4_2_o1_per_run.png")
    s, p = "auth-service", "oscillating"
    cols = []
    for rep in (1, 2):
        r = cells[(s, p, "h2")][rep]
        cols.append((r, s, "h2", p, f"H2, repetisi {rep}: O1 {num(r['O1_slo_s'])} detik, " + it("error") + " "
                     + num(r["O2_error_pct"], 2) + "%", CPU_TARGET["h2"]))
    fig_timeline(plt, cols, fig_dir / "gambar_4_3_h2_oscillating.png",
                 "CPU (% dari " + it("request") + ")", "pembacaan CPU oleh HPA (% dari " + it("request") + ")")
    cols = []
    for c in ("h3", "k1"):
        r = cells[(s, p, c)][1]
        cols.append((r, s, c, p, f"{c.upper()}, repetisi 1: O1 {num(r['O1_slo_s'])} detik, " + it("error") + " "
                     + num(r["O2_error_pct"], 2) + "%", THRESHOLD[s]))
    fig_timeline(plt, cols, fig_dir / "gambar_4_4_h3_k1_oscillating.png",
                 "Permintaan/detik per " + it("pod"), "pembacaan laju permintaan per " + it("pod"),
                 mark_peak_starts=True)
    fig_pareto(plt, res["A5"], fig_dir / "gambar_4_5_pareto.png")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--results", default=str(PART12 / "results.json"))
    ap.add_argument("--out", default=str(po.PILOT_DIR / "analysis" / "thesis"))
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    runs, res = data["runs"], data["analyses"]
    res["_runs"] = runs
    d = derive(res, runs)
    d["tables"] = tables(res, d)
    (out_dir / "derived.json").write_text(json.dumps(d, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    if not args.no_figures:
        figures(res, runs, out_dir)
    print(f"{len(runs)} runs -> {out_dir}")


if __name__ == "__main__":
    main()
