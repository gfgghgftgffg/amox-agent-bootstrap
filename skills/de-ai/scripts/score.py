# -*- coding: utf-8 -*-
"""候选打分与保真校验。

英文：GPT-2 的句间困惑度起伏 + 句式统计，加权求和。没有校准权重可用（那需要成对的
人工标注样本），所以这是启发式分，只用于候选排序和改前改后比较。
中文：同样没有校准样本，用可手算的句式统计做启发式分。
保真：英文用 GPT-2 末层隐层余弦；中文用长度比。
"""

import re
from typing import Dict, List, Sequence, Tuple

import numpy as np

LENGTH_RATIO = {"en": (0.70, 1.45), "zh": (0.75, 1.40)}

# 启发式公式的理论最大值，用来把 base 归一到 0~1，避免候选全部顶到上限
EN_BASE_MAX = 1.575
ZH_BASE_MAX = 1.55


def _is_cjk_text(text: str) -> bool:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return cjk >= 10 and cjk / max(1, len(text)) > 0.2


def trigram_jaccard(s1: str, s2: str) -> float:
    """英文按词三元组，中文按字三元组（中文没有空格分词）。"""
    if _is_cjk_text(s1) or _is_cjk_text(s2):
        t1 = re.findall(r"[\u4e00-\u9fff]|[A-Za-z]+|\d+", s1.lower())
        t2 = re.findall(r"[\u4e00-\u9fff]|[A-Za-z]+|\d+", s2.lower())
    else:
        t1, t2 = re.findall(r"\w+", s1.lower()), re.findall(r"\w+", s2.lower())
    g1, g2 = set(zip(t1, t1[1:], t1[2:])), set(zip(t2, t2[1:], t2[2:]))
    return len(g1 & g2) / max(1, len(g1 | g2)) if (g1 and g2) else 0.0


def _spec(text: str) -> Dict[str, set]:
    return {
        "numbers": set(re.findall(r"\d+(?:\.\d+)?", text)),
        "citations": set(re.findall(r"\[(\d+)\]", text)),
        "identifiers": set(re.findall(r"\b[A-Z][A-Z0-9_]{1,}\b|\b\w+:\w+\b|\b[A-Za-z]+_[A-Za-z0-9_]+\b", text)),
    }


def _size(text: str, lang: str) -> int:
    if lang == "zh":
        return len(re.findall(r"[\u4e00-\u9fff]", text))
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))


def validate(orig_text: str, cand: str, terms: Sequence[Tuple[str, str]] = (),
             dst_lang: str = "en", forbidden: Sequence[str] = (),
             protected: Sequence[str] = (), cross_lang: bool = False) -> List[str]:
    """确定性保真校验。返回问题列表，空列表表示通过。

    术语检查只在目标语种为英文时生效：英文术语译成中文属于正常翻译，不是漂移。
    """
    problems = []
    a, b = _spec(orig_text), _spec(cand)
    for key in ("numbers", "citations"):
        missing = a[key] - b[key]
        if missing:
            problems.append(f"{key} missing: {sorted(missing)}")
    if a["identifiers"] - b["identifiers"]:
        problems.append(f"identifiers missing: {sorted(a['identifiers'] - b['identifiers'])[:6]}")
    if dst_lang == "en":
        seen = set()
        bs = chr(92)
        for _, rep in terms:
            plain = rep.replace(bs + bs, bs)
            if not plain or plain in seen:
                continue
            seen.add(plain)
            if orig_text.count(plain) != cand.count(plain):
                problems.append(f"term drift: '{plain}' {orig_text.count(plain)}->{cand.count(plain)}")
    for term in protected:
        if term and orig_text.count(term) > cand.count(term):
            problems.append(f"protected term lost: '{term}'")
    for word in forbidden:
        if word and word in cand and word not in orig_text:
            problems.append(f"forbidden term: '{word}'")
    if re.search(r"QZ\d{3}ZQ", cand):
        problems.append("placeholder residue")
    if cross_lang:
        # 中文汉字数与英文词数大致是 1 : 0.55~0.8，用这个区间抓截断
        zh_chars = len(re.findall(r"[一-鿿]", orig_text))
        en_words = _size(cand, "en")
        if zh_chars >= 20:
            ratio = en_words / zh_chars
            if ratio < 0.30 or ratio > 1.05:
                problems.append(f"length anomaly: {zh_chars} chars -> {en_words} words (ratio {ratio:.2f})")
    else:
        lo, hi = LENGTH_RATIO.get(dst_lang, LENGTH_RATIO["en"])
        a_len, b_len = _size(orig_text, dst_lang), _size(cand, dst_lang)
        if a_len >= 10:
            ratio = b_len / a_len
            if ratio < lo or ratio > hi:
                problems.append(f"length anomaly: {a_len}->{b_len} (ratio {ratio:.2f})")
    return problems


