#!/usr/bin/env python3
"""synthetic-panel Step 5: SSR 语义评分（官方公式逐行对齐 pymc-labs/semantic-similarity-rating）。

用法:
    uv run --with sentence-transformers --with numpy score_ssr.py \
        --personas RUN_DIR/personas.jsonl --reviews-dir RUN_DIR/out \
        --anchors SKILL_DIR/templates/anchors-zh.json --run-dir RUN_DIR \
        [--extra-segments "地区,收入档"] [--temperature 1.0] [--epsilon 0.0] \
        [--model BAAI/bge-small-zh-v1.5]

算法（arXiv 2510.08338 §SSR + 官方 compute.py）:
    sim       = (1 + cosine) / 2                      # 缩放到 [0,1]
    numerator = sim - sim_min(行)； ε 加在最小位
    denom     = sim_sum - K*sim_min + ε
    pmf       = numerator / denom                     # 每个锚点集一个 pmf
    pmf       = mean(各锚点集 pmf)                     # 论文做法：多集平均
    pmf       = pmf^(1/T) 归一化                       # T=1 缺省（论文设置）

输出:
    RUN_DIR/scores.jsonl       每 persona: pmf + expected(1-5) + argmax
    RUN_DIR/aggregates.json    总体/分群/价格需求曲线/弹性（报告唯一数字来源）
    RUN_DIR/quotes.json        每 archetype top/bottom 引文
    RUN_DIR/themes-input/<archetype>.jsonl   主题提取 agent 输入
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np


def similarities_to_pmf(sim: np.ndarray, epsilon: float) -> np.ndarray:
    """官方 SSR 公式。sim: (N, K) 已缩放相似度。"""
    sim_min = sim.min(axis=1, keepdims=True)
    sim_sum = sim.sum(axis=1, keepdims=True)
    numerator = sim - sim_min
    if epsilon > 0:
        min_idx = np.argmin(sim, axis=1)
        numerator[np.arange(sim.shape[0]), min_idx] += epsilon
    k = sim.shape[1]
    denominator = sim_sum - k * sim_min + epsilon
    return numerator / denominator


def scale_pmfs(pmfs: np.ndarray, temperature: float) -> np.ndarray:
    if temperature == 1.0:
        return pmfs
    if temperature <= 0:
        out = np.zeros_like(pmfs)
        out[np.arange(pmfs.shape[0]), np.argmax(pmfs, axis=1)] = 1.0
        return out
    scaled = np.power(np.clip(pmfs, 1e-12, None), 1.0 / temperature)
    return scaled / scaled.sum(axis=1, keepdims=True)


def agg_block(rows):
    """rows: list of dicts with pmf/expected -> 汇总块"""
    pmfs = np.array([r["pmf"] for r in rows])
    exps = np.array([r["expected"] for r in rows])
    top2 = float(pmfs[:, 3:].sum(axis=1).mean())  # P(4)+P(5) 的均值 = top-2-box
    return {
        "n": len(rows),
        "mean_expected": round(float(exps.mean()), 3),
        "std_expected": round(float(exps.std()), 3),
        "pmf": [round(float(x), 4) for x in pmfs.mean(axis=0)],
        "top2box_pct": round(100 * top2, 2),
        "argmax_dist": [int((np.argmax(pmfs, axis=1) == i).sum()) for i in range(pmfs.shape[1])],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--personas", required=True)
    ap.add_argument("--reviews-dir", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--extra-segments", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=0.0)
    ap.add_argument("--model", default="BAAI/bge-large-zh-v1.5")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    personas = {}
    with open(args.personas, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            personas[p["id"]] = p

    reviews = {}
    for bf in sorted(Path(args.reviews_dir).glob("batch-*.json")):
        data = json.loads(bf.read_text(encoding="utf-8"))
        for r in data.get("reviews", []):
            if r.get("persona_id") and (r.get("review") or "").strip():
                reviews[r["persona_id"]] = r["review"].strip()

    missing = sorted(set(personas) - set(reviews))
    if missing:
        print(f"ERROR: 覆盖不全，缺 {len(missing)} 个 persona（先跑 validate_batches.py 重补）",
              file=sys.stderr)
        print(json.dumps(missing[:20]), file=sys.stderr)
        sys.exit(2)

    anchor_cfg = json.loads(Path(args.anchors).read_text(encoding="utf-8"))
    anchor_sets = anchor_cfg["sets"]  # [{id, statements:[5 条，1→5 级]}]
    k_points = len(anchor_sets[0]["statements"])

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(args.model)
    pids = sorted(reviews)
    texts = [reviews[pid] for pid in pids]
    emb_r = model.encode(texts, normalize_embeddings=True, show_progress_bar=False,
                         batch_size=64)

    set_pmfs = []
    for aset in anchor_sets:
        emb_a = model.encode(aset["statements"], normalize_embeddings=True,
                             show_progress_bar=False)
        sim = (1.0 + emb_r @ emb_a.T) / 2.0  # 官方 (1+cos)/2 缩放
        set_pmfs.append(similarities_to_pmf(sim, args.epsilon))
    pmfs = scale_pmfs(np.mean(set_pmfs, axis=0), args.temperature)
    expected = pmfs @ np.arange(1, k_points + 1)

    rows = []
    with (run_dir / "scores.jsonl").open("w", encoding="utf-8") as f:
        for i, pid in enumerate(pids):
            p = personas[pid]
            row = {
                "persona_id": pid,
                "archetype_id": p["archetype_id"],
                "price_label": p["price_label"],
                "price_value": p["price_value"],
                "attrs": p["attrs"],
                "pmf": [round(float(x), 4) for x in pmfs[i]],
                "expected": round(float(expected[i]), 3),
                "argmax": int(np.argmax(pmfs[i]) + 1),
                "review": reviews[pid],
            }
            rows.append(row)
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    # ---- 聚合 ----
    def group_by(key_fn):
        groups = {}
        for r in rows:
            groups.setdefault(key_fn(r), []).append(r)
        return {k: agg_block(v) for k, v in sorted(groups.items())}

    aggregates = {
        "method": "SSR (arXiv 2510.08338, official formula)",
        "embedding_model": args.model,
        "anchor_sets": [a["id"] for a in anchor_sets],
        "temperature": args.temperature,
        "epsilon": args.epsilon,
        "n": len(rows),
        "overall": agg_block(rows),
        "by_archetype": group_by(lambda r: r["archetype_id"]),
        "by_price": group_by(lambda r: r["price_label"]),
        "archetype_x_price": {
            aid: group_by_inner
            for aid, group_by_inner in (
                (aid, {pl: agg_block(sub) for pl, sub in sorted(
                    _group(rows_a, lambda r: r["price_label"]).items())})
                for aid, rows_a in sorted(_group(rows, lambda r: r["archetype_id"]).items())
            )
        },
    }
    for seg in [s.strip() for s in args.extra_segments.split(",") if s.strip()]:
        aggregates[f"by_{seg}"] = group_by(lambda r, s=seg: str(r["attrs"].get(s, "未知")))

    # 需求曲线 + 对数线性弹性拟合（top2box ~ a + b*ln(price)）
    curve = []
    for pl, block in aggregates["by_price"].items():
        pv = next(r["price_value"] for r in rows if r["price_label"] == pl)
        curve.append({"price_label": pl, "price_value": pv,
                      "top2box_pct": block["top2box_pct"],
                      "mean_expected": block["mean_expected"], "n": block["n"]})
    curve.sort(key=lambda c: c["price_value"])
    aggregates["demand_curve"] = curve
    if len(curve) >= 2 and all(c["price_value"] > 0 for c in curve):
        x = np.log([c["price_value"] for c in curve])
        y = np.array([c["top2box_pct"] for c in curve])
        b, a = np.polyfit(x, y, 1)
        pred = a + b * x
        ss_res, ss_tot = float(((y - pred) ** 2).sum()), float(((y - y.mean()) ** 2).sum())
        aggregates["price_fit"] = {
            "model": "top2box_pct = a + b*ln(price)",
            "a": round(float(a), 3), "b_per_ln_price": round(float(b), 3),
            "r2": round(1 - ss_res / ss_tot, 3) if ss_tot > 0 else None,
        }

    (run_dir / "aggregates.json").write_text(
        json.dumps(aggregates, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- 引文 + 主题输入 ----
    quotes = {}
    ti_dir = run_dir / "themes-input"
    ti_dir.mkdir(exist_ok=True)
    for aid, rows_a in sorted(_group(rows, lambda r: r["archetype_id"]).items()):
        srt = sorted(rows_a, key=lambda r: r["expected"])
        pick = lambda rs: [{"persona_id": r["persona_id"], "expected": r["expected"],
                            "price_label": r["price_label"], "review": r["review"]}
                           for r in rs]
        quotes[aid] = {"bottom": pick(srt[:3]), "top": pick(srt[-3:][::-1])}
        with (ti_dir / f"{aid}.jsonl").open("w", encoding="utf-8") as f:
            for r in srt:
                f.write(json.dumps({
                    "persona_id": r["persona_id"], "expected": r["expected"],
                    "price_label": r["price_label"], "attrs": r["attrs"],
                    "review": r["review"]}, ensure_ascii=False,
                    separators=(",", ":")) + "\n")
    (run_dir / "quotes.json").write_text(
        json.dumps(quotes, ensure_ascii=False, indent=1), encoding="utf-8")

    # 分布健全红旗
    flags = []
    overall_pmf = aggregates["overall"]["pmf"]
    if max(overall_pmf) > 0.8:
        flags.append(f"单档占比 {max(overall_pmf):.0%} > 80%：检查锚点语言/温度")
    print(json.dumps({"n": len(rows), "overall": aggregates["overall"],
                      "demand_curve": curve, "red_flags": flags},
                     ensure_ascii=False, indent=1))


def _group(rows, key_fn):
    g = {}
    for r in rows:
        g.setdefault(key_fn(r), []).append(r)
    return g


if __name__ == "__main__":
    main()
