# -*- coding: utf-8 -*-
"""Cross-family translation chains.

A chain is a list of hops. Each hop declares a language plus a tier1 and a tier2 engine list.
Before a run, every hop is probed: tier1 (the engines validated by the original experiment) is
tried first, tier2 (the general pool) only when tier1 is unreachable.

tier1 assignment follows the measured result: mid hops use iciba / qqTranSmart / reverso to break
the source word order, and the final hop uses only youdao / iciba. Reverso as a last hop leaves
European academic phrasing, so it only appears in the tier2 final-hop pool; a downgrade is logged.

Language field: a concrete code ("de"), None (= document target language), or "BRIDGE"
(the first language that is neither source nor target).
"""

import re
import time
from typing import Dict, List, Optional, Sequence, Tuple

SHORT = {
    "iciba": "iciba", "qqTranSmart": "qq", "youdao": "youdao", "reverso": "reverso",
    "baidu": "baidu", "tencent": "tencent", "sogou": "sogou", "alibaba": "ali",
    "caiyun": "caiyun", "bing": "bing", "google": "google", "yandex": "yandex",
    "deepl": "deepl", "papago": "papago", "modernMt": "modernMt",
}

# Each hop: (language, tier1 engines, tier2 engines)
DEFAULT_CHAINS: List[List[Tuple[Optional[str], Tuple[str, ...], Tuple[str, ...]]]] = [
    [("de", ("iciba",), ("baidu", "youdao", "bing")),
     ("fr", ("qqTranSmart",), ("baidu", "youdao", "bing")),
     (None, ("youdao",), ("iciba", "baidu", "bing", "reverso"))],

    [("ja", ("qqTranSmart",), ("baidu", "youdao", "bing")),
     ("de", ("iciba",), ("baidu", "youdao", "bing")),
     (None, ("youdao",), ("iciba", "baidu", "bing", "reverso"))],

    [("ru", ("iciba",), ("baidu", "youdao", "bing")),
     ("de", ("qqTranSmart",), ("baidu", "youdao", "bing")),
     (None, ("iciba",), ("youdao", "baidu", "bing", "reverso"))],

    [("de", ("reverso",), ("bing", "google", "iciba")),
     ("BRIDGE", ("qqTranSmart",), ("baidu", "reverso", "bing")),
     (None, ("iciba",), ("youdao", "baidu", "bing", "reverso"))],
]

BRIDGE_ORDER = ["zh", "en", "ja", "fr", "de", "ru"]

# Probe sentences: short, unambiguous, one per language.
PROBE = {"en": "The service validates the ticket before it is issued.",
         "zh": "该系统在签发之前会先校验票据的有效性。"}

Chain = Tuple[str, Tuple[Tuple[str, str], ...]]


def _expand_lang(lang: Optional[str], src: str, dst: str) -> str:
    if lang is None:
        return dst
    if lang == "BRIDGE":
        return next((l for l in BRIDGE_ORDER if l not in (src, dst)), "ja")
    return lang


def _parse_cfg(chains_cfg: Optional[Sequence]) -> List[List[Tuple[Optional[str], Tuple[str, ...], Tuple[str, ...]]]]:
    """Accept [[["de", ["iciba"], ["baidu"]], ...], ...]; a two-element hop means all tier1."""
    if not chains_cfg:
        return DEFAULT_CHAINS
    parsed = []
    for chain in chains_cfg:
        hops = []
        for item in chain:
            lang = item[0]
            tier1 = item[1] if isinstance(item[1], (list, tuple)) else [item[1]]
            tier2 = item[2] if len(item) > 2 and item[2] is not None else []
            if isinstance(tier2, str):
                tier2 = [tier2]
            hops.append((lang, tuple(tier1), tuple(tier2)))
        parsed.append(hops)
    return parsed


def _probe(eng: str, from_lang: str, to_lang: str) -> Optional[str]:
    """Return None when usable, otherwise the error message."""
    try:
        import translators as ts
    except ImportError:
        return "translators not installed (pip install translators)"
    text = PROBE.get(from_lang, PROBE["en"])
    try:
        out = ts.translate_text(text, translator=eng, from_language=from_lang, to_language=to_lang)
        return None if isinstance(out, str) and out.strip() else "empty output"
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def build_chains(src: str, dst: str,
                 chains_cfg: Optional[Sequence] = None,
                 probe: bool = True) -> Tuple[List[Chain], List[str], List[str]]:
    """Pick an engine per hop. Returns (usable chains, log lines, downgrade notes)."""
    templates = _parse_cfg(chains_cfg)
    log: List[str] = []
    degradations: List[str] = []
    cache: Dict[Tuple[str, str, str], Optional[str]] = {}
    chains: List[Chain] = []

    for idx, hops in enumerate(templates):
        resolved, ok = [], True
        for lang, tier1, tier2 in hops:
            to_lang = _expand_lang(lang, src, dst)
            from_lang = resolved[-1][1] if resolved else src
            picked, tier, last_err = None, None, None
            for level, pool in (("tier1", tier1), ("tier2", tier2)):
                for eng in pool:
                    key = (eng, from_lang, to_lang)
                    if probe:
                        if key not in cache:
                            cache[key] = _probe(eng, from_lang, to_lang)
                        last_err = cache[key]
                    else:
                        last_err = None
                    if last_err is None:
                        picked, tier = eng, level
                        break
                if picked:
                    break
            if picked is None:
                pool = ", ".join(tier1 + tier2)
                log.append(f"  chain{idx + 1} broken at {from_lang}->{to_lang}: none of {pool} usable"
                           + (f" ({last_err[:60]})" if last_err else ""))
                ok = False
                break
            resolved.append((picked, to_lang))
            mark = "" if tier == "tier1" else "  <- downgraded"
            log.append(f"  chain{idx + 1} {from_lang}->{to_lang:<6} uses {picked:<12} [{tier}]{mark}")
            if tier == "tier2":
                degradations.append(f"chain{idx + 1} {from_lang}->{to_lang} downgraded to {picked}")
        if ok and resolved:
            name = "->".join(f"{lang.upper()}_{SHORT.get(eng, eng)}" for eng, lang in resolved)
            chains.append((name, tuple(resolved)))
    return chains, log, degradations


def translate_chain(text: str, src: str, hops: Tuple[Tuple[str, str], ...],
                    retries: int = 3) -> Tuple[Optional[str], Optional[str]]:
    """Return (result, error). Any failed hop abandons the chain; no partial output is returned."""
    try:
        import translators as ts
    except ImportError:
        return None, "translators not installed (pip install translators)"

    cur_text, cur_lang = text, src
    for eng, to_lang in hops:
        last = None
        for attempt in range(1, retries + 1):
            try:
                out = ts.translate_text(cur_text, translator=eng,
                                        from_language=cur_lang, to_language=to_lang)
                if not isinstance(out, str) or not out.strip():
                    raise RuntimeError("empty output")
                cur_text, cur_lang = out, to_lang
                last = None
                break
            except Exception as exc:
                last = f"{eng} {cur_lang}->{to_lang}: {type(exc).__name__}: {exc}"
                if attempt < retries:
                    time.sleep(1.2 * attempt)
        if last:
            return None, last
    return cur_text, None


def detect_lang(text: str) -> str:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    letters = max(1, len(re.findall(r"[A-Za-z]", text)))
    return "zh" if cjk / letters > 0.3 else "en"
