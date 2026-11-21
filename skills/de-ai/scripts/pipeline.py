#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""De-AI Pipeline: cross-family multi-engine tournament plus deterministic regex rewriting.

Flow: collect blocks -> probe engines -> run chains -> clean every candidate -> validate ->
score -> pick -> write back -> export. Every intermediate result lands in --work, so a rerun
with the same arguments reuses finished translations.
"""

import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

import chains as chainmod
import docio
import rules
import score as scoremod

LEVEL_CHAINS = {"light": 1, "standard": 3, "deep": 4}


def load_json(path: str, default=None):
    if not path:
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cache_key(*parts: str) -> str:
    return hashlib.sha1("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser(description="De-AI Pipeline")
    ap.add_argument("--docx", "--input", dest="docx", required=True,
                    help="Input file: .docx / .md / .markdown / .txt")
    ap.add_argument("--out", "--out-docx", dest="out", required=True,
                    help="Output file; the extension decides the format")
    ap.add_argument("--out-pdf", default="", help=".docx only; converted with LibreOffice or Word")
    ap.add_argument("--src-lang", default="auto", choices=["auto", "en", "zh"])
    ap.add_argument("--dst-lang", default="same", choices=["same", "en", "zh"])
    ap.add_argument("--level", default="standard", choices=list(LEVEL_CHAINS))
    ap.add_argument("--min-words", type=int, default=30)
    ap.add_argument("--config", default=str(Path(__file__).parent / "config_default.json"))
    ap.add_argument("--terms", default="", help="JSON: [[pattern, replacement], ...]")
    ap.add_argument("--work", default="", help="Work directory, defaults to <out>.work")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--skip-preflight", action="store_true", help="Skip engine probing")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_json(args.config, {})
    if args.seed is not None:
        cfg["seed"] = args.seed
    seed = int(cfg.get("seed", 42))
    terms = [tuple(x) for x in load_json(args.terms, [])] or rules.DEFAULT_TERM_FIXES
    sel = cfg.get("selection", {})
    require_validation = bool(sel.get("require_validation", True))
    min_sim_cfg = sel.get("min_sim", {"en": 0.99, "zh": 0.75})
    min_div = float(sel.get("min_divergence", 0.10))
    forbidden = list(cfg.get("forbidden", []))

    if Path(args.out).resolve() == Path(args.docx).resolve():
        print("ERROR: --out points at the input file. The original is never overwritten; "
              "pick a different output path.")
        return 1

    work = Path(args.work or (args.out + ".work"))
    (work / "units").mkdir(parents=True, exist_ok=True)

    try:
        document = docio.load_document(args.docx)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.out_pdf and document.kind != "docx":
        print("ERROR: --out-pdf supports .docx input only.")
        return 1
    print(f"Input format: {document.kind}")

    targets, skipped = document.units(min_words=args.min_words)
    print(f"Targets: {len(targets)} | skipped: {len(skipped)}")
    if not targets:
        print("No rewritable block. Check --min-words, or read the skip reasons.")
        return 1
    if not terms:
        print("[INFO] No --terms given, so no term replacement this run "
              "(auto-extracted identifiers are still protected).")

    if args.src_lang == "auto":
        langs = {chainmod.detect_lang(t["text"]) for t in targets}
        src = "zh" if langs == {"zh"} else "en"
    else:
        src = args.src_lang
    dst = src if args.dst_lang == "same" else args.dst_lang
    min_sim = float(min_sim_cfg.get(dst, 0.99)) if isinstance(min_sim_cfg, dict) else float(min_sim_cfg)
    cross = src != dst

    print(f"Selecting chains ({src} -> {dst}), first usable engine per hop")
    all_chains, chain_log, degradations = chainmod.build_chains(
        src, dst, cfg.get("chain_templates"), probe=not args.skip_preflight)
    for line in chain_log:
        print(line)
    all_chains = all_chains[: LEVEL_CHAINS[args.level]]
    print(f"  {len(all_chains)} usable chain(s)")
    if degradations:
        print(f"  [WARN] {len(degradations)} hop(s) downgraded to tier2, quality may drop:")
        for d in degradations:
            print(f"    {d}")

    if not all_chains:
        print("\nNo usable chain. Inside mainland China usually only iciba / qqTranSmart / youdao work;")
        print("elsewhere usually only reverso / bing / google do.")
        print("Replace chain_templates with engines you can reach, for example:")
        print('  [[["reverso","de"],["bing","fr"],["reverso",null]],')
        print('   [["bing","ja"],["reverso","de"],["reverso",null]]]')
        return 3

    print(f"Language: {src} -> {dst} | chains: {len(all_chains)}")
    for name, _ in all_chains:
        print(f"  {name}")

    if args.dry_run:
        json.dump({"targets": targets, "skipped": skipped,
                   "chains": [n for n, _ in all_chains], "src": src, "dst": dst},
                  open(work / "plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Dry run written: {work / 'plan.json'}")
        return 0

    protected = scoremod.extract_terms([t["text"] for t in targets]) if src == dst else []
    if protected:
        print(f"Auto-protected terms ({len(protected)}): {', '.join(protected[:8])}"
              + (" …" if len(protected) > 8 else ""))

    scorer = scoremod.build_scorer(dst)
    series = rules.RuleContext(cfg, seed=seed).series
    cfg_hash = cache_key(json.dumps(cfg, sort_keys=True), str(seed))

    units_log, failed = [], []
    t_start = time.time()

    for n, rec in enumerate(targets, 1):
        t0 = time.time()
        unit_id = f"P{rec['idx']:04d}"
        ctx = rules.RuleContext(cfg, seed=int(hashlib.sha1(f"{seed}:{unit_id}".encode()).hexdigest()[:8], 16))
        ctx.series = series
        if cross:
            ref_score, ref_feats, ref_hidden = 0.0, {}, None
        else:
            ref_score, ref_feats, ref_hidden = scorer.score(rec["text"])
        candidates = []

        for cname, hops in all_chains:
            key = cache_key(rec["text"], cname, src, dst, cfg_hash)
            cpath = work / "units" / f"{key}.json"
            cached = load_json(str(cpath), None) if cpath.exists() else None
            if cached is not None:
                raw, err = cached.get("raw"), cached.get("error")
            else:
                raw, err = chainmod.translate_chain(rec["text"], src, hops)
                json.dump({"unit": unit_id, "chain": cname, "src": src, "dst": dst,
                           "raw": raw, "error": err},
                          open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            if err or not raw:
                candidates.append({"chain": cname, "status": "translate-failed", "error": err})
                continue

            cleaned = rules.postprocess(raw, rec["text"], dst, ctx, terms)
            problems = scoremod.validate(rec["text"], cleaned, terms, dst, forbidden, protected, cross)
            sc, feats, hidden = scorer.score(cleaned, ref_text=rec["text"])
            if cross:
                sim = None
            elif hidden is not None:
                sim = scorer.fidelity(hidden, ref_hidden)
            else:
                sim = scorer.fidelity(rec["text"], cleaned)
            candidates.append({
                "chain": cname, "status": "ok", "raw": raw, "clean": cleaned,
                "score": round(sc, 4), "sim": sim,
                "base": feats.get("_base"), "penalty": feats.get("_penalty"),
                "features": {k: v for k, v in feats.items() if not k.startswith("_")},
                "validation": problems,
                "divergence": None if cross else round(scoremod.trigram_jaccard(cleaned, rec["text"]), 4),
            })

        ok = [c for c in candidates if c.get("status") == "ok"]
        usable = [c for c in ok if not c["validation"]] if require_validation else ok
        good_sim = usable if cross else [c for c in usable if c["sim"] is not None and c["sim"] >= min_sim]
        pool = good_sim or usable
        chosen, note = None, ""
        if pool:
            pool.sort(key=lambda c: (0 if (cross or c["divergence"] >= min_div) else 1, c["score"]))
            chosen = pool[0]
            if not good_sim:
                note = f"replaced-low-sim(<{min_sim})"
            elif not cross and chosen["divergence"] < min_div:
                note = f"replaced-min-change(<{min_div})"
            elif not cross and chosen["score"] > ref_score:
                note = f"replaced-worse(+{chosen['score'] - ref_score:.3f})"
        elif ok:
            note = "all-candidates-failed-validation"
            failed.append({"unit": unit_id, "reason": note,
                           "detail": {c["chain"]: c["validation"] for c in ok}})
        else:
            note = "all-chains-failed"
            failed.append({"unit": unit_id, "reason": note,
                           "detail": {c["chain"]: c.get("error") for c in candidates}})

        units_log.append({
            "unit": unit_id, "idx": rec["idx"], "orig": rec["text"],
            "orig_score": round(ref_score, 4), "status": note or "replaced",
            "orig_base": ref_feats.get("_base"), "orig_penalty": ref_feats.get("_penalty"),
            "min_sim": min_sim,
            "chosen_chain": chosen["chain"] if chosen else "",
            "chosen_score": chosen["score"] if chosen else None,
            "chosen_base": chosen.get("base") if chosen else None,
            "chosen_penalty": chosen.get("penalty") if chosen else None,
            "chosen_sim": chosen["sim"] if chosen else None,
            "chosen_divergence": chosen["divergence"] if chosen else None,
            "final": chosen["clean"] if chosen else rec["text"],
            "candidates": candidates,
        })

        if chosen:
            document.set_text(rec["idx"], chosen["clean"])
            div_s = "—" if chosen["divergence"] is None else f"{chosen['divergence']:.3f}"
            sim_s = "—" if chosen["sim"] is None else f"{chosen['sim']:.3f}"
            print(f"[{n:03d}/{len(targets):03d}] {unit_id} | {ref_score:.3f}->{chosen['score']:.3f} "
                  f"| div={div_s} sim={sim_s} | {chosen['chain']} "
                  f"({time.time()-t0:.1f}s)")
        else:
            print(f"[{n:03d}/{len(targets):03d}] {unit_id} | KEPT ORIGINAL ({note}) ({time.time()-t0:.1f}s)")

    document.save(args.out)
    if args.out_pdf:
        try:
            engine = docio.export_pdf(args.out, args.out_pdf)
            print(f"PDF converted by {engine}; metadata scrubbed")
        except Exception as exc:
            print(f"[WARN] PDF export failed: {exc}")
            return 2

    report = {
        "input": args.docx, "output": args.out, "kind": document.kind,
        "src": src, "dst": dst, "level": args.level, "seed": seed,
        "chains": [n for n, _ in all_chains],
        "elapsed_sec": round(time.time() - t_start, 1),
        "units": units_log, "failed": failed, "skipped": skipped,
    }
    json.dump(report, open(work / "result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    write_report(work / "report.md", report, dst)

    replaced = sum(1 for u in units_log if u["status"].startswith("replaced"))
    print(f"\nReplaced {replaced}/{len(targets)} | failed {len(failed)} | {report['elapsed_sec']}s")
    print(f"Artifacts: {work}")
    return 0 if not failed else 2


def write_report(path: Path, report: Dict, dst: str) -> None:
    lines = [
        "# De-AI report",
        "",
        f"- Direction: {report['src']} -> {report['dst']} ({report['level']})",
        f"- Seed: {report['seed']}  elapsed: {report['elapsed_sec']}s",
        f"- Chains: {', '.join(report['chains'])}",
        f"- Blocks: {len(report['units'])}  failed: {len(report['failed'])}  skipped: {len(report['skipped'])}",
        "",
        "## Per-block result",
        "",
        ("Cross-language ({} -> {}): the before score, 3-gram overlap and similarity are not "
         "comparable and are left blank.".format(report["src"], report["dst"])
         if report["src"] != report["dst"]
         else "Before = sentence score + penalty, after uses the same split; both columns can "
              "exceed 1 and neither is a percentage."),
        "",
        "| Block | Status | Chain | Before | After | 3-gram overlap | Similarity |",
        "|---|---|---|---|---|---|---|",
    ]
    for u in report["units"]:
        lines.append(
            f"| {u['unit']} | {u['status']} | {u['chosen_chain'] or '-'} "
            f"| {str(u['orig_base']) + '+' + str(u['orig_penalty']) if u['orig_base'] is not None else '—'} "
            f"| {str(u['chosen_base']) + '+' + str(u['chosen_penalty']) if u['chosen_base'] is not None else '—'} "
            f"| {u['chosen_divergence'] if u['chosen_divergence'] is not None else '—'} "
            f"| {round(u['chosen_sim'], 4) if u['chosen_sim'] is not None else '—'} |")
    if report["failed"]:
        lines += ["", "## Blocks kept as-is", ""]
        for f in report["failed"]:
            lines.append(f"- `{f['unit']}` {f['reason']}")
    if report["skipped"]:
        lines += ["", "## Skipped blocks", "", "| Block | Reason | Opening |", "|---|---|---|"]
        for s in report["skipped"]:
            lines.append(f"| {s['idx']} | {s['reason']} | {s['text'][:40]} |")
    if dst == "zh":
        lines += ["", "## Chinese metrics (measured only, never rewritten)", "",
                  "Character density, longest attributive clause and parallelism density live in `features` "
                  "inside `result.json`; all three need a human."]
    lines += ["", "## Notes", "",
              "The after score ranks candidates; it is not a detector probability. A lower 3-gram overlap "
              "means the word order moved further from the source.",
              "Only candidates that pass the number, citation, identifier, term and length checks can be chosen."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted")
        raise SystemExit(130)
