---
title: "数学LaTeX公式速查手册"
published: 2026-05-29
description: "考研数学常用LaTeX公式符号速查，包括微积分、线性代数等"
tags: ["LaTeX", "公式", "速查", "考研数学"]
category: "数学"
draft: false
pinned: false
---

## 一、基础符号

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 加减 | `\pm` | $\pm$ |
| 乘 | `\times` | $\times$ |
| 除 | `\div` | $\div$ |
| 不等于 | `\neq` | $\neq$ |
| 大于等于 | `\geq` | $\geq$ |
| 小于等于 | `\leq` | $\leq$ |
| 约等于 | `\approx` | $\approx$ |
| 无穷 | `\infty` | $\infty$ |
| 点乘 | `\cdot` | $\cdot$ |
| 叉乘 | `\times` | $\times$ |
| 正负 | `\pm` | $\pm$ |
| 负正 | `\mp` | $\mp$ |
| 恒等于 | `\equiv` | $\equiv$ |
| 远大于 | `\gg` | $\gg$ |
| 远小于 | `\ll` | $\ll$ |

---

## 二、希腊字母

| 小写 | 大写 | LaTeX |
|------|------|-------|
| α | A | `\alpha` |
| β | B | `\beta` |
| γ | Γ | `\gamma` |
| δ | Δ | `\delta` |
| ε | E | `\epsilon` |
| ζ | Z | `\zeta` |
| η | H | `\eta` |
| θ | Θ | `\theta` |
| ι | I | `\iota` |
| κ | K | `\kappa` |
| λ | Λ | `\lambda` |
| μ | M | `\mu` |
| ν | N | `\nu` |
| ξ | Ξ | `\xi` |
| π | Π | `\pi` |
| ρ | P | `\rho` |
| σ | Σ | `\sigma` |
| τ | T | `\tau` |
| υ | Υ | `\upsilon` |
| φ | Φ | `\phi` |
| χ | X | `\chi` |
| ψ | Ψ | `\psi` |
| ω | Ω | `\omega` |

---

## 三、集合符号

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 属于 | `\in` | $\in$ |
| 不属于 | `\notin` | $\notin$ |
| 包含于 | `\subseteq` | $\subseteq$ |
| 真包含于 | `\subset` | $\subset$ |
| 并集 | `\cup` | $\cup$ |
| 交集 | `\cap` | $\cap$ |
| 空集 | `\emptyset` | $\emptyset$ |
| 实数集 | `\mathbb{R}` | $\mathbb{R}$ |
| 整数集 | `\mathbb{Z}` | $\mathbb{Z}$ |
| 自然数集 | `\mathbb{N}` | $\mathbb{N}$ |
| 复数集 | `\mathbb{C}` | $\mathbb{C}$ |
| 任意 | `\forall` | $\forall$ |
| 存在 | `\exists` | $\exists$ |

---

## 四、微积分符号

### 4.1 导数

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 一阶导数 | `\frac{dy}{dx}` | $\frac{dy}{dx}$ |
| 二阶导数 | `\frac{d^2y}{dx^2}` | $\frac{d^2y}{dx^2}$ |
| n阶导数 | `\frac{d^ny}{dx^n}` | $\frac{d^ny}{dx^n}$ |
| 偏导数 | `\frac{\partial y}{\partial x}` | $\frac{\partial y}{\partial x}$ |
| 二阶偏导 | `\frac{\partial^2 y}{\partial x^2}` | $\frac{\partial^2 y}{\partial x^2}$ |
| 混合偏导 | `\frac{\partial^2 y}{\partial x \partial y}` | $\frac{\partial^2 y}{\partial x \partial y}$ |
| 导数值 | `f'(x)` | $f'(x)$ |
| 二阶导数值 | `f''(x)` | $f''(x)$ |
| n阶导数值 | `f^{(n)}(x)` | $f^{(n)}(x)$ |

### 4.2 积分

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 不定积分 | `\int f(x) dx` | $\int f(x) dx$ |
| 定积分 | `\int_a^b f(x) dx` | $\int_a^b f(x) dx$ |
| 二重积分 | `\iint_D f(x,y) dA` | $\iint_D f(x,y) dA$ |
| 三重积分 | `\iiint_\Omega f(x,y,z) dV` | $\iiint_\Omega f(x,y,z) dV$ |
| 曲线积分 | `\oint_L P dx + Q dy` | $\oint_L P dx + Q dy$ |

