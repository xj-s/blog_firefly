---
title: "第三章 进程管理"
published: 2026-05-29
description: "操作系统进程管理笔记，包括进程状态、调度算法、同步互斥与死锁"
image: ""
tags: ["操作系统", "进程", "调度算法", "同步互斥"]
category: "408/操作系统"
draft: false
pinned: false
---

## 3.1 进程的基本概念

### 进程的定义

进程是程序的一次执行过程，是系统进行**资源分配和调度**的基本单位。

> [!NOTE]
> 进程与程序的区别：进程是动态的，程序是静态的。一个程序可以对应多个进程。

### 进程的组成

- **PCB（进程控制块）**：进程存在的唯一标志
- **程序段**：存放要执行的代码
- **数据段**：存放程序运行时使用的数据

### 进程的状态与转换

进程的五种基本状态：

| 状态 | 含义 |
|------|------|
| 创建态 | 进程正在被创建 |
| 就绪态 | 进程已获得除 CPU 之外的所有资源 |
| 运行态 | 进程正在 CPU 上执行 |
| 阻塞态 | 进程因等待某事件而暂停运行 |
| 终止态 | 进程正在从系统中消失 |

状态转换关系：

```
创建态 → 就绪态 → 运行态 → 终止态
              ↑       ↓
              └── 阻塞态 ←┘
```

> [!TIP]
> **重点考点**：就绪态 → 运行态（进程调度）、运行态 → 就绪态（时间片到）、运行态 → 阻塞态（请求 I/O）、阻塞态 → 就绪态（I/O 完成）

## 3.2 进程调度算法

### FCFS（先来先服务）

```python
def fcfs(processes):
    """先来先服务调度算法"""
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.start_time = current_time
        p.wait_time = current_time - p.arrival_time
        current_time += p.burst_time
        p.finish_time = current_time
    return processes
```

### SJF（短作业优先）

短作业优先算法选择**运行时间最短**的作业优先执行：

$$T_{avg} = \frac{1}{n} \sum_{i=1}^{n} T_i$$

其中 $T_i = C_i - A_i$，$C_i$ 为完成时间，$A_i$ 为到达时间。

> [!WARNING]
> SJF 存在**饥饿问题**：长作业可能永远得不到执行。且需要预先知道作业的运行时间。

### 时间片轮转（RR）

时间片轮转算法的关键参数是时间片 $q$：

- $q$ 太大 → 退化为 FCFS
- $q$ 太小 → 上下文切换开销过大

## 3.3 进程同步与互斥

### 临界区问题

```c
// 进程 Pi 的通用结构
while (true) {
    entry section;      // 进入区：检查并设置标志
    critical section;   // 临界区：访问共享资源
    exit section;       // 退出区：清除标志
    remainder section;  // 剩余区：其他操作
}
```

### Peterson 算法

```c
bool flag[2] = {false, false};
int turn;

void process_i(int i) {
    int j = 1 - i;
    flag[i] = true;
    turn = j;
    while (flag[j] && turn == j)
        ; // 忙等待
    // 临界区
    critical_section();
    flag[i] = false;
}
```

### 信号量机制

$$P(S): S = S - 1; \text{if } S < 0 \text{ then block}$$
$$V(S): S = S + 1; \text{if } S \leq 0 \text{ then wakeup}$$

> [!NOTE]
> **考研高频考点**：用信号量实现生产者-消费者问题、读者-写者问题、哲学家进餐问题。务必熟练掌握！

---

*本章是操作系统的核心章节，建议结合王道考研视频 + 课本例题反复练习。*
