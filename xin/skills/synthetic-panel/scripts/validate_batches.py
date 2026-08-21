#!/usr/bin/env python3
"""synthetic-panel Step 4: 访谈产出覆盖校验 + 已知损坏模式自愈（零侥幸门控）。

用法:
    uv run validate_batches.py --personas RUN_DIR/personas.jsonl --out-dir RUN_DIR/out [--no-repair]

自愈：LLM agent 常在 review 文本里写未转义英文双引号导致 JSON 失效（实测 12/50 批，
2026-06-13 dogfood）。parse 失败时用结构正则提取 persona_id/review 对，重写为合法 JSON
（原文件备份为 .raw）。内容零改动，仅修转义。

exit 0 = 100% 覆盖；exit 2 = 有缺失，stdout 输出缺失明细 JSON（含需重跑的 batch 列表）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

PAIR_RE = re.compile(
    r'"persona_id"\s*:\s*"(P\d+)"\s*,\s*"review"\s*:\s*"(.*?)"\s*\}\s*(?=,|\])',
    re.DOTALL)


def try_repair(bf: Path) -> dict | None:
    """对 parse 失败的批次文件做结构化提取修复。成功返回修复后 dict，失败返回 None。"""
    raw = bf.read_text(encoding="utf-8")
    pairs = PAIR_RE.findall(raw)
    if not pairs:
        return None
    reviews = []
    for pid, text in pairs:
        try:
            text = json.loads(f'"{text}"')  # 合法转义序列正常解码
        except json.JSONDecodeError:
            text = text.replace('\\"', '"')  # 混合转义：还原已转义引号，裸引号保持原样
        reviews.append({"persona_id": pid, "review": text})
    m = re.search(r'"batch_id"\s*:\s*"([^"]+)"', raw)
    data = {"batch_id": m.group(1) if m else bf.stem, "reviews": reviews}
    bf.with_suffix(".raw").write_text(raw, encoding="utf-8")
    bf.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--personas", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--no-repair", action="store_true")
    args = ap.parse_args()

    expected = {}
    with open(args.personas, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            expected[p["id"]] = p

    got = {}
    malformed = []
    repaired = []
    out_dir = Path(args.out_dir)
    for bf in sorted(out_dir.glob("batch-*.json")):
        data = None
        try:
            data = json.loads(bf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            if not args.no_repair:
                data = try_repair(bf)
            if data is None:
                malformed.append({"file": bf.name, "reason": f"parse-error: {e}"})
                continue
            repaired.append({"file": bf.name, "recovered": len(data["reviews"])})
        for r in data.get("reviews", []):
            pid, review = r.get("persona_id"), (r.get("review") or "").strip()
            if pid and review and len(review) >= 20:
                got[pid] = review
            else:
                malformed.append({"file": bf.name, "persona_id": pid,
                                  "reason": "empty-or-too-short"})

    missing_ids = sorted(set(expected) - set(got))
    # 缺失 persona → 找回其所属 batch 文件（按 batches/ 目录反查）
    batches_dir = out_dir.parent / "batches"
    missing_batches = {}
    if missing_ids and batches_dir.is_dir():
        miss = set(missing_ids)
        for bf in sorted(batches_dir.glob("batch-*.json")):
            data = json.loads(bf.read_text(encoding="utf-8"))
            ids = {p["id"] for p in data["personas"]}
            if ids & miss:
                missing_batches[data["batch_id"]] = str(bf)

    report = {
        "expected": len(expected),
        "got": len(got),
        "coverage_pct": round(100.0 * len(got) / max(1, len(expected)), 2),
        "repaired": repaired,
        "missing_ids": missing_ids,
        "missing_batches": [{"id": k, "file": v} for k, v in missing_batches.items()],
        "malformed": malformed,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    sys.exit(0 if not missing_ids else 2)


if __name__ == "__main__":
    main()