### 4.3 极限

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 极限 | `\lim_{x \to a}` | $\lim_{x \to a}$ |
| 左极限 | `\lim_{x \to a^-}` | $\lim_{x \to a^-}$ |
| 右极限 | `\lim_{x \to a^+}` | $\lim_{x \to a^+}$ |
| 无穷极限 | `\lim_{x \to \infty}` | $\lim_{x \to \infty}$ |

### 4.4 求和与求积

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 求和 | `\sum_{i=1}^n a_i` | $\sum_{i=1}^n a_i$ |
| 求积 | `\prod_{i=1}^n a_i` | $\prod_{i=1}^n a_i$ |
| 连加 | `\sum_{n=0}^\infty a_n` | $\sum_{n=0}^\infty a_n$ |

---

## 五、三角函数

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 正弦 | `\sin x` | $\sin x$ |
| 余弦 | `\cos x` | $\cos x$ |
| 正切 | `\tan x` | $\tan x$ |
| 余切 | `\cot x` | $\cot x$ |
| 正割 | `\sec x` | $\sec x$ |
| 余割 | `\csc x` | $\csc x$ |
| 反正弦 | `\arcsin x` | $\arcsin x$ |
| 反余弦 | `\arccos x` | $\arccos x$ |
| 反正切 | `\arctan x` | $\arctan x$ |

---

## 六、对数与指数

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 自然对数 | `\ln x` | $\ln x$ |
| 常用对数 | `\lg x` | $\lg x$ |
| 对数 | `\log_a x` | $\log_a x$ |
| 指数 | `e^x` | $e^x$ |
| 幂 | `x^n` | $x^n$ |
| 根号 | `\sqrt{x}` | $\sqrt{x}$ |
| n次根 | `\sqrt[n]{x}` | $\sqrt[n]{x}$ |

---

## 七、线性代数

### 7.1 矩阵

```latex
\begin{pmatrix} a & b \\ c & d \end{pmatrix}  % 圆括号
\begin{bmatrix} a & b \\ c & d \end{bmatrix}  % 方括号
\begin{vmatrix} a & b \\ c & d \end{vmatrix}  % 行列式
\begin{Vmatrix} a & b \\ c & d \end{Vmatrix}  % 范数
```

效果：
$$
\begin{pmatrix} a & b \\ c & d \end{pmatrix}
\quad
\begin{bmatrix} a & b \\ c & d \end{bmatrix}
\quad
\begin{vmatrix} a & b \\ c & d \end{vmatrix}
$$

### 7.2 常用矩阵

单位矩阵：
```latex
E = \begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{pmatrix}
```
$$
E = \begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{pmatrix}
$$

对角矩阵：
```latex
\Lambda = \begin{pmatrix} \lambda_1 & & \\ & \lambda_2 & \\ & & \lambda_3 \end{pmatrix}
```
$$
\Lambda = \begin{pmatrix} \lambda_1 & & \\ & \lambda_2 & \\ & & \lambda_3 \end{pmatrix}
$$

### 7.3 向量

| 符号 | LaTeX | 示例 |
|------|-------|------|
| 向量 | `\vec{v}` | $\vec{v}$ |
| 粗体向量 | `\mathbf{v}` | $\mathbf{v}$ |
| 列向量 | `\begin{pmatrix} x \\ y \\ z \end{pmatrix}` | $\begin{pmatrix} x \\ y \\ z \end{pmatrix}$ |
| 行向量 | `(x, y, z)` | $(x, y, z)$ |
| 范数 | `\|\vec{v}\|` | $\|\vec{v}\|$ |
| 点积 | `\vec{a} \cdot \vec{b}` | $\vec{a} \cdot \vec{b}$ |
| 叉积 | `\vec{a} \times \vec{b}` | $\vec{a} \times \vec{b}$ |

---

## 八、常见公式

### 8.1 极限公式

两个重要极限：
```latex
\lim_{x \to 0} \frac{\sin x}{x} = 1
```
$$
\lim_{x \to 0} \frac{\sin x}{x} = 1
$$

