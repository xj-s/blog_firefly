# 考研词汇数据说明

本目录是 `/vocab/` 页面使用的静态数据，由 `scripts/vocab/build_data.py` 生成。

## 文件

| 文件 | 内容 |
| --- | --- |
| `meta.json` | 词库统计、数据来源、分片信息 |
| `index.json` | 搜索索引（单词、音标、简要释义、词频、真题次数） |
| `words/<letter>.json` | 按首字母分片的单词详情（释义、搭配、同近义、词族、记忆法、真题例句） |

## 来源与许可

- [NETEMVocabulary](https://github.com/exam-data/NETEMVocabulary)：考研大纲 5530 词、词频、CEFR、部分早年真题例句。数据以 **CC BY-NC-SA 4.0** 共享。
- [KyleBing/english-vocabulary](https://github.com/KyleBing/english-vocabulary)：释义、词组、同近义、同根词、记忆法、例句。原库未声明标准开源协议，本项目仅按学习用途使用。
- [ECDICT](https://github.com/skywind3000/ECDICT)：词形还原；[ipa-dict](https://github.com/open-dict-data/ipa-dict)：音标兜底。均为 MIT。
- [kaoyanzhenti](https://github.com/Fantasia1999/kaoyanzhenti)：2010–2026 考研英语（一/二）真题 PDF，仅按单句摘录用于个人学习研究。

## 使用边界

- 本数据**不包含**《考研红宝书》《词汇闪过》等版权书籍的原文；页面栏目参考这类词书的常见编排方式。
- 真题只摘录单句，标注年份、试卷类型和题型，不提供整卷。
- 本模块用于个人学习，不用于商业用途。
- 生词本、笔记、复习记录保存在访问者浏览器的 `localStorage`，不会上传到服务器。
