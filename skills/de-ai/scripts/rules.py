# -*- coding: utf-8 -*-
"""Deterministic rewrite rules. Each rule fires per hit according to a probability, driven by a
seeded random source so runs reproduce.

The English rules started from de_ai_pipeline postprocess_nmt_english, made probabilistic and
extended with connective swapping. The Chinese rules target the same class of problems: stock
frames, light verbs, passives, filler connectives, long sentences, repeated sentence openings,
redundant words. Character stacking and parallelism density are measured only.
"""

import random
import re
from typing import Dict, List, Sequence, Tuple

# ==============================================================================
# Term table (project specific, override with --terms)
# ==============================================================================
# Nothing is replaced by default. Supply a table per project: a template lives in
# projects/terms.example.json and a validated Kerberos / AWS table in
# projects/terms.kerberos-aws.json. The empty default is deliberate: replacement is a global
# regex, so a wrong table damages an unrelated document.
DEFAULT_TERM_FIXES: List[Tuple[str, str]] = []

# ==============================================================================
# Random context
# ==============================================================================
class RuleContext:
    def __init__(self, cfg: Dict, seed: int = 0):
        self.cfg = cfg
        self.rng = random.Random(seed)
        series = cfg.get("ordinal_series", "auto")
        self.series = self.rng.choice(ORDINAL_SERIES) if series == "auto" else series
        zh_series = cfg.get("zh_ordinal_series", "auto")
        self.zh_series = self.rng.choice(ZH_ORDINAL_SERIES) if zh_series == "auto" else zh_series
        self.counts: Dict[str, int] = {}
        self.max_per_word = int(cfg.get("max_per_word", 2))
        self.hits: Dict[str, int] = {}

    def p(self, lang: str, rule: str) -> bool:
        prob = float(self.cfg.get(lang, {}).get(rule, 0.0))
        return prob > 0 and self.rng.random() < prob

    def prob(self, lang: str, rule: str) -> float:
        return float(self.cfg.get(lang, {}).get(rule, 0.0))

    def bump(self, rule: str) -> None:
        self.hits[rule] = self.hits.get(rule, 0) + 1

    def take_slot(self, word: str) -> bool:
        """Allow at most max_per_word replacements of one word per document."""
        n = self.counts.get(word, 0)
        if n >= self.max_per_word:
            return False
        self.counts[word] = n + 1
        return True


# ==============================================================================
# English
# ==============================================================================
ORDINAL_SERIES: List[List[str]] = [
    ["First", "Second", "Last"],
    ["Firstly", "Secondly", "Finally"],
    ["To begin with", "Next", "Finally"],
]
_ORDINAL_RE = re.compile(
    r"^(Firstly|First|To begin with|Secondly|Second|Thirdly|Third|Next|Finally|Lastly|Last)\b[,\s]*",
    re.IGNORECASE,
)

CONNECTOR_CLASSES = {
    "causal": ["Therefore", "Thus", "Hence", "Consequently", "As a result", "So"],
    "additive": ["Additionally", "In addition", "Also", "Moreover", "Furthermore", "Besides"],
    "contrast": ["However", "Nevertheless", "Still", "Yet"],
    "temporal": ["Meanwhile", "At the same time", "In parallel"],
    "summary": ["In summary", "Overall", "Taken together"],
}
_WORD_CLASS = {w.lower(): k for k, ws in CONNECTOR_CLASSES.items() for w in ws}
_CONNECTOR_RE = re.compile(
    r"\b(" + "|".join(sorted(_WORD_CLASS, key=len, reverse=True)) + r")\b[,\s]*",
    re.IGNORECASE,
)

GERUND_TAILS = [
    (r",\s*(?:thereby\s+)?avoiding\b", " and avoids"),
    (r",\s*(?:thereby\s+)?ensuring\b", " to ensure"),
    (r",\s*(?:thereby\s+)?allowing\b", " and allows"),
    (r",\s*(?:thereby\s+)?enabling\b", " and enables"),
    (r",\s*(?:thereby\s+)?reducing\b", " and reduces"),
    (r",\s*(?:thereby\s+)?minimizing\b", " and minimizes"),
    (r",\s*(?:thereby\s+)?preventing\b", " and prevents"),
    (r",\s*(?:thereby\s+)?making\b", " and makes"),
    # ", including -> such as" was removed: no measured support, and it breaks clauses once
    # translation has rearranged the sentence.
]

