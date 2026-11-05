# halfman的破站

> 考研复习笔记博客

🌐 网站地址：[https://halfman.top](https://halfman.top)

---

## 关于

这是一个记录考研复习过程的个人博客，涵盖数学、英语、政治、408计算机综合等科目的学习笔记。不是系统性的总结，大约在每次学习后会更新知识。

基于 [Firefly](https://github.com/CuteLeaf/Firefly) 主题创作。

## 笔记内容

| 分类 | 内容 |
|------|------|
| 数学 | 高等数学、线性代数、概率论 |
| 408 | 数据结构、计算机网络、操作系统、计算机组成 |
| 英语 | 词汇、语法、阅读 |
| 政治 | 马原、毛概、史纲、思修 |

## 背单词模块

访问 `/vocab/`，或在导航栏点「背单词」。

- **查词**：考纲释义、词性、英文释义、常见搭配、同义替换、词族、词根记忆法、熟词僻义提示。
- **真题语境**：2010–2026 考研英语（一/二）阅读、新题型、翻译中的原句，标注年份与题型。
- **生词本**：一键加入，支持个人笔记、掌握标记、搜索筛选、JSON 导出/导入。
- **间隔复习**：按 1 / 2 / 4 / 7 / 15 / 30 / 60 天排队，四档反馈（忘记 / 模糊 / 记得 / 熟练），支持键盘操作。
- **本地优先**：生词本和复习记录保存在浏览器 localStorage，不需要登录，也不上传服务器。

词库以考研大纲 5530 词为基础，合并常见词书拓展词，共约 5700 词。数据来源、许可和重新生成方式见 [scripts/vocab/README.md](scripts/vocab/README.md)。

> 本模块不包含《考研红宝书》《词汇闪过》等版权书籍的原文；栏目结构参考其常见编排方式。真题按单句摘录，仅供个人学习研究。

## 技术栈

- [Astro](https://astro.build/) - 静态站点生成
- [Tailwind CSS](https://tailwindcss.com/) - 样式框架
- [Svelte](https://svelte.dev/) - 交互组件
- [GitHub Pages](https://pages.github.com/) - 托管部署

## 本地开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建
pnpm build
```

### 词汇数据

`public/vocab/data/` 已包含生成好的数据，正常开发/构建不需要额外步骤。只有修改词库或更新真题语料时才需要重新生成：

```bash
node scripts/vocab/fetch_sources.mjs
python -m pip install pypdf
python scripts/vocab/extract_exams.py
python scripts/vocab/build_data.py
```

## 更新笔记

1. 在 `src/content/posts/` 对应分类下创建 `.md` 文件
2. 添加 frontmatter 属性
3. `git push` 自动部署

---

*个人学习使用。*
