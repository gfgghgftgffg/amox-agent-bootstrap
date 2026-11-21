# de-ai

改写文档，让它不再读起来像机翻或生成文本。支持 `.docx`、`.md`、`.txt`，中文或英文都行，输出保持原格式。

正文不由大模型生成。文本先过一遍跨语系的机器翻译打散语序，再走正则削掉翻译留下的痕迹：句尾的 `, ensuring`、堆叠的情态被动、成套的套话连接词、长度差不多的句子。每一段产出若干候选，脚本挑那个跟原文差得最远、同时没丢数字、引用和标识符的。

主文档是英文：[README.md](README.md)。agent 读取的是 [SKILL.md](SKILL.md)，本文件只是中文镜像。

## 安装

```bash
pip install -r scripts/requirements.txt
```

英文稿另需 `torch`、`transformers` 和本地缓存的 GPT-2，合计约 3GB。连不上 Hugging Face 时先过镜像拉一次：

```bash
HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('gpt2')"
```

拉完缓存在本地，之后离线可用。

## 跑起来

```bash
# 中文进，中文出
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# 英文进，英文出
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# 中文进，英文出
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

正式跑之前先空跑，看它会动哪些块、跳过哪些：

```bash
python scripts/pipeline.py --input in.docx --out out.docx --src-lang auto --dst-lang same --dry-run
```

作为 agent skill 使用时，把目录和 prompt 模板一起放进 skills 路径，然后显式调用。它是刻意排除在自动选择之外的。

## 四条链

固定四条，每条穿过两个中转语种，最后回到原语种：

```
原文 --[iciba]-->   德语 --[qq]-->     法语 --[youdao]--> 原语种
原文 --[qq]-->      日语 --[iciba]-->  德语 --[youdao]--> 原语种
原文 --[iciba]-->   俄语 --[qq]-->     德语 --[iciba]-->  原语种
原文 --[reverso]--> 德语 --[qq]-->     桥接语种 --[iciba]--> 原语种
```

起作用的不是引擎，是中间那个语种。中英直译回英文，从句顺序和修饰语位置基本原样保留；过一遍日语或俄语再回来，语序就被重排了。

末跳限定在 `youdao` 和 `iciba`。reverso 放末跳会留下欧式学术腔，所以它只在备用池里出现。

## 引擎怎么选

翻译走 [`translators`](https://github.com/UlionTse/translators) 包的那些免费接口，能连上哪几个取决于你在哪。国内通常是 `iciba`、`qqTranSmart`、`youdao`、`baidu`；境外通常是 `reverso`、`bing`、`google`、`yandex`。

每一跳都配了 tier1（原方案实测过的引擎）和 tier2（其余备用）。开跑前逐跳探测一次，取第一个能连上的；只有 tier1 全挂才降到 tier2，运行日志会写清楚：

```
chain2 zh->ja      uses qqTranSmart  [tier1]
chain3 de->en      uses baidu        [tier2]  <- downgraded
```

出现 `[tier2]` 说明原方案引擎不可用，效果可能下降。要换顺序或换引擎，覆盖配置里的 `chain_templates`，每跳写成 `[语种, [tier1...], [tier2...]]`，`null` 表示文档自己的目标语种：

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## 调规则强度

每条规则都按概率逐处触发。复制 `projects/rewrite.example.json`，改完用 `--config` 传进去：

```json
{
  "seed": 42,
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
  "selection": { "min_sim": { "en": 0.99, "zh": 0.75 }, "min_divergence": 0.10 }
}
```

`0` 等于关掉，低于 `0.3` 基本不命中。`seed` 固定随机源，同样的参数重跑得到同一份稿。`max_per_word` 限制同一个连接词全篇最多替换几次，`ordinal_series` 锁定序号风格，避免 `First` 后面接 `Secondly`。英文那组管 `, -ing` 尾巴、九条固定情态被动、连接词轮换、长句断开、连续同构句首；中文那组管框架句（`随着…的发展`、`综上所述`）、虚化动词（`进行了分析` → `分析了`）、被动、高频修饰词、伴随尾巴（`，从而`、`，使得`）、长句和重复句首。

另外两个设置值得单独记住。`forbidden` 里的词一旦出现在候选文本就作废该候选，用来挡你见过的错译。`selection.min_divergence` 是"这条候选算真正改写"所需的最小 3-gram 差异。

术语还原和引用补回不受这些概率影响，永远全量执行。

## 术语

标识符不需要任何配置就受保护。脚本会从全文抽出驼峰名、全大写缩写、`ns:Action`、下标键、版本号和重复出现的产品名，候选里丢掉一个就作废。这项检查只在源语和目标语相同时跑，因为跨语种翻译时标识符本来就该被译掉。

替换需要显式给表，因为它是全局正则，词表不对会改坏正文。表是 `[正则, 替换]` 的列表：

```json
[
  ["\\bkms:\\s*Decrypt\\b", "kms:Decrypt"],
  ["\\breplay memory\\b", "replay cache"]
]
```

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

从 `projects/terms.example.json` 起步，已验证的 Kerberos / AWS 词表在 `projects/terms.kerberos-aws.json`。不给 `--terms` 就什么都不替换，运行时会提示。

## 产物

```
out.docx                    改写后的文档，元数据已清
out.docx.work/report.md     逐块对照表、未替换原因、跳过清单
out.docx.work/result.json   全部候选、分数、校验问题、最终文本
out.docx.work/units/        每块每条链的原始翻译，重跑时复用
```

候选在排序之前就要过校验：丢了数字、引用或受保护标识符，术语次数对不上，出现禁用词，或者长度跑出区间（英文 0.70~1.45 词，中文 0.75~1.40 字，跨语种 0.30~1.05 英文词每汉字）就作废。长度这一条是因为免费接口有时会把长段落的尾巴吃掉，而数字和引用都还在，这种情况下只剩长度能看出来。

报告里那个分数只用于同一个块内部的候选排序。跨文档不可比，也不是检测器的读数。

## 支持的格式

| 扩展名 | 读 | 写 | 跳过 |
|---|---|---|---|
| `.docx` | python-docx | 保留段落样式，合并段内 run | 标题样式、图表注、参考文献、等宽字体段落、短标签 |
| `.md` `.markdown` | 纯文本，按空行分块 | 原样写回 | 标题、代码围栏、表格、引用块、链接定义、缩进代码 |
| `.txt` | 纯文本，按空行分块 | 原样写回 | 过短的块 |

Markdown 的代码围栏逐行判断，围栏内的内容（含表格）不动。旧版 `.doc` 不支持，先另存为 `.docx`。

## 什么时候停

块列表是有限的，每跳最多试三次，链数由 `--level` 固定在 1、3 或 4，代码里没有 `while`。PDF 导出给 LibreOffice 600 秒、Word 300 秒超时。

每一块最后落在六种状态之一。四种写回（`replaced`、`replaced-low-sim`、`replaced-min-change`、`replaced-worse`），两种保留原文（`all-candidates-failed-validation`、`all-chains-failed`）。六种都会写进报告。

退出码：`0` 全部替换，`1` 没有可改的块，`2` 有块被保留或 PDF 导出失败，`3` 没有可用链，需要改 `chain_templates`。

由 agent 驱动时最多跑两轮：先 `standard`，再对失败的块用 `deep` 或换种子。自己驱动也一样，同一块跑第三轮基本不会变。

## 开跑前要知道的

正文会发给上面列出的第三方翻译接口。机密材料不要用。

`.docx` 写回会合并段内 run，段落中间的加粗、斜体、上标引用编号会丢，导出后要核格式。Markdown 和纯文本没有这个问题。

整篇改写会动到本来没问题的块，也可能把它们改差。报告会标出哪些块几乎没动、哪些分数反而升高，那些要读一遍。

PDF 导出用 LibreOffice，Windows 上也可以用 Microsoft Word。其余功能不依赖任何外部程序。

## 许可

MIT