# Coordinated participles such as "and ensuring" become coordinated predicates, so a
# later sentence split never leaves an -ing fragment behind.
AND_GERUND = [
    (r"\band\s+avoiding\b", "and avoids"),
    (r"\band\s+ensuring\b", "and ensures"),
    (r"\band\s+allowing\b", "and allows"),
    (r"\band\s+enabling\b", "and enables"),
    (r"\band\s+reducing\b", "and reduces"),
    (r"\band\s+preventing\b", "and prevents"),
    (r"\band\s+making\b", "and makes"),
    (r"\band\s+minimizing\b", "and minimizes"),
]

MODAL_PASSIVE = [
    (r"\b(\w+)\s+will be replaced\b", r"\1 is replaced", r"\1 are replaced"),
    (r"\b(\w+)\s+will be protected\b", r"\1 stays protected", r"\1 stay protected"),
    (r"\b(\w+)\s+must be synchronized\b", r"\1 needs synchronization", r"\1 need synchronization"),
    (r"\b(\w+)\s+must be monitored\b", r"\1 requires monitoring", r"\1 require monitoring"),
    (r"\b(\w+)\s+must be protected\b", r"\1 requires protection", r"\1 require protection"),
    (r"\b(\w+)\s+must be tested\b", r"\1 requires testing", r"\1 require testing"),
    (r"\b(\w+)\s+will be revoked\b", r"\1 gets revoked", r"\1 get revoked"),
    (r"\b(\w+)\s+can be reused\b", r"\1 remains reusable", r"\1 remain reusable"),
    (r"\b(\w+)\s+can be accessed\b", r"\1 is reachable", r"\1 are reachable"),
]

RESPONSIBLE = [
    (r"\b(\w+)\s+is responsible for\s+(\w+ing)\b", r"\1 handles \2"),
    (r"\b(\w+)\s+are responsible for\s+(\w+ing)\b", r"\1 handle \2"),
]


def _plural_looking(word: str) -> bool:
    w = word.lower()
    return w.endswith("s") and not w.endswith(("ss", "us", "is"))

FINITE_VERBS = (
    r"\b(is|are|was|were|has|have|had|uses|use|provides|provide|requires|require|"
    r"stores|store|verifies|verify|returns|return|remains|remain|allows|allow|"
    r"supports|support|will|can|must|should|may|handles|handle|holds|hold|"
    r"confirms|confirm|records|record|initiates|initiate|limits|limit|prevents|prevent|"
    r"keeps|keep|applies|apply|enables|enable|defines|define|covers|cover|checks|check|"
    r"rejects|reject|sends|send|creates|create|runs|run)\b"
)
# Split only when the right side has an explicit subject; otherwise the shared subject
# would be cut off.
_SUBJECT_START = re.compile(r"^(the|this|that|these|those|it|they|we|you|i|each|such|both|all|most|some|any|a|an|its|their|our|his|her)\b", re.I)

EN_FLAGGED_STARTERS = {"the", "this", "these", "when", "before", "if", "after"}


def _resub_prob(pattern: str, repl: str, text: str, p: float, ctx: RuleContext,
                flags: int = 0, rule: str = "") -> str:
    def _sub(m):
        if ctx.rng.random() < p:
            ctx.bump(rule or pattern)
            return m.expand(repl)
        return m.group(0)
    return re.sub(pattern, _sub, text, flags=flags)


def en_punctuation(text: str) -> str:
    t = re.sub(r"([.;:])([A-Za-z])", r"\1 \2", text)
    t = t.replace("\u2014", ", ").replace(" -- ", ", ")
    return re.sub(r"[ \t]{2,}", " ", t)


def en_connectors(text: str, ctx: RuleContext) -> str:
    if not ctx.p("en", "connector_swap"):
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out, idx = [], 0
    for s in sentences:
        m = _ORDINAL_RE.match(s)
        if m and idx < len(ctx.series):
            s = ctx.series[idx] + ", " + s[m.end():]
            idx += 1
            ctx.bump("en.ordinal")
        out.append(s)

    def _pick(m):
        word = m.group(1)
        cls = _WORD_CLASS[word.lower()]
        pool = [w for w in CONNECTOR_CLASSES[cls] if w.lower() != word.lower()]
        if not pool or not ctx.take_slot(word.lower()):
            return m.group(0)
        ctx.bump("en.connector_swap")
        return ctx.rng.choice(pool) + ", "

    return _CONNECTOR_RE.sub(_pick, " ".join(out))


