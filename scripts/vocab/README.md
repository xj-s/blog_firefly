# 考研词汇模块数据管线

`/vocab/` 页面读取的是构建期生成的静态数据，运行时不依赖后端、数据库或 API Key。

## 目录

```
scripts/vocab/
  fetch_sources.mjs   下载原始数据到 .cache/vocab/
  extract_exams.py    从 2010–2026 真题 PDF 抽取英文句子
  build_data.py       合并词表、释义、真题语料，生成 public/vocab/data/
  notes.json          人工整理的熟词僻义 / 考点提示（可选）
  confusions.json     易混词分组
```

生成结果（需要提交到仓库）：

```
public/vocab/data/
  meta.json           词库统计、数据来源、分片信息
  index.json          搜索索引（约 480 KB）
  words/a.json … z.json  按首字母分片的单词详情
```

## 重新生成

```bash
# 1. 下载原始数据（约 40 MB PDF + 20 MB 词库）
node scripts/vocab/fetch_sources.mjs

# 2. 安装 PDF 解析依赖（仅生成数据时需要）
python -m pip install pypdf

# 3. 从真题 PDF 抽取句子
python scripts/vocab/extract_exams.py

# 4. 合并并生成前端数据
python scripts/vocab/build_data.py
```

构建站点本身不需要 Python，也不需要重新生成数据；`public/vocab/data/` 已经是产物。

## 数据来源

| 来源 | 用途 | 许可 |
| --- | --- | --- |
| [NETEMVocabulary](https://github.com/exam-data/NETEMVocabulary) | 考研大纲 5530 词、词频、CEFR、部分早年真题例句 | CC BY-NC-SA 4.0 |
| [KyleBing/english-vocabulary](https://github.com/KyleBing/english-vocabulary) | 释义、词组、同近义、同根词、词根记忆法、例句 | 原库未声明标准开源协议，标注为学习用途 |
| [ECDICT](https://github.com/skywind3000/ECDICT) | 词形还原、音标兜底 | MIT |
| [ipa-dict](https://github.com/open-dict-data/ipa-dict) | 美式音标兜底 | MIT |
| [kaoyanzhenti](https://github.com/Fantasia1999/kaoyanzhenti) | 2010–2026 英语一/二真题 PDF | 仅供个人学习研究 |

说明：

- 本模块**不包含**《考研红宝书》《词汇闪过》等版权书籍的原文。界面栏目（考纲释义、考频、熟词僻义、搭配、真题）参考这类词书的常见编排方式；`notes.json` 是人工整理的公开知识，不是书籍摘录。
- 真题只按**单句**摘录，标注年份、英语一/二、题型（阅读 Text N / 翻译 / 新题型），不提供整卷。
- 生词本、笔记、复习记录只保存在浏览器 `localStorage`，不上传服务器。

## 生成逻辑

1. **词表并集**：NETEM 5530 大纲词 + 词书拓展词，共约 5700 词。
2. **释义合并**：优先用词书的多词性释义、英文释义、搭配、同近义、词族、记忆法；缺失时用 NETEM 释义。
3. **词形还原**：ECDICT lemma 表提供屈折变化，再用规则生成的词形做校验，过滤 lemma 表里的噪声（例如把 `thing` 误判为 `the` 的形式）。
4. **真题匹配**：排除完形填空（原题空格会破坏句子），按词形匹配 2010–2026 阅读/新题型/翻译句子，优先阅读、近年、长度适中的句子，每个词最多 5 句，并保证年份分散。
5. **人工考点**：`notes.json` 里的词会显示“考点提示”；`confusions.json` 生成易混词链接。
6. **分片**：按首字母输出 JSON，页面按需加载；搜索索引单独加载。

## 已知边界

- 真题语料覆盖约 67% 的词条。没有匹配到句子的词会显示“2010–2026 暂未匹配”，并回退到词书例句或早年真题例句。
- PDF 来自公开仓库，个别年份存在 OCR 错字；抽取脚本会过滤明显噪声，但不保证逐字与官方试卷一致。
- 2026 年试卷来自公开仓库，使用前请自行核对。