IDENT_PATTERNS = [
    r"\b[A-Z][A-Za-z0-9]*(?:[A-Z][a-z0-9]+)+\b",   # GetObject, HomeBucket
    r"\b[A-Z]{2,}\b",                               # TLS, KMS, AD
    r"\b[a-zA-Z]+:[a-zA-Z]+\b",                      # kms:Decrypt
    r"\b[A-Za-z]_[A-Za-z0-9,]+\b",                   # K_c,tgs
    r"\bv?\d+\.\d+(?:\.\d+)*\b",  # 版本号
]
_STOP_CAPS = {"A", "I", "OK", "AI", "HTML", "URL", "PDF", "DOCX", "API", "ID"}


def extract_terms(texts: Sequence[str], min_repeat: int = 2) -> List[str]:
    """从文档里自动抽出不能改动的标识符，不需要模型也不需要用户填表。

    - 驼峰标识符、全大写缩写、`ns:Action`、`K_c,x`、版本号：出现过就算。
    - 「多个首字母大写的词组」：至少重复 min_repeat 次才算产品名，避免把句首词当术语。
    """
    found: Dict[str, int] = {}
    for text in texts:
        for pat in IDENT_PATTERNS:
            for m in re.findall(pat, text):
                if len(m) < 2 or m in _STOP_CAPS:
                    continue
                found[m] = found.get(m, 0) + 1
        for m in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text):
            found[m] = found.get(m, 0) + 1
    return sorted(t for t, c in found.items()
                  if c >= (1 if not " " in t else min_repeat))


