---
name: de-ai
description: "改写 .docx 原文，降低机翻腔与 AI 痕迹。中文稿可出中文或出英文。用户说「降 AI 率」「去 AI 味」「这段太像机翻」「改写这份 docx」时使用。改写由跨语系机器翻译链加确定性正则完成，不由大模型生成正文。"
disable-model-invocation: true
license: MIT
metadata:
  version: "3.0.0"
---

# De-AI Pipeline

## 你不做什么

**不许自己改写、润色、重写正文。** 一个字都不行。

最终文本必须由本 skill 的脚本产出：翻译链负责换词序，正则负责削句尾与句长。由你直接生成会带语言模型的采样指纹，正好是这套流程要避开的东西。

你只做四件事：跑脚本、读产物、按判据决定下一步、向用户汇报。

## 你的动作

### 0. 环境

解释器用当前环境的 `python`。依赖见 `scripts/requirements.txt`，缺就装，不要擅自换实现。

```bash
PY=python
S="<skill目录>/scripts/pipeline.py"
```

### 1. 确认输入

支持 `.docx`、`.md`、`.markdown`、`.txt`。用户只给了聊天里的文字，先落成 `.md` 或 `.txt` 再往下走。

`.doc`（旧版二进制）不支持，让用户另存为 `.docx`。

问清一件事：**交中文还是交英文**。中文稿默认交中文，英文稿默认交英文。

### 2. 空跑

```bash
"$PY" "$S" --input "<输入>" --out "<输出>" --src-lang auto --dst-lang same --dry-run
```

这一步会先探测引擎可用性，再写 `<输出>.work/plan.json`。确认三件事：

- 目标段数是否合理
- 跳过清单里有没有被误跳的正文
- 语种判断对不对（`auto` 按 CJK 占比，混合稿要手工指定）

可用链少于 2 条时不要继续，先按第 6 节换链。

### 3. 正式跑

```bash
"$PY" "$S" --input "<输入>" --out "<输出>" --src-lang auto --dst-lang same --level standard
```

`--level` 选 `light`（1 条）/ `standard`（3 条，默认）/ `deep`（4 条）。先跑 `standard`，别一上来用 `deep`。

### 4. 读产物

`<输出>.work/report.md` 先看，`<输出>.work/result.json` 查细节。

| 状态 | 含义 | 你的动作 |
|---|---|---|
| `replaced` | 正常替换 | 不用管 |
| `replaced-low-sim` | 替换了但跟原文差太多 | 逐句对照 `orig` 和 `final`，讲给用户听 |
| `replaced-min-change` | 这段的链都没真正改写 | 换 `deep` 重跑；还不行就说"这段机械改写改不动" |
| `replaced-worse(+Δ)` | 写出去了，但排序分比原文更高（其它候选更差） | 把原文和改后一起给用户，让他决定留哪句 |
| `all-candidates-failed-validation` | 候选都丢了数字/引用/术语，或翻译被截断 | 看 `candidates[].validation`：`length anomaly` 是接口吞段，`term drift` 是术语走形，`numbers missing` 是数字丢 |
| `all-chains-failed` | 所有链都报错 | 看 `detail` 里的引擎错误，多半是网络或限流 |

### 5. 最多重跑一次

整个流程最多自动再跑一轮，只针对 `replaced-min-change`、`all-candidates-failed-validation`、`all-chains-failed` 的段落，用 `--level deep` 或换 `--seed`。第二轮结束无论结果如何都停下汇报。

`<输出>.work/units/` 是翻译缓存，同参数重跑只补失败或未完成的链，不重翻已做完的。

### 6. 汇报

四样东西，不要更多：

1. 处理段数、替换数、跳过数、失败数
2. 逐段对照表（状态、链、改前「句式分+扣分」、改后同口径、3-gram 重合）
3. 需要人看的段落清单及原因
4. 一句限定：`new_score` 是候选排序分，不是任何检测器的概率

## 不许说的话

- 不许承诺"AI 率降到多少"。这套流程没有检测器。
- 不许说"已通过 AI 检测"。唯一证据是用户提交后拿到的真实报告。
- 不许把 `new_score` 下降的百分比说成 AI 率下降的百分比。

## 参数

| 参数 | 说明 |
|---|---|
| `--input` / `--docx` | 输入文件：`.docx` / `.md` / `.markdown` / `.txt` |
| `--out` / `--out-docx` | 输出文件，扩展名决定格式，可与输入不同 |
| `--src-lang auto\|en\|zh` | 默认 `auto`，按段落 CJK 占比判断 |
| `--dst-lang same\|en\|zh` | `same` 表示交原语种 |
| `--level light\|standard\|deep` | 跑 1/3/4 条链 |
| `--terms <json>` | 项目术语表，`[[正则, 替换], ...]` |
| `--config <json>` | 概率、种子、链模板，模板见 `projects/rewrite.example.json` |
| `--seed N` | 固定随机，复现同一次结果 |
| `--skip-preflight` | 跳过引擎探测，直接跑 |
| `--out-pdf <pdf>` | 仅 `.docx` 输入可用；优先 LibreOffice（跨平台），Windows 上退回 Word |

