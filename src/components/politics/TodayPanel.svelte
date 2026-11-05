<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { daysBetween, politicsStore, weekdayLabel } from "@/lib/politics/store.svelte";
import type { Card, PlanDay } from "@/lib/politics/types";

interface Props {
	planDay: PlanDay | null;
	plan: PlanDay[];
	cards: Card[];
	queue: Card[];
	dueCards: Card[];
	newPlanCards: Card[];
	beforeStart: boolean;
	afterEnd: boolean;
	today: string;
	examDate: string;
	onStart: () => void;
	onStartDue: () => void;
	onOpenTopics: () => void;
}

let {
	planDay,
	plan,
	cards,
	queue,
	dueCards,
	newPlanCards,
	beforeStart,
	afterEnd,
	today,
	examDate,
	onStart,
	onStartDue,
	onOpenTopics,
}: Props = $props();

const examDays = $derived(daysBetween(today, examDate));

const dayCards = $derived.by(() => {
	if (!planDay) return [];
	const ids = new Set(planDay.pointIds);
	return cards.filter((card) => ids.has(card.pointId));
});
const dayPointCount = $derived(new Set(dayCards.map((card) => card.pointId)).size);
const doneCards = $derived(dayCards.filter((card) => Boolean(politicsStore.records[card.id])).length);
const dayProgress = $derived(dayCards.length ? Math.round((doneCards / dayCards.length) * 100) : 0);

const pointsPreview = $derived.by(() => {
	const map = new Map<string, { title: string; count: number; page: number }>();
	for (const card of dayCards) {
		const row = map.get(card.pointId);
		if (row) row.count += 1;
		else map.set(card.pointId, { title: card.pointTitle, count: 1, page: card.page });
	}
	return [...map.values()];
});

const planDone = $derived(
	plan.filter((day) => {
		const list = cards.filter((card) => day.pointIds.includes(card.pointId));
		return list.length > 0 && list.every((card) => politicsStore.records[card.id]);
	}).length,
);
const planPct = $derived(plan.length ? Math.round((planDone / plan.length) * 100) : 0);
const planPreview = $derived(plan.slice(Math.max(0, (planDay?.day ?? 1) - 2), Math.max(0, (planDay?.day ?? 1) - 2) + 7));

const phaseLabel = $derived(beforeStart ? "明天开始" : afterEnd ? "计划已完成" : `第 ${planDay?.day ?? 1} 天 · ${planDay?.phase ?? "第一轮"}`);
const ctaLabel = $derived(beforeStart ? "提前开始第 1 天" : afterEnd ? "复习到期卡片" : `开始今日 ${Math.max(15, Math.round(queue.length * 2.2))} 分钟`);
</script>

