# de-ai

[English](README.md) | 简体中文

![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)
![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

[安装依赖](#安装依赖) • [快速开始](#快速开始) • [处理流程](#处理流程) • [翻译链](#翻译链) • [规则与术语配置](#规则与术语配置) • [命令行参数](#命令行参数) • [输出与限制](#输出与限制)

使用跨语系机器翻译链与确定性正则规则改写中英文 `.docx`、`.md` 或 `.txt` 文档，输出保持指定文档格式。所有改写结果均由翻译接口和固定种子的规则脚本生成，不经过语言模型改写正文。Agent 调用时读取 [SKILL.md](SKILL.md)。

> [!WARNING]
> 目标段落会通过 [`translators`](https://github.com/UlionTse/translators) 发送到第三方免费翻译接口。请勿用于机密或受限文档。

## 安装依赖

需要 Python 3.9 及以上版本：

```bash
pip install -r scripts/requirements.txt
```

输出为英文时，打分与隐状态相似度校验还需 `torch`、`transformers` 及本地缓存的 `gpt2` 模型（合计约 3 GB）。

> [!TIP]
> 无法直连 Hugging Face Hub 时，可先通过镜像预拉取一次 `gpt2`，后续即可离线加载：
>
> ```bash
> HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoTokenizer.from_pretrained('gpt2'); AutoModelForCausalLM.from_pretrained('gpt2')"
> ```

## 快速开始

```bash
# 仅探测可用链并输出分块计划，不执行改写
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run

# 中文 Markdown 改写为中文
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# 英文 Word 文档改写为英文
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# 中文纯文本翻译并清理为英文
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

`pipeline.py` 以只读方式打开 `--input`，若 `--out` 与输入解析为同一路径则直接报错退出，不会覆盖原文件。

作为仅显式调用的 Agent Skill（[SKILL.md](SKILL.md)）使用时，将本目录放入宿主 Skills 目录（Pi 另需部署仓库中的 `pi/prompts/de-ai.md`），再通过 `/de-ai <file>` 或 `/skill:de-ai` 触发。

## 处理流程

1. **提取正文块**：按空行切分 `.md`/`.txt` 或逐段扫描 `.docx`，跳过标题、代码块、表格、图表注、参考文献及字词数低于 `--min-words`（默认 `30`）的短块。
2. **执行跨语系翻译链**：每个正文块依次经过最多 4 条三跳翻译链，经过日语、俄语、德语、法语等两个中转语种重排从句和修饰语顺序，再译回目标语种。
3. **执行正则后处理**：修正标点、执行可选术语表替换、轮换连接词与序号词组、清理英文 `, -ing` 伴随状语与情态被动或中文套话框架与虚化动词、切分超长句、去重连续同构句首，并还原 `[N]` 引用编号。
4. **保真校验与排序**：剔除丢失数字、引用、全大写／`ns:Action` 标识符、受保护术语或术语频次的候选，以及触发 `forbidden` 禁用词或长度比例越界（英文 `0.70–1.45` 词、中文 `0.75–1.40` 字、`zh -> en` 跨语种 `0.30–1.05` 英文词/汉字）的候选。先从通过校验的候选中选出达到相似度阈值的结果。同语种改写时，再优先考虑 `3-gram` Jaccard 重叠度至少为 `0.10`（`selection.min_divergence`）的候选。同组内按 `score`（`base + penalty`）从低到高排序。重叠度超过 `0.22` 会增加惩罚项。

特征对比与打分公式见 [references/chains.md](references/chains.md)。

## 翻译链

默认模板在每一跳先探测 `tier1` 引擎列表，连不通时自动降级到 `tier2` 备选池：

```text
原文 --[iciba]-->       de --[qqTranSmart]--> fr     --[youdao]--> 目标语种
原文 --[qqTranSmart]--> ja --[iciba]-->       de     --[youdao]--> 目标语种
原文 --[iciba]-->       ru --[qqTranSmart]--> de     --[iciba]-->  目标语种
原文 --[reverso]-->     de --[qqTranSmart]--> BRIDGE --[iciba]-->  目标语种
```

`BRIDGE` 自动取 `zh, en, ja, fr, de, ru` 中第一个既非源语也非目标语的语种。可用接口取决于网络环境（中国大陆常见为 `iciba`、`qqTranSmart`、`youdao`、`baidu`；境外常见为 `reverso`、`bing`、`google`、`yandex`）。

```text
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

> [!NOTE]
> `tier1` 将末跳限定在 `youdao` 和 `iciba`，因为 `reverso` 放在末跳会残留欧式学术句式，因此仅作为中间跳或 `tier2` 备选。

如需调整引擎顺序，可在配置文件中覆盖 `chain_templates`（每跳格式为 `[语种, [tier1...], [tier2...]]`，`null` 代表文档目标语种）：

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## 规则与术语配置

### 改写规则

复制 [projects/rewrite.example.json](projects/rewrite.example.json) 修改后通过 `--config` 传入：

```json
{
  "seed": 42,
  "ordinal_series": "auto",
  "max_per_word": 2,
  "en": {
    "connector_swap": 1.0,
    "gerund_tail": 0.85,
    "modal_passive": 0.7,
    "split_long": 0.8,
    "starter_dedup": 0.9
  },
  "zh": {
    "frame_delete": 0.9,
    "connector_swap": 0.8,
    "tail_swap": 0.8,
    "verbify": 0.7,
    "passive_rewrite": 0.7,
    "highfreq_trim": 0.6,
    "split_long": 0.8,
    "redundant_trim": 0.9,
    "starter_dedup": 0.9
  },
  "zh_highfreq_words": ["进一步", "显著", "充分", "全面", "极大", "深入", "有效", "关键", "核心"],
  "forbidden": [],
  "selection": {
    "min_sim": { "en": 0.99, "zh": 0.75 },
    "require_validation": true,
    "keep_all_candidates": true,
    "min_divergence": 0.1
  }
}
```

- 规则数值（`0.0`–`1.0`）表示逐处命中的触发概率（`0` 关闭规则）；`seed` 固定后处理规则的随机选择。
- `max_per_word` 限制单个连接词全篇替换上限（同时对 `zh_highfreq_words` 保留前 `max_per_word` 次出现后再按概率删减）；`ordinal_series` 固定序号成套出现（避免 `首先` 后混入异构序号）。
- `forbidden` 列出禁止新引入的错译词。术语替换与引用还原始终全量执行。

### 术语保护与替换

同语种改写会自动提取并保护驼峰命名、全大写缩写、`ns:Action`、下标键（如 `K_c,tgs`）、版本号及重复出现的首字母大写专名。

正则术语替换默认为空，需通过 `--terms` 显式传入 `[[正则, 替换], ...]`，避免误伤无关正文：

```json
[
  ["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"],
  ["\\breplay memory\\b", "replay cache"]
]
```

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

可从 [projects/terms.example.json](projects/terms.example.json) 起步，或参考已验证的技术论文词表 [projects/terms.kerberos-aws.json](projects/terms.kerberos-aws.json)。

## 命令行参数

| 参数 | 说明 |
| --- | --- |
| `--input`、`--docx` | 输入文件路径（`.docx`、`.md`、`.markdown`、`.mdown`、`.txt`） |
| `--out`、`--out-docx` | 输出文件路径（不得与 `--input` 相同；扩展名决定输出格式） |
| `--src-lang auto\|en\|zh` | 源语种；默认 `auto` 在全部目标块的汉字/拉丁字母比均 `> 0.3` 时取 `zh`，否则取 `en` |
| `--dst-lang same\|en\|zh` | 目标语种；默认 `same` 保持源语种 |
| `--level light\|standard\|deep` | 启用的翻译链数量：`1`、`3`（默认）或 `4` |
| `--min-words <int>` | 参与改写的最小块长度（汉字数 + 英文词数，默认 `30`） |
| `--config <json>` | 规则概率、筛选阈值、随机种子与 `chain_templates` 配置文件 |
| `--terms <json>` | 可选术语替换表 `[[正则, 替换], ...]` |
| `--work <dir>` | 缓存与报告输出目录（默认 `<out>.work`） |
| `--seed <int>` | 覆盖配置中的随机种子 |
| `--dry-run` | 探测引擎并生成 `<work>/plan.json`，不执行翻译改写 |
| `--skip-preflight` | 跳过运行前的逐跳引擎探测 |
| `--out-pdf <pdf>` | 仅限 `.docx` 输入；通过 LibreOffice（600 秒超时）或 Windows Word COM（300 秒超时）导出已清理元数据的 PDF |

**退出码**：`0` 全部目标块完成替换；`1` 参数错误或无可改写块；`2` 部分块保留原文或 PDF 导出失败；`3` 无可用翻译链。

## 输出与限制

```text
out.docx                    改写后的文档（.docx 已清理核心元数据）
out.docx.work/report.md     逐块状态对照表、保留原文原因与跳过清单
out.docx.work/result.json   所有候选译文、特征分项与校验详情
out.docx.work/units/        按块和链缓存的原始翻译结果，同参数重跑直接复用
```

每个目标块最终记为六种状态之一：`replaced`、`replaced-low-sim(<min_sim)`、`replaced-min-change(<min_div)`、`replaced-worse(+Δ)`（写回译文），或 `all-candidates-failed-validation`、`all-chains-failed`（保留原文）。`report.md` 中的 `Before` 和 `After` 仅用于块内候选排序，不代表任何检测器的判定概率。

### 格式处理与注意事项

| 格式 | 读写方式 | 自动跳过的块 |
| --- | --- | --- |
| `.docx` | 基于 `python-docx`；保留段落样式，合并被替换段落内的 run，并清理 `docProps/core.xml` | 标题／目录／图表注／参考文献样式、图表与摘要行、等宽字体段落、长度 `< min-words` 的块 |
| `.md`、`.markdown`、`.mdown` | 按空行分块，UTF-8（`\n`）写回 | 标题、围栏与缩进代码块（含围栏内表格）、表格、引用块、分隔线、图片、HTML、链接定义及 `< min-words` 的块 |
| `.txt` | 按空行分块，UTF-8（`\n`）写回 | 长度 `< min-words` 的块 |

> [!CAUTION]
> `.docx` 写回会合并段落内的 run，段内局部加粗、斜体和上标格式会丢失。定稿前请核查 `.docx` 排版，并重点通读报告中标记为 `replaced-min-change` 或 `replaced-worse` 的段落。旧版 `.doc` 需先另存为 `.docx`。

### 目录结构

```text
scripts/
  pipeline.py         命令行入口：分块、缓存、跑链、选优与报告输出
  docio.py            .docx / Markdown / 纯文本统一读写及 PDF 导出
  chains.py           翻译链模板、逐跳预探测与重试逻辑
  rules.py            受随机种子控制的中英文正则后处理规则
  score.py            GPT-2／统计打分、术语提取与保真校验
  config_default.json 默认规则概率与筛选阈值
  requirements.txt    Python 依赖清单
references/chains.md  特征对照数据、打分公式与翻译链设计依据
projects/             可复制修改的改写配置与术语表示例
```