## 链

四条链的形状固定，**每一跳分两级引擎**：先用 tier1（原方案实测过的厂商），全不可用才降到 tier2。

| 链 | 第 1 跳 | 第 2 跳 | 第 3 跳（末跳） |
|---|---|---|---|
| 1 | DE · `iciba` | FR · `qqTranSmart` | 原语种 · `youdao` |
| 2 | JA · `qqTranSmart` | DE · `iciba` | 原语种 · `youdao` |
| 3 | RU · `iciba` | DE · `qqTranSmart` | 原语种 · `iciba` |
| 4 | DE · `reverso` | 桥接语种 · `qqTranSmart` | 原语种 · `iciba` |

tier1 的分配来自实测结论：中转跳用 `iciba` / `qqTranSmart` / `reverso` 打散语序，**末跳只用 `youdao` / `iciba`**——`reverso` 作末跳会残留欧式学术短语，所以它只出现在 tier2 的末跳候选里。

tier2 是通用降级池：`baidu`、`bing`、`google`、`youdao`、`iciba`、`reverso`、`tencent`、`sogou`、`alibaba`、`caiyun`、`yandex`、`deepl`、`papago`。

运行时会打印每跳用了哪一级：

```
链2 zh->ja     用 qqTranSmart  [tier1]
链2 ja->de     用 iciba        [tier1]
链3 de->en     用 baidu        [tier2]  ← 降级
```

**出现 `[tier2]` 就是原方案厂商不可用，输出质量可能下降**，汇报时要跟用户说明。

桥接语种取第一个不同于首尾的语言：英出英用中文，中出中用英文，中出英用日语。

要改优先级，在配置里给 `chain_templates`，格式是「每跳 = [语种, [tier1...], [tier2...]]」，两元素写法等于把引擎全当 tier1：

```json
{
  "chain_templates": [
    [["de", ["iciba"], ["baidu", "bing"]],
     ["fr", ["qqTranSmart"], ["baidu"]],
     [null, ["youdao"], ["iciba", "reverso"]]]
  ]
}
```

## 概率配置

所有规则按 `config_default.json` 的概率逐处触发，固定种子可复现。项目覆盖文件放 `projects/<项目>/rewrite.json`：

```json
{
  "seed": 42,
  "en": { "connector_swap": 1.0, "gerund_tail": 0.85, "modal_passive": 0.7, "split_long": 0.8, "starter_dedup": 0.9 },
  "zh": { "frame_delete": 0.9, "connector_swap": 0.8, "tail_swap": 0.8, "verbify": 0.7,
          "passive_rewrite": 0.7, "highfreq_trim": 0.6, "split_long": 0.8,
          "redundant_trim": 0.9, "starter_dedup": 0.9 },
  "zh_highfreq_words": ["进一步", "显著", "充分", "全面", "极大", "深入", "有效", "关键", "核心"],
  "forbidden": ["回放缓存"],
  "selection": { "min_sim": { "en": 0.99, "zh": 0.75 }, "min_divergence": 0.10 }
}
```

- 0 等于关闭，低于 0.3 基本只命中极个别位置。
- 术语还原与引用补回不参与随机，永远全量执行。
- 序号成套：`First/Second/Last`、`Firstly/Secondly/Finally`、`To begin with/Next/Finally` 整篇只选一套，不会出现 `First` 接 `Secondly`；中文同理。
- 套话连接词不删，按同类池随机取用，同词全篇最多替换 `max_per_word` 次。
- `forbidden` 里的词出现在候选文本就作废该候选，用于挡已知错译。
- `min_divergence` 是"这条候选真的改动了"的下限（与原文的 3-gram 重合）。低于它的候选排到后面，全部低于时状态记 `replaced-min-change`。

## 术语

分两层，都不需要用户填表。

**第一层，自动保护（默认开启）。** 从全文自动抽出不能改动的标识符：驼峰名（`GetObject`）、全大写缩写（`TLS`、`KMS`）、`ns:Action`（`kms:Decrypt`）、下标键（`K_c,tgs`）、版本号（`1.3`），以及重复出现两次以上的多词产品名（`AWS Transfer Family`）。候选里只要少了一个，该候选作废。源语与目标语相同时（英出英、中出中）才做这项检查，跨语种翻译时标识符本来就会被译掉。