```latex
\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e
```
$$
\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e
$$

### 8.2 洛必达法则

```latex
\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}
```
$$
\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}
$$

### 8.3 泰勒展开

```latex
e^x = \sum_{n=0}^\infty \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots
```
$$
e^x = \sum_{n=0}^\infty \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots
$$

```latex
\sin x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots
```
$$
\sin x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots
$$

```latex
\cos x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots
```
$$
\cos x = \sum_{n=0}^\infty \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots
$$

```latex
\ln(1+x) = \sum_{n=1}^\infty \frac{(-1)^{n-1} x^n}{n} = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots
```
$$
\ln(1+x) = \sum_{n=1}^\infty \frac{(-1)^{n-1} x^n}{n} = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots
$$

```latex
\frac{1}{1-x} = \sum_{n=0}^\infty x^n = 1 + x + x^2 + x^3 + \cdots, \quad |x| < 1
```
$$
\frac{1}{1-x} = \sum_{n=0}^\infty x^n = 1 + x + x^2 + x^3 + \cdots, \quad |x| < 1
$$

### 8.4 积分公式

```latex
\int x^n dx = \frac{x^{n+1}}{n+1} + C, \quad n \neq -1
```
$$
\int x^n dx = \frac{x^{n+1}}{n+1} + C, \quad n \neq -1
$$

```latex
\int \frac{1}{x} dx = \ln|x| + C
```
$$
\int \frac{1}{x} dx = \ln|x| + C
$$

```latex
\int e^x dx = e^x + C
```
$$
\int e^x dx = e^x + C
$$

```latex
\int \sin x dx = -\cos x + C
```
$$
\int \sin x dx = -\cos x + C
$$

```latex
\int \cos x dx = \sin x + C
```
$$
\int \cos x dx = \sin x + C
$$

```latex
\int \tan x dx = -\ln|\cos x| + C
```
$$
\int \tan x dx = -\ln|\cos x| + C
$$

```latex
\int \frac{1}{a^2 + x^2} dx = \frac{1}{a} \arctan\frac{x}{a} + C
```
$$
\int \frac{1}{a^2 + x^2} dx = \frac{1}{a} \arctan\frac{x}{a} + C
$$

```latex
\int \frac{1}{\sqrt{a^2 - x^2}} dx = \arcsin\frac{x}{a} + C
```
$$
\int \frac{1}{\sqrt{a^2 - x^2}} dx = \arcsin\frac{x}{a} + C
$$

### 8.5 欧拉公式

```latex
e^{ix} = \cos x + i\sin x
```
$$
e^{ix} = \cos x + i\sin x
$$

```latex
e^{i\pi} + 1 = 0
```
$$
e^{i\pi} + 1 = 0
$$

---

## 九、常用写法

### 9.1 括号

| 写法 | LaTeX | 效果 |
|------|-------|------|
| 小括号 | `(a+b)` | $(a+b)$ |
| 中括号 | `[a+b]` | $[a+b]$ |
| 大括号 | `\{a+b\}` | $\{a+b\}$ |
| 自动括号 | `\left(\frac{a}{b}\right)` | $\left(\frac{a}{b}\right)$ |
| 自动方括号 | `\left[\frac{a}{b}\right]` | $\left[\frac{a}{b}\right]$ |
| 自动花括号 | `\left\{\frac{a}{b}\right\}` | $\left\{\frac{a}{b}\right\}$ |
| 绝对值 | `\|x\|` | $\|x\|$ |
| 范数 | `\|\vec{v}\|` | $\|\vec{v}\|$ |

### 9.2 箭头

| 写法 | LaTeX | 效果 |
|------|-------|------|
| 右箭头 | `\to` | $\to$ |
| 左箭头 | `\leftarrow` | $\leftarrow$ |
| 双向箭头 | `\leftrightarrow` | $\leftrightarrow$ |
| 推出 | `\Rightarrow` | $\Rightarrow$ |
| 等价 | `\Leftrightarrow` | $\Leftrightarrow$ |
| 趋于 | `\rightarrow` | $\rightarrow$ |

### 9.3 空格

