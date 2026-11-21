# de-ai

改写 `.docx` / `.md` / `.txt` 原文，降低机翻腔与 AI 痕迹。中文稿可以出中文，也可以出英文。

改写方式：**跨语系机器翻译链打散词序 + 确定性正则削句尾句长**。正文不由大模型生成。

## 做什么

```
原文 --[iciba]--> 德语 --[qq]--> 法语 --[youdao]--> 原语种
原文 --[qq]-->    日语 --[iciba]--> 德语 --[youdao]--> 原语种
原文 --[iciba]--> 俄语 --[qq]--> 德语 --[iciba]-->  原语种
原文 --[reverso]--> 德语 --[qq]--> 桥接语种 --[iciba]--> 原语种
```

同一段跑四条链，各产出一个候选，清洗后按分数选优。清洗是纯正则：

- 英文：`, -ing` 尾巴清零、情态被动降级、套话连接词按同类池随机取用、长句按主语断开、连续同构句首替换
- 中文：框架句删除（"随着…的发展"、"综上所述"）、虚化动词实义化（"进行了分析"→"分析了"）、被动改写、高频修饰词降频、伴随尾巴（"，从而"/"，使得"）随机取用、长句断开

每条规则的触发概率都能在配置文件里调，种子固定可复现。

## 安装

```bash
pip install -r scripts/requirements.txt
```

英文稿需要 `torch` + `transformers` 并下载 GPT-2（约 3GB）。国内网络先设镜像预拉一次：

```bash
HF_ENDPOINT=https://hf-mirror.com python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('gpt2')"
```

拉完缓存在本地，之后离线可用。

## 用法

作为 agent skill 使用：把本目录放进 `~/.pi/agent/skills/`（或 `~/.claude/skills/`），然后说「帮我把这份 docx 的 AI 味降一下」。

直接跑也行：

```bash
# 中文稿出中文
python scripts/pipeline.py --input in.md --out out.md --src-lang zh --dst-lang zh

# 英文稿出英文（Word 文档）
python scripts/pipeline.py --input in.docx --out out.docx --src-lang en --dst-lang en

# 中文稿出英文
python scripts/pipeline.py --input in.txt --out out.txt --src-lang zh --dst-lang en
```

先空跑看计划：

```bash
python scripts/pipeline.py --input in.docx --out out.docx --src-lang zh --dst-lang zh --dry-run
```

## 引擎可用性

翻译走 [`translators`](https://github.com/UlionTse/translators) 封装的免费接口。**每跳先用原方案的厂商（tier1），不可用才降到通用池（tier2）。**

| 网络 | 通常可用 |
|---|---|
| 中国大陆 | `iciba`、`qqTranSmart`、`youdao`、`baidu` |
| 境外 | `reverso`、`bing`、`google`、`yandex` |

运行时会逐跳打印实际选中的引擎和级别，出现 `[tier2]` 说明原方案厂商没连上：

```
链2 zh->ja     用 qqTranSmart  [tier1]
链3 de->en     用 baidu        [tier2]  ← 降级
```

要改优先级：

```json
{
  "chain_templates": [
    [["de", ["reverso"], ["bing", "google"]],
     ["fr", ["qqTranSmart"], ["bing"]],
     [null, ["iciba"], ["youdao", "reverso"]]]
  ]
}
```

## 术语

自动保护不需要配置：运行时会从全文抽出驼峰名、全大写缩写、`ns:Action`、下标键、版本号、重复出现的产品名，候选里丢了就作废。

术语替换需要显式给词表（全局正则，词表不对会改坏正文）：

```bash
python scripts/pipeline.py --input in.docx --out out.docx --terms projects/terms.example.json
```

## 产物

```
out.docx                  改写后的文档（元数据已清）
out.docx.work/report.md   逐段对照表、未替换原因、跳过清单
out.docx.work/result.json 全部候选、分数、校验问题、最终文本
out.docx.work/units/      每段每条链的原始翻译，重跑时复用
```

## 校验

任一不过就作废该候选：数字集合、引用编号、大写标识符、术语出现次数、禁用译法、长度比。

长度比（英文 0.70~1.45 词，中文 0.75~1.40 汉字）是防吞段用的——免费翻译接口会悄悄截断长句，数字和引用都还在，只有长度对不上。

## 注意

- 排序分不是检测器概率，只在候选之间和改前改后之间可比。本工具不承诺任何检测分数。
- 写回会合并段内 run，段落中间的加粗、斜体、上标引用编号会丢，导出后要人工核格式。
- 整篇改写会把本来没问题的段落一起改掉，改完请通读。
- 正文会发给上述第三方翻译网站，敏感内容不要用。
- 支持 `.docx`、`.md`、`.markdown`、`.txt`；旧版 `.doc` 需先另存为 `.docx`。
- PDF 导出需要 LibreOffice（跨平台）或 Windows 上的 Word，其余功能不依赖外部程序。
- `.docx` 写回会合并段内 run，段中的加粗、斜体、上标引用编号会丢。

## 许可

MIT