class EnglishScorer:
    """英文打分器：本地 GPT-2 提供困惑度与隐层，其余是正则统计。"""

    def __init__(self, model_name: str = "gpt2"):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        self.torch = torch
        try:  # 已缓存就离线加载，避免每次跑都去连 Hub
            self.tok = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.mod = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
        except Exception:
            print(f"[INFO] {model_name} 不在本地缓存，开始下载（约 500MB）。"
                  "国内网络可先设 HF_ENDPOINT=https://hf-mirror.com")
            self.tok = AutoTokenizer.from_pretrained(model_name)
            self.mod = AutoModelForCausalLM.from_pretrained(model_name)
        self.mod.eval()

    def extract_features(self, text: str) -> Tuple[Dict[str, float], np.ndarray]:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip().split()) >= 2]
        n_sents = max(1, len(sents))
        sent_lens = [len(s.split()) for s in sents] or [len(text.split())]

        mean_sl = float(np.mean(sent_lens))
        std_sl = float(np.std(sent_lens)) if len(sent_lens) > 1 else 0.0
        cv_sl = std_sl / max(1.0, mean_sl)
        range_sl = (float(np.max(sent_lens)) - float(np.min(sent_lens))) / max(1.0, mean_sl)
        short_sent_frac = sum(1 for l in sent_lens if l <= 11) / n_sents
        long_sent_frac = sum(1 for l in sent_lens if l >= 28) / n_sents
        uniform_sent_frac = sum(1 for l in sent_lens if 15 <= l <= 25) / n_sents

        starters = [s.split()[0].lower().strip("([\"'") for s in sents if s.split()]
        the_this_starter_frac = sum(
            1 for st in starters
            if st in {"the", "this", "these", "it", "each", "in", "after", "before", "if", "when"}
        ) / n_sents

        tl = text.lower()
        passive_cnt = len(re.findall(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", tl))
        modal_passive_cnt = len(re.findall(r"\b(will|should|must|can|may|could)\s+be\s+\w+ed\b", tl))
        nmt_connectors = len(re.findall(
            r"\b(therefore|however|additionally|furthermore|moreover|at the same time|thereby|"
            r"firstly|secondly|finally|initially|subsequently|consequently|respectively|"
            r"provided that|as well as|in order to)\b", tl))
        gerund_after_comma = len(re.findall(r",\s*(thereby\s+)?\w+ing\b", tl))

        enc = self.tok(text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = enc["input_ids"]
        with self.torch.no_grad():
            out = self.mod(input_ids, labels=input_ids, output_hidden_states=True)
            logits = out.logits[:, :-1, :]
            targets = input_ids[:, 1:]
            log_probs = self.torch.log_softmax(logits, dim=-1)
            token_lp = log_probs.gather(2, targets.unsqueeze(-1)).squeeze(-1).squeeze(0).numpy()
            hidden = out.hidden_states[-1].mean(dim=1).squeeze(0).numpy()

        sent_nlls = []
        for s in sents:
            s_ids = self.tok(s, return_tensors="pt", truncation=True, max_length=256)["input_ids"]
            if s_ids.shape[1] >= 4:
                with self.torch.no_grad():
                    sent_nlls.append(float(self.mod(s_ids, labels=s_ids).loss.item()))
        sent_nll_std = float(np.std(sent_nlls)) if len(sent_nlls) > 1 else 0.0
        sent_nll_range = (max(sent_nlls) - min(sent_nlls)) if len(sent_nlls) > 1 else 0.0

        feats = {
            "mean_sl": mean_sl, "cv_sl": cv_sl, "range_sl": range_sl,
            "short_sent_frac": short_sent_frac, "long_sent_frac": long_sent_frac,
            "uniform_sent_frac": uniform_sent_frac,
            "the_this_starter_frac": the_this_starter_frac,
            "passive_rate": (passive_cnt + modal_passive_cnt) / n_sents,
            "modal_passive_rate": modal_passive_cnt / n_sents,
            "nmt_conn_rate": nmt_connectors / n_sents,
            "gerund_comma_rate": gerund_after_comma / n_sents,
            "comma_rate": text.count(",") / n_sents,
            "paren_rate": text.count("(") / n_sents,
            "hyphen_rate": len(re.findall(r"\w+-\w+", text)) / n_sents,
            "citation_rate": len(re.findall(r"\[\d+\]", text)) / n_sents,
            "mean_nll": -float(np.mean(token_lp)),
            "std_nll": float(np.std(token_lp)),
            "sent_nll_std": sent_nll_std,
            "sent_nll_range": sent_nll_range,
        }
        return feats, hidden

    def score(self, text: str, ref_text: str = "") -> Tuple[float, Dict[str, float], np.ndarray]:
        f, h = self.extract_features(text)
        raw = (
            0.45
            - 0.60 * f["short_sent_frac"]
            - 0.25 * (f["sent_nll_std"] - 0.50)
            + 0.40 * f["uniform_sent_frac"]
            + 0.35 * f["modal_passive_rate"]
            + 0.25 * f["nmt_conn_rate"]
        )
        # 除以理论最大值再截断，否则短段落会全部顶到 1.0，候选之间就分不出高低了
        base = float(np.clip(raw / EN_BASE_MAX, 0.0, 1.0))
        ov = trigram_jaccard(text, ref_text) if ref_text else 0.0
        penalty = (0.80 * f["gerund_comma_rate"]
                   + 0.35 * max(0.0, f["the_this_starter_frac"] - 0.30)
                   + 0.50 * max(0.0, ov - 0.22)
                   + 0.20 * f["modal_passive_rate"])
        f["_base"] = round(base, 4)
        f["_penalty"] = round(penalty, 4)
        return base + penalty, f, h

    def fidelity(self, cand_hidden, ref_hidden) -> float:
        a, b = np.asarray(cand_hidden), np.asarray(ref_hidden)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


class ChineseScorer:
    """中文打分器：纯统计，无模型依赖。"""

    CONNECTORS = ("首先", "其次", "再次", "最后", "此外", "因此", "然而", "同时",
                  "综上", "总之", "值得注意", "不难看出", "众所周知", "由此可见")
    VAGUE_VERBS = ("进行", "实现", "具有", "起到", "加以", "予以")

    def extract_features(self, text: str) -> Dict[str, float]:
        sents = [s for s in re.split(r"(?<=[。！？])", text) if s.strip()]
        n = max(1, len(sents))
        lens = [len(s) for s in sents]
        mean_len = sum(lens) / n
        std_len = (sum((l - mean_len) ** 2 for l in lens) / n) ** 0.5
        cjk = max(1, len(re.findall(r"[\u4e00-\u9fff]", text)))
        return {
            "avg_len": mean_len,
            "len_std": std_len,
            "short_frac": sum(1 for l in lens if l <= 20) / n,
            "comma_rate": text.count("，") / n,
            "de_rate": text.count("的") / n,
            "de_density": text.count("的") / cjk,
            "connector_rate": sum(text.count(c) for c in self.CONNECTORS) / n,
            "vague_verb_rate": sum(text.count(v) for v in self.VAGUE_VERBS) / n,
            "passive_rate": (text.count("被") + text.count("受到了") + text.count("得到了")) / n,
            "punct_variety": len({c for c in text if c in "，。、；：？！（）——《》"}),
            "parallel_runs": len(re.findall(
                r"[\u4e00-\u9fff]{2,6}、[\u4e00-\u9fff]{2,6}、[\u4e00-\u9fff]{2,6}", text)),
        }

    def score(self, text: str, ref_text: str = "") -> Tuple[float, Dict[str, float], None]:
        f = self.extract_features(text)
        raw = (
            0.40
            - 0.50 * f["short_frac"]
            + 0.30 * min(1.0, max(0.0, (f["avg_len"] - 30) / 25))
            + 0.15 * min(1.0, f["comma_rate"] / 2.5)
            + 0.20 * min(1.0, max(0.0, (f["de_rate"] - 2) / 4))
            + 0.25 * min(1.0, f["connector_rate"] / 1.0)
            + 0.15 * min(1.0, f["vague_verb_rate"] / 1.0)
            + 0.10 * min(1.0, f["passive_rate"] / 1.5)
            - 0.10 * min(1.0, f["punct_variety"] / 8)
        )
        base = max(0.0, raw / ZH_BASE_MAX)
        ov = trigram_jaccard(text, ref_text) if ref_text else 0.0
        penalty = 0.50 * max(0.0, ov - 0.22)
        f["_base"] = round(base, 4)
        f["_penalty"] = round(penalty, 4)
        return base + penalty, f, None

    def fidelity(self, orig: str, cand: str) -> float:
        """中文没有可比对的隐层，用长度比做粗保真指标。"""
        a, b = len(orig), len(cand)
        if not a:
            return 0.0
        return round(min(a, b) / max(a, b), 4)


def build_scorer(lang: str, model_name: str = "gpt2"):
    if lang == "zh":
        return ChineseScorer()
    return EnglishScorer(model_name=model_name)