<div class="pol-today-grid">
	<section class="pol-card pol-pad">
		<div class="flex flex-wrap items-start justify-between gap-3">
			<div>
				<p class="pol-eyebrow">Today · {weekdayLabel(today)}</p>
				<h3 class="mt-2 text-2xl font-black tracking-tight text-90 md:text-3xl">
					{phaseLabel}
				</h3>
				<p class="pol-section-sub mt-1">
					{#if beforeStart}
						计划从 {plan[0]?.date ?? "2026-11-06"} 开始。今天可以先热身，把第 1 天的马原卡片过一遍。
					{:else if afterEnd}
						31 天计划已经走完。现在只做到期复习，保持手感，不再追求新卡数量。
					{:else}
						{planDay?.focus ?? "先回忆，再揭晓"} · 第 {planDay?.pages?.join("、") ?? "—"} 页
					{/if}
				</p>
			</div>
			<div class="pol-chip pol-chip-warm">
				<Icon icon="material-symbols:timer-rounded" class="text-sm" />
				约 {Math.max(15, planDay?.minutes ?? 40)} 分钟
			</div>
		</div>

		<div class="mt-4 flex flex-wrap gap-2">
			<span class="pol-chip pol-chip-primary">
				<Icon icon="material-symbols:menu-book-rounded" class="text-sm" />
				{dayCards.length} 张卡 / {dayPointCount} 个考点
			</span>
			<span class="pol-chip">
				<Icon icon="material-symbols:menu-book-rounded" class="text-sm" />
				第 {planDay?.pages?.join("、") ?? "—"} 页
			</span>
			<span class="pol-chip">
				<Icon icon="material-symbols:event-rounded" class="text-sm" />
				距初试 {examDays} 天
			</span>
		</div>

		<div class="mt-4">
			<div class="mb-1.5 flex items-center justify-between text-[0.65rem] text-40">
				<span>本日卡片熟悉度</span>
				<span>{doneCards}/{dayCards.length}</span>
			</div>
			<div class="pol-progress"><span style={`width:${dayProgress}%`}></span></div>
		</div>

		<div class="mt-5">
			<div class="mb-1 flex items-center justify-between">
				<h4 class="pol-section-title">今天要拿下的考点</h4>
				<button type="button" class="pol-link text-xs" onclick={onOpenTopics}>按专题看</button>
			</div>
			{#if pointsPreview.length}
				<div class="mt-1">
					{#each pointsPreview.slice(0, 8) as point (point.title)}
						<div class="pol-plan-point">
							<span class="pol-plan-dot"></span>
							<span class="pol-plan-point-text">{point.title}</span>
							<span class="pol-list-meta shrink-0">p{point.page} · {point.count} 张</span>
						</div>
					{/each}
					{#if pointsPreview.length > 8}
						<p class="mt-2 text-[0.68rem] text-40">还有 {pointsPreview.length - 8} 个考点，进入卡片队列继续。</p>
					{/if}
				</div>
			{:else}
				<div class="pol-empty mt-2">今天没有新卡，做一轮到期复习就够了。</div>
			{/if}
		</div>

		<div class="mt-5 flex flex-wrap items-center gap-2">
			<button type="button" class="pol-button pol-button-primary" onclick={onStart}>
				<Icon icon="material-symbols:play-arrow-rounded" class="text-lg" />
				{ctaLabel}
			</button>
			{#if dueCards.length > 0}
				<button type="button" class="pol-button pol-button-ghost" onclick={onStartDue}>
					<Icon icon="material-symbols:refresh-rounded" class="text-base" />
					先复习到期 {dueCards.length} 张
				</button>
			{/if}
			<span class="text-[0.66rem] text-30">按 Space 揭晓 · 1–4 评分</span>
		</div>
	</section>

	<div class="space-y-3">
		<section class="pol-card pol-pad">
			<div class="flex items-center justify-between gap-2">
				<div>
					<h4 class="pol-section-title">今日队列</h4>
					<p class="pol-section-sub">新卡优先，到期卡穿插。</p>
				</div>
				<span class="pol-chip pol-chip-primary">{queue.length} 张</span>
			</div>
			<div class="mt-3 grid grid-cols-3 gap-2">
				<div class="pol-stat">
					<span class="pol-stat-value">{newPlanCards.length}</span>
					<span class="pol-stat-label">新卡</span>
				</div>
				<div class="pol-stat">
					<span class="pol-stat-value">{dueCards.length}</span>
					<span class="pol-stat-label">到期</span>
				</div>
				<div class="pol-stat">
					<span class="pol-stat-value">{politicsStore.reviewedOn(today)}</span>
					<span class="pol-stat-label">今日已背</span>
				</div>
			</div>
			<div class="mt-3 flex items-center justify-between text-[0.66rem] text-40">
				<span>连续 {politicsStore.streak} 天</span>
				<span>{afterEnd ? "自由复习" : beforeStart ? "提前预习" : `第 ${planDay?.day ?? 1}/${plan.length} 天`}</span>
			</div>
		</section>

		<section class="pol-card pol-pad">
			<h4 class="pol-section-title">怎么背这张卡</h4>
			<div class="mt-2 space-y-2">
				<div class="pol-hint-line">
					<span class="pol-hint-index">01</span>
					<span>先只看标题，主动回忆关键词和对应关系。</span>
				</div>
				<div class="pol-hint-line">
					<span class="pol-hint-index">02</span>
					<span>揭晓答案，用彩色词校准；灰色解释先不用逐字背。</span>
				</div>
				<div class="pol-hint-line">
					<span class="pol-hint-index">03</span>
					<span>按“忘记 / 模糊 / 记得 / 熟练”评分，系统排下一次。</span>
				</div>
			</div>
			<div class="mt-3 rounded-lg bg-(--btn-regular-bg) p-2.5 text-[0.68rem] leading-relaxed text-60">
				页面只保留 A→B 对应，不要求逐字复述。会议、土地政策、统一战线是性价比最高的专题。
			</div>
		</section>

		<section class="pol-card pol-pad">
			<div class="flex items-center justify-between gap-2">
				<div>
					<h4 class="pol-section-title">31 天总进度</h4>
					<p class="pol-section-sub">11-06 → 12-06 · 网格显示当前 7 天</p>
				</div>
				<span class="text-xs font-bold text-(--primary)">{planPct}%</span>
			</div>
			<div class="pol-progress mt-2"><span style={`width:${planPct}%`}></span></div>
			<div class="pol-plan-grid mt-3">
				{#each planPreview as day (day.date)}
					{@const isToday = day.date === today}
					{@const list = cards.filter((card) => day.pointIds.includes(card.pointId))}
					{@const done = list.length > 0 && list.every((card) => politicsStore.records[card.id])}
					<div class={`pol-plan-day ${isToday ? "pol-plan-day-today" : ""} ${done ? "pol-plan-day-done" : ""}`}>
						<div class="pol-plan-day-date">{day.date.slice(5)}</div>
						<div class="pol-plan-day-main">D{day.day} · p{day.pages.join(",")}</div>
					</div>
				{/each}
			</div>
			<p class="mt-2 text-[0.64rem] text-30">计划只排到 12 月初；之后进入自由复习，按到期队列走。</p>
		</section>
	</div>
</div>
