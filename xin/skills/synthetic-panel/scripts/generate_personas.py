#!/usr/bin/env python3
"""synthetic-panel Step 2: 从 panel-config.json 确定性展开 N 个 persona 实例并分批。

用法:
    uv run generate_personas.py --config RUN_DIR/panel-config.json --out-dir RUN_DIR

输出:
    RUN_DIR/personas.jsonl          每行一个 persona 实例
    RUN_DIR/batches/batch-NNN.json  访谈 agent 的输入批次
    stdout                          batch 清单 JSON（供主对话构造 Workflow args）

设计约束:
    - 全确定性（seed 驱动），同 config 重跑结果逐字节一致。
    - 价格变体在每个 archetype 内部 round-robin，保证分群×价格正交（每群内各价格 n 差 ≤1）。
"""
import argparse
import json
import random
import sys
from pathlib import Path


def weighted_choice(rng: random.Random, pairs):
    """pairs: [[value, weight], ...] -> value"""
    values = [p[0] for p in pairs]
    weights = [float(p[1]) for p in pairs]
    return rng.choices(values, weights=weights, k=1)[0]


def expand_archetype(rng: random.Random, arch: dict, count: int, price_variants: list, start_idx: int):
    out = []
    for j in range(count):
        attrs = {}
        lo, hi = arch["age_range"]
        attrs["年龄"] = rng.randint(int(lo), int(hi))
        if arch.get("genders"):
            attrs["性别"] = weighted_choice(rng, arch["genders"])
        if arch.get("regions"):
            attrs["地区"] = weighted_choice(rng, arch["regions"])
        if arch.get("income_bands"):
            attrs["收入档"] = weighted_choice(rng, arch["income_bands"])
        for name, rng_pair in (arch.get("numeric_attrs") or {}).items():
            attrs[name] = rng.randint(int(rng_pair[0]), int(rng_pair[1]))
        for name, pairs in (arch.get("categorical_attrs") or {}).items():
            attrs[name] = weighted_choice(rng, pairs)
        pains = arch.get("pains") or []
        picked_pains = rng.sample(pains, k=min(2, len(pains))) if pains else []
        price = price_variants[j % len(price_variants)]
        out.append({
            "id": f"P{start_idx + j:04d}",
            "archetype_id": arch["id"],
            "archetype_name": arch["name"],
            "attrs": attrs,
            "pains": picked_pains,
            "context": arch.get("context", ""),
            "price_label": price["label"],
            "price_value": price["value"],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    (out_dir / "batches").mkdir(parents=True, exist_ok=True)

    n = int(cfg["n_personas"])
    batch_size = int(cfg.get("batch_size", 20))
    seed = int(cfg.get("seed", 42))
    price_variants = cfg["price_variants"]
    archetypes = cfg["archetypes"]
    if not archetypes:
        print("ERROR: archetypes 为空", file=sys.stderr)
        sys.exit(1)

    rng = random.Random(seed)

    # 按 weight 精确配额（余数给 weight 最大的群）
    total_w = sum(float(a.get("weight", 1)) for a in archetypes)
    quotas = [int(n * float(a.get("weight", 1)) / total_w) for a in archetypes]
    remainder = n - sum(quotas)
    order = sorted(range(len(archetypes)),
                   key=lambda i: float(archetypes[i].get("weight", 1)), reverse=True)
    for k in range(remainder):
        quotas[order[k % len(order)]] += 1

    personas = []
    idx = 1
    for arch, quota in zip(archetypes, quotas):
        personas.extend(expand_archetype(rng, arch, quota, price_variants, idx))
        idx += quota

    with (out_dir / "personas.jsonl").open("w", encoding="utf-8") as f:
        for p in personas:
            f.write(json.dumps(p, ensure_ascii=False, separators=(",", ":")) + "\n")

    shuffled = personas[:]
    rng.shuffle(shuffled)  # 批内混群，避免单 agent 风格同化单一群
    batches = []
    for b, start in enumerate(range(0, len(shuffled), batch_size), start=1):
        bid = f"batch-{b:03d}"
        bfile = out_dir / "batches" / f"{bid}.json"
        bfile.write_text(json.dumps(
            {"batch_id": bid, "personas": shuffled[start:start + batch_size]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        batches.append({"id": bid, "file": str(bfile)})

    summary = {
        "n_personas": len(personas),
        "n_batches": len(batches),
        "quotas": {a["id"]: q for a, q in zip(archetypes, quotas)},
        "price_variants": [p["label"] for p in price_variants],
        "batches": batches,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
