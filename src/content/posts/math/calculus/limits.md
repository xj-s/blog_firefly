---
title: "第一章 函数与极限"
published: 2026-05-28
description: "高等数学第一章笔记，包括函数极限的定义、性质、计算方法及连续性"
image: ""
tags: ["高等数学", "极限", "连续性"]
category: "数学/高等数学"
draft: false
pinned: false
---

## 1.1 函数极限的定义

### $\varepsilon - \delta$ 定义

设函数 $f(x)$ 在 $x_0$ 的某去心邻域内有定义，若存在常数 $A$，对于任意给定的 $\varepsilon > 0$，总存在 $\delta > 0$，使得当 $0 < |x - x_0| < \delta$ 时，有

$$|f(x) - A| < \varepsilon$$

则称 $A$ 为 $f(x)$ 当 $x \to x_0$ 时的极限，记作

$$\lim_{x \to x_0} f(x) = A$$

> [!TIP]
> **记忆技巧**：$\varepsilon$ 是"误差容忍度"，$\delta$ 是"自变量的控制范围"。极限的本质是"任意小的误差都可以通过控制自变量来实现"。

## 1.2 极限的运算法则

若 $\lim f(x) = A$，$\lim g(x) = B$，则：

$$\lim[f(x) \pm g(x)] = A \pm B$$

$$\lim[f(x) \cdot g(x)] = A \cdot B$$

$$\lim \frac{f(x)}{g(x)} = \frac{A}{B} \quad (B \neq 0)$$

## 1.3 两个重要极限

### 第一个重要极限

$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$

> [!NOTE]
> 推广形式：$\lim_{x \to 0} \frac{\sin ax}{bx} = \frac{a}{b}$

### 第二个重要极限

$$\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e$$

等价形式：

$$\lim_{x \to 0} (1 + x)^{\frac{1}{x}} = e$$

## 1.4 等价无穷小替换

当 $x \to 0$ 时：

| 原式 | 等价无穷小 |
|------|-----------|
| $\sin x$ | $x$ |
| $\tan x$ | $x$ |
| $\arcsin x$ | $x$ |
| $\arctan x$ | $x$ |
| $1 - \cos x$ | $\frac{1}{2}x^2$ |
| $e^x - 1$ | $x$ |
| $\ln(1+x)$ | $x$ |
| $(1+x)^a - 1$ | $ax$ |

> [!WARNING]
> **易错点**：等价无穷小替换只能在**乘除**关系中使用，不能在**加减**关系中直接替换！

### 典型例题

求极限 $\displaystyle\lim_{x \to 0} \frac{\tan x - \sin x}{x^3}$

**解**：

$$\frac{\tan x - \sin x}{x^3} = \frac{\sin x(1 - \cos x)}{x^3 \cos x}$$

当 $x \to 0$ 时，$\sin x \sim x$，$1 - \cos x \sim \frac{x^2}{2}$，$\cos x \to 1$

$$= \frac{x \cdot \frac{x^2}{2}}{x^3 \cdot 1} = \frac{1}{2}$$

> [!CAUTION]
> 如果直接对 $\tan x - \sin x$ 做等价替换为 $x - x = 0$，就会犯错！这就是"加减不能直接替换"的典型反例。

## 1.5 函数的连续性

函数 $f(x)$ 在 $x_0$ 处连续的充要条件：

$$\lim_{x \to x_0} f(x) = f(x_0)$$

即满足三个条件：
1. $f(x_0)$ 有定义
2. $\lim_{x \to x_0} f(x)$ 存在
3. 极限值等于函数值

---

*建议配合张宇/汤家凤高数视频 + 660题对应章节练习。*