def en_gerund(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("en", "gerund_tail")
    if p <= 0:
        return text
    for pat, rep in GERUND_TAILS:
        text = _resub_prob(pat, rep, text, p, ctx, rule="en.gerund_tail")
    for pat, rep in AND_GERUND:
        text = _resub_prob(pat, rep, text, p, ctx, rule="en.gerund_tail")
    return text


def en_modal_passive(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("en", "modal_passive")
    if p <= 0:
        return text

    def _make(pat, sing, plur):
        def _sub(m):
            if ctx.rng.random() >= p:
                return m.group(0)
            ctx.bump("en.modal_passive")
            return m.expand(plur if _plural_looking(m.group(1)) else sing)
        return _sub

    for pat, sing, plur in MODAL_PASSIVE:
        text = re.sub(pat, _make(pat, sing, plur), text)
    return text


def en_responsible(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("en", "connector_swap")
    if p <= 0:
        return text
    for pat, rep in RESPONSIBLE:
        text = _resub_prob(pat, rep, text, p, ctx, rule="en.responsible")
    return text


def en_split_long(text: str, ctx: RuleContext) -> str:
    if ctx.prob("en", "split_long") <= 0:
        return text
    out = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        if not ctx.p("en", "split_long"):
            out.append(s)
            continue
        done = False
        if len(s.split()) >= 20 and "; " in s:
            p1, p2 = [x.strip() for x in s.split("; ", 1)]
            if re.search(FINITE_VERBS, p2, flags=re.I) and _SUBJECT_START.match(p2):
                out.extend([p1 + ".", p2[0].upper() + p2[1:]])
                ctx.bump("en.split_long")
                done = True
        if not done and len(s.split()) >= 22 and ", and " in s:
            p1, p2 = [x.strip() for x in s.split(", and ", 1)]
            if (len(p2.split()) >= 5 and re.search(FINITE_VERBS, p2, flags=re.I)
                    and _SUBJECT_START.match(p2)):
                out.extend([p1 + ".", p2[0].upper() + p2[1:]])
                ctx.bump("en.split_long")
                done = True
        if not done:
            out.append(s)
    return " ".join(out)


def en_starter_dedup(text: str, ctx: RuleContext) -> str:
    if ctx.prob("en", "starter_dedup") <= 0:
        return text
    out, prev = [], False
    for s in re.split(r"(?<=[.!?])\s+", text):
        if not s.strip():
            continue
        w0 = s.split()[0].lower().strip("([\"'")
        flagged = w0 in EN_FLAGGED_STARTERS
        if flagged and prev and ctx.p("en", "starter_dedup"):
            new = re.sub(r"^When\s+", "Once ", s)
            if new == s:
                new = re.sub(r"^Before\s+", "Prior to ", s)
            if new == s:
                new = re.sub(r"^This\s+(approach|design|policy|method|step)\b", r"Such \1", s)
            if new == s:
                new = re.sub(r"^The\s+", "That ", s)
            if new != s:
                s = new
                ctx.bump("en.starter_dedup")
            prev = s.split()[0].lower().strip("([\"'") in EN_FLAGGED_STARTERS
        else:
            prev = flagged
        out.append(s[0].upper() + s[1:] if s and s[0].islower() else s)
    return " ".join(out)


# ==============================================================================
# Chinese
# ==============================================================================
ZH_FRAME_PATTERNS = [
    r"^随着.{2,15}?(?:的)?(?:不断)?(?:发展|推进|深入|普及|进步)[，,]",
    r"^在.{2,15}?的(?:背景|语境|视角|条件|前提)(?:之)?下[，,]",
    r"^对于.{2,15}?而言[，,]",
    r"^就.{2,15}?而言[，,]",
]
ZH_CLOSERS = [
    r"^综上所述[，,]",
    r"^总而言之[，,]",
    r"^总的来说[，,]",
    r"^由此可见[，,]",
    r"^不难(?:看出|发现)[，,]",
    r"^众所周知[，,]",
]
ZH_CONNECTORS = {
    "causal": ["因此", "因而", "所以"],
    "additive": ["此外", "另外", "同时", "再者"],
    "contrast": ["然而", "但是", "不过", "相反"],
}
ZH_ORDINAL_SERIES = [
    ["首先", "其次", "最后"],
    ["第一", "第二", "第三"],
    ["起初", "随后", "最后"],
]
_ZH_ORDINAL_RE = re.compile(r"^(首先|其次|再次|最后|第一|第二|第三|起初|随后)[，,]")

# Trailing connectives are swapped within a class, never deleted, so the causal or
# coordinating relation survives.
ZH_TAIL_CLASSES = {
    "causal": ["从而", "进而", "因而", "由此", "于是"],
    "causative": ["使得", "致使", "令", "让"],
    "coord": ["并且", "而且", "同时", "并", "也"],
}
_ZH_TAIL_RE = re.compile(
    r"[，,]\s*(" + "|".join(sorted({w for ws in ZH_TAIL_CLASSES.values() for w in ws},
                                   key=len, reverse=True)) + r")")


def zh_tail_swap(text: str, ctx: RuleContext) -> str:
    """The Chinese counterpart of `, -ing`: 从而 / 使得 / 并且 rotate within their class."""
    if ctx.prob("zh", "tail_swap") <= 0:
        return text

    def _pick(m):
        word = m.group(1)
        cls = next((c for c, ws in ZH_TAIL_CLASSES.items() if word in ws), None)
        if cls is None:
            return m.group(0)
        pool = [w for w in ZH_TAIL_CLASSES[cls] if w != word]
        if not pool or not ctx.take_slot(word):
            return m.group(0)
        ctx.bump("zh.tail_swap")
        return m.group(0)[0] + ctx.rng.choice(pool)

    return _ZH_TAIL_RE.sub(_pick, text)
ZH_PASSIVE = [
    (r"被(\S{1,8})所(\S{1,8})", r"由\1\2"),
    (r"得到了(\S{0,4}?)(验证|应用|认可|推广|重视)", r"已\1\2"),
    (r"受到了(\S{0,4}?)(关注|重视|质疑)", r"引起\1\2"),
]
ZH_VERBIFY = [
    (r"对(\S{1,12}?)进行了(\S{1,8}?)(分析|研究|测试|验证|评估|优化)", r"\2\3了\1"),
    (r"起到了(\S{1,8}?)作用", r"\1了"),
    (r"具有(?:重要|深远|一定)的?(现实|理论|实践)?意义", r"有\1意义"),
]
ZH_REDUNDANT = [
    (r"进行一个(\S{1,6})", r"\1"),
    (r"的的", "的"),
    (r"了了", "了"),
    (r"(非常|十分|极其|极为)", ""),
]
ZH_FLAGGED_STARTERS = ("本文", "本研究", "该系统", "该方法", "该方案", "该机制", "我们", "通过", "在")
ZH_STARTER_SWAP = {
    "本文": ["笔者", "本研究", "这里"],
    "本研究": ["本文", "笔者", "这里"],
    "该系统": ["它", "此系统", "这套系统"],
    "该方法": ["此方法", "这种办法", "它"],
    "该方案": ["此方案", "这种方案"],
    "该机制": ["此机制", "它"],
    "我们": ["笔者", "本文"],
    "通过": ["借助", "依靠", "经由"],
    "在": ["于", "处在"],
}


def zh_punctuation(text: str) -> str:
    t = re.sub(r"(?<=[\u4e00-\u9fff]),(?=[\u4e00-\u9fff])", "，", text)
    t = re.sub(r"(?<=[\u4e00-\u9fff])\.(?=[\u4e00-\u9fff])", "。", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff]):(?=[\u4e00-\u9fff])", "：", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff]);(?=[\u4e00-\u9fff])", "；", t)
    return re.sub(r"[ \t]{2,}", " ", t)


def _zh_sentences(text: str) -> List[str]:
    return [s for s in re.split(r"(?<=[。！？])", text) if s.strip()]


def zh_frame_delete(text: str, ctx: RuleContext) -> str:
    """"随着…的发展," "在…的背景下," 这类框架，整句删的删、前缀去的去。"""
    p = ctx.prob("zh", "frame_delete")
    if p <= 0:
        return text
    sents = _zh_sentences(text)
    out = []
    for i, s in enumerate(sents):
        body = s.lstrip()
        if not ctx.rng.random() < p:
            out.append(s)
            continue
        hit = False
        for pat in ZH_CLOSERS:
            if re.match(pat, body):
                body = re.sub(pat, "", body).lstrip()
                hit = True
                break
        if not hit:
            for pat in ZH_FRAME_PATTERNS:
                if re.match(pat, body):
                    body = re.sub(pat, "", body).lstrip()
                    hit = True
                    break
        if hit:
            if body and not body.endswith(("。", "！", "？")):
                body += "。"
            ctx.bump("zh.frame_delete")
            if body and len(body) > 8:
                out.append(body)
        else:
            out.append(s)
    return "".join(out)


def zh_fragment_fix(text: str) -> str:
    """翻译常把「，以确保」切成「。以确保」，句号后接关联词时改回逗号。"""
    pat = r"。\s*(以|为|并|从|从而|因此|由于|进而|以便)"
    return re.sub(pat, r"，\1", text)


def zh_ordinals(text: str, ctx: RuleContext) -> str:
    """序号必须成套：首先/其次/最后，不能混成 首先/Secondly。"""
    series = getattr(ctx, "zh_series", ZH_ORDINAL_SERIES[0])
    out, idx = [], 0
    for s in _zh_sentences(text):
        m = _ZH_ORDINAL_RE.match(s.lstrip())
        if m and idx < len(series):
            s = series[idx] + "，" + s.lstrip()[m.end():]
            idx += 1
            ctx.bump("zh.ordinal")
        out.append(s)
    return "".join(out)


def zh_connectors(text: str, ctx: RuleContext) -> str:
    def _pick(m):
        word = m.group(1)
        cls = next((c for c, ws in ZH_CONNECTORS.items() if word in ws), None)
        if cls is None:
            return m.group(0)
        pool = [w for w in ZH_CONNECTORS[cls] if w != word]
        if not pool or not ctx.take_slot(word):
            return m.group(0)
        ctx.bump("zh.connector_swap")
        return ctx.rng.choice(pool)

    pat = "(" + "|".join(sorted({w for ws in ZH_CONNECTORS.values() for w in ws},
                                key=len, reverse=True)) + ")"
    return re.sub(pat, _pick, text)


def zh_verbify(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("zh", "verbify")
    if p <= 0:
        return text
    for pat, rep in ZH_VERBIFY:
        text = _resub_prob(pat, rep, text, p, ctx, rule="zh.verbify")
    return text


def zh_passive(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("zh", "passive_rewrite")
    if p <= 0:
        return text
    for pat, rep in ZH_PASSIVE:
        text = _resub_prob(pat, rep, text, p, ctx, rule="zh.passive_rewrite")
    return text


def zh_highfreq_trim(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("zh", "highfreq_trim")
    if p <= 0:
        return text
    words = ctx.cfg.get("zh_highfreq_words", [])
    if not words:
        return text
    for w in words:
        cap = ctx.max_per_word

        def _sub(m, _w=w, _cap=cap):
            seen = ctx.counts.get(_w, 0)
            if seen < _cap:
                ctx.counts[_w] = seen + 1
                return m.group(0)
            if ctx.rng.random() < p:
                ctx.bump("zh.highfreq_trim")
                return ""
            return m.group(0)

        text = re.sub(re.escape(w), _sub, text)
    return text


def zh_redundant_trim(text: str, ctx: RuleContext) -> str:
    p = ctx.prob("zh", "redundant_trim")
    if p <= 0:
        return text
    for pat, rep in ZH_REDUNDANT:
        text = _resub_prob(pat, rep, text, p, ctx, rule="zh.redundant_trim")
    return text


def zh_split_long(text: str, ctx: RuleContext) -> str:
    if ctx.prob("zh", "split_long") <= 0:
        return text
    out = []
    for s in _zh_sentences(text):
        if len(s) > 45 and s.count("，") >= 3 and ctx.p("zh", "split_long"):
            parts = s.split("，")
            cut = 2 if len(parts) > 3 else 1
            left = "，".join(parts[:cut]) + "。"
            right = "，".join(parts[cut:])
            right = right[0].lstrip() + right[1:] if right else right
            out.append(left)
            out.append(right if right else "")
            ctx.bump("zh.split_long")
        else:
            out.append(s)
    return "".join(out)


def zh_starter_dedup(text: str, ctx: RuleContext) -> str:
    if ctx.prob("zh", "starter_dedup") <= 0:
        return text
    out, prev = [], ""
    for s in _zh_sentences(text):
        body = s.lstrip()
        head = next((w for w in ZH_FLAGGED_STARTERS if body.startswith(w)), "")
        if head and head == prev and ctx.p("zh", "starter_dedup"):
            pool = [w for w in ZH_STARTER_SWAP.get(head, []) if w != head]
            if pool:
                s = body.replace(head, ctx.rng.choice(pool), 1)
                if not s.endswith(("。", "！", "？")):
                    s += "。"
                ctx.bump("zh.starter_dedup")
        out.append(s)
        prev = next((w for w in ZH_FLAGGED_STARTERS if s.lstrip().startswith(w)), "")
    return "".join(out)


# ==============================================================================
# 只统计、不自动改的中文指标
# ==============================================================================
def zh_metrics(text: str) -> Dict[str, float]:
    sents = [s for s in _zh_sentences(text) if s.strip()]
    n = max(1, len(sents))
    de_counts = [s.count("的") for s in sents]
    len_cjk = max(1, len(re.findall(r"[\u4e00-\u9fff]", text)))
    return {
        "sent_count": len(sents),
        "avg_len": round(sum(len(s) for s in sents) / n, 1),
        "len_std": round((sum((len(s) - sum(len(x) for x in sents) / n) ** 2 for s in sents) / n) ** 0.5, 1),
        "short_frac": round(sum(1 for s in sents if len(s) <= 20) / n, 3),
        "comma_rate": round(text.count("，") / n, 2),
        "de_rate": round(sum(de_counts) / n, 2),
        "max_de_per_sent": max(de_counts) if de_counts else 0,
        "de_density": round(text.count("的") / len_cjk, 4),
        "parallel_runs": len(re.findall(r"[\u4e00-\u9fff]{2,6}、[\u4e00-\u9fff]{2,6}、[\u4e00-\u9fff]{2,6}", text)),
        "punct_variety": len({c for c in text if c in "，。、；：？！（）——《》"}),
    }


# ==============================================================================
# 引用与术语
# ==============================================================================
def restore_citations(text: str, orig_text: str) -> str:
    cites = re.findall(r"\[(\d+)\]", orig_text)
    for c in cites:
        text = re.sub(rf"\(\s*{c}\s*\)", f"[{c}]", text)
        text = re.sub(rf"（\s*{c}\s*）", f"[{c}]", text)
    missing = [c for c in cites if f"[{c}]" not in text]
    for c in dict.fromkeys(missing):
        if text.endswith(("。", ".")):
            text = text[:-1] + f" [{c}]" + text[-1]
        else:
            text = text + f" [{c}]"
    return text


def apply_terms(text: str, terms: Sequence[Tuple[str, str]]) -> str:
    for pat, rep in terms:
        text = re.sub(pat, rep, text)
    return text


# ==============================================================================
# 总入口
# ==============================================================================
def postprocess(text: str, orig_text: str, lang: str, ctx: RuleContext,
                terms: Sequence[Tuple[str, str]] = DEFAULT_TERM_FIXES) -> str:
    """顺序固定：标点 → 术语 → 连接词 → 尾巴/虚化 → 被动 → 断句 → 句首 → 冗余 → 引用。"""
    if lang == "zh":
        text = zh_punctuation(text)
        text = apply_terms(text, terms)
        text = zh_frame_delete(text, ctx)
        text = zh_ordinals(text, ctx)
        text = zh_connectors(text, ctx)
        text = zh_tail_swap(text, ctx)
        text = zh_verbify(text, ctx)
        text = zh_passive(text, ctx)
        text = zh_highfreq_trim(text, ctx)
        text = zh_split_long(text, ctx)
        text = zh_fragment_fix(text)
        text = zh_starter_dedup(text, ctx)
        text = zh_redundant_trim(text, ctx)
    else:
        text = en_punctuation(text)
        text = apply_terms(text, terms)
        text = en_connectors(text, ctx)
        text = en_responsible(text, ctx)
        text = en_gerund(text, ctx)
        text = en_modal_passive(text, ctx)
        text = en_split_long(text, ctx)
        text = en_starter_dedup(text, ctx)
    text = re.sub(r"\s+", " ", text).strip() if lang != "zh" else re.sub(r"[ \t]+", " ", text).strip()
    return restore_citations(text, orig_text)