| 写法 | LaTeX | 效果 |
|------|-------|------|
| 小空格 | `a\,b` | $a\,b$ |
| 中空格 | `a\;b` | $a\;b$ |
| 大空格 | `a\quad b` | $a\quad b$ |
| 超大空格 | `a\qquad b` | $a\qquad b$ |

### 9.4 文字

| 写法 | LaTeX | 效果 |
|------|-------|------|
| 正体 | `\text{abc}` | $\text{abc}$ |
| 粗体 | `\mathbf{v}` | $\mathbf{v}$ |
| 花体 | `\mathcal{L}` | $\mathcal{L}$ |
| 黑板粗体 | `\mathbb{R}` | $\mathbb{R}$ |

### 9.5 分段函数

```latex
f(x) = \begin{cases} 
x^2, & x > 0 \\
0, & x = 0 \\
-x, & x < 0 
\end{cases}
```
$$
f(x) = \begin{cases} 
x^2, & x > 0 \\
0, & x = 0 \\
-x, & x < 0 
\end{cases}
$$

### 9.6 多行公式对齐

```latex
\begin{aligned}
(a+b)^2 &= a^2 + 2ab + b^2 \\
(a-b)^2 &= a^2 - 2ab + b^2 \\
a^2 - b^2 &= (a+b)(a-b)
\end{aligned}
```
$$
\begin{aligned}
(a+b)^2 &= a^2 + 2ab + b^2 \\
(a-b)^2 &= a^2 - 2ab + b^2 \\
a^2 - b^2 &= (a+b)(a-b)
\end{aligned}
$$

### 9.7 方程组

```latex
\begin{cases}
x + y = 5 \\
2x - y = 1
\end{cases}
```
$$
\begin{cases}
x + y = 5 \\
2x - y = 1
\end{cases}
$$

### 9.8 上下标组合

| 写法 | LaTeX | 效果 |
|------|-------|------|
| 上标 | `x^2` | $x^2$ |
| 下标 | `x_i` | $x_i$ |
| 多字符上标 | `x^{n+1}` | $x^{n+1}$ |
| 多字符下标 | `x_{i+1}` | $x_{i+1}$ |
| 上下都有 | `x_i^2` | $x_i^2$ |
| 导数 | `f'(x)` | $f'(x)$ |
| 二阶导 | `f''(x)` | $f''(x)$ |

### 9.9 常见等式

```latex
a^2 - b^2 = (a+b)(a-b)
```
$$
a^2 - b^2 = (a+b)(a-b)
$$

```latex
(a+b)^n = \sum_{k=0}^n C_n^k a^{n-k} b^k
```
$$
(a+b)^n = \sum_{k=0}^n C_n^k a^{n-k} b^k
$$

```latex
\sin^2 x + \cos^2 x = 1
```
$$
\sin^2 x + \cos^2 x = 1
$$

```latex
\sec^2 x = 1 + \tan^2 x
```
$$
\sec^2 x = 1 + \tan^2 x
$$

---

## 十、LaTeX Suite 快捷输入

| 输入 | 替换为 | 效果 |
|------|--------|------|
| `ff` | `\frac{}{}` | 分数 |
| `sq` | `\sqrt{}` | 根号 |
| `pp` | `^{} ` | 上标 |
| `__` | `_{} ` | 下标 |
| `inn` | `\int` | 积分 |
| `sum` | `\sum` | 求和 |
| `lim` | `\lim` | 极限 |
| `->` | `\to` | 箭头 |
| `>=` | `\geq` | 大于等于 |
| `<=` | `\leq` | 小于等于 |
| `!=` | `\neq` | 不等于 |
| `...` | `\cdots` | 省略号 |
| `**` | `\cdot` | 点乘 |
| `xx` | `\times` | 叉乘 |
| `||` | `\mid` | 整除 |
| `AA` | `\forall` | 任意 |
| `EE` | `\exists` | 存在 |
| `RR` | `\mathbb{R}` | 实数集 |
| `ZZ` | `\mathbb{Z}` | 整数集 |
| `NN` | `\mathbb{N}` | 自然数集 |

---

*本手册涵盖考研数学常用LaTeX公式，建议收藏备用。*