**第二层，术语替换（需显式给词表）。** 默认不替换任何术语，因为替换是全局正则，词表不对会改坏正文：

```json
[["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"], ["\\breplay memory\\b", "replay cache"]]
```

模板 `projects/terms.example.json`，已验证的 Kerberos / AWS 词表 `projects/terms.kerberos-aws.json`。

术语替换是全局正则，词表不对会直接改坏正文，所以默认空表。中文稿常见需要补的错译（如 `回放缓存 → 重放缓存`）和不可接受译法（写进 `forbidden`）都由项目词表负责。

## 支持的格式

| 格式 | 读 | 写 | 跳过什么 |
|---|---|---|---|
| `.docx` | python-docx | 保留段落样式，合并段内 run | 标题样式、图注表注、参考文献、等宽字体段落、短标签 |
| `.md` / `.markdown` | 纯文本，空行分块 | 原样写回 | 标题、代码围栏、表格、引用块、链接定义、缩进代码 |
| `.txt` | 纯文本，空行分块 | 原样写回 | 只跳过过短的块 |

Markdown 的代码围栏用行级状态机判断，围栏内的内容（含表格）不会被改。输出文件扩展名可以和输入不同，比如 `.md` 进 `.docx` 出不支持——文本类之间可以互换。

## 校验（不通过就作废该候选）

数字集合、引用编号集合、大写标识符（`KMS`、`kms:Decrypt`、`K_C`）必须全部保留；目标语为英文时术语表每项出现次数必须相等；`forbidden` 里的词不得出现；长度比英文 0.70~1.45 词、中文 0.75~1.40 汉字。

长度比是防吞段的：免费翻译接口会悄悄截断长句，数字和引用都还在，只有长度对不上。

## 产物

```
<out-docx>             改写后的文档（元数据已清）
<out-docx>.work/units/ 每段每条链的原始翻译与错误
<out-docx>.work/result.json   全部候选、分数、校验问题、最终文本
<out-docx>.work/report.md     逐段对照表、未替换原因、跳过清单
```

## 已知限制

- `.docx` 写回会合并段内 run，段落中间的加粗、斜体、上标引用编号会丢，导出后要人工核格式。`.md` / `.txt` 没有这个问题。
- PDF 导出需要 LibreOffice（Windows / macOS / Linux 都有）或 Windows 上的 Microsoft Word；两者都没有时会在报告里给出警告，文档本身已经写好。
- 中文「的」字堆叠、最长定语句、排比密度只统计不自动改，数字在 `result.json` 的 `features` 里。
- 免费接口会限流。长稿子分段跑，超时后同参数重跑即可续。
- 旧版 `.doc` 不支持，需要先另存为 `.docx`。
- 英文分是启发式，没有校准权重（校准需要成对的人工标注样本）。
- 打分按「每条链一个候选」算，段落只有一两句时句式率的统计不稳，分数波动大；短段落的分数只当作相对参考。
- 整篇改写会把本来没问题的段落也改掉，可能改差。改完要人读一遍。

## 停止条件

### 代码层（到点必停，不会挂住）

| 条件 | 行为 |
|---|---|
| 段落列表遍历完 | 正常结束，写 `result.json` 与 `report.md` |
| 每跳翻译失败 3 次 | 放弃该链，记错误，继续下一条 |
| 链数上限 | `light` 1 条 / `standard` 3 条 / `deep` 4 条，不会自己加链 |
| 引擎探测 | 每个（引擎, 源语, 目标语）组合只探一次 |
| Word 导 PDF | 300 秒超时 |
| 代码里 `while` | 0 个，没有重试大循环 |

### 段落层（每段必有一个终局）

写回的：`replaced`、`replaced-low-sim`、`replaced-min-change`。
保留原文的：`all-candidates-failed-validation`、`all-chains-failed`。

两种情况都会写进报告，不会静默跳过。

### Agent 层（这条最重要）

**最多两轮。** 第一轮 `standard`；第二轮只对上面三类失败段落用 `--level deep` 或换 `--seed`。第二轮结束无论结果如何都停下汇报，不许再试。

### 退出码

| 码 | 含义 |
|---|---|
| 0 | 所有目标段都已替换 |
| 1 | 没有可改写的段落（检查 `--min-words`） |
| 2 | 有段落被保留原文，需要看报告 |
| 3 | 没有可用链，需要配 `chain_templates` |

### 人可以收工的条件

1. 退出码 0。
2. 没有 `all-chains-failed`；没有 `all-candidates-failed-validation`，或已确认可接受。
3. `replaced-min-change` 的段落已看过，或 deep 重跑后仍无改善、确认人工处理。
4. 全文通读一遍——改写会动整篇，包括本来没问题的段落。
