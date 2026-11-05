<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { cardsForPoints, loadCards, loadIndex, loadMeta, loadPlan, loadPoints } from "@/lib/politics/data";
import { politicsStore, todayKey } from "@/lib/politics/store.svelte";
import type { Card, IndexRow, PlanDay, Point, PoliticsMeta } from "@/lib/politics/types";
import { onMount } from "svelte";
import CardsPanel from "./CardsPanel.svelte";
import LookupPanel from "./LookupPanel.svelte";
import ProgressPanel from "./ProgressPanel.svelte";
import StudySession from "./StudySession.svelte";
import TodayPanel from "./TodayPanel.svelte";
import TopicsPanel from "./TopicsPanel.svelte";

type Tab = "today" | "cards" | "lookup" | "topics" | "progress";

let tab: Tab = $state("today");
let meta: PoliticsMeta | null = $state(null);
let indexRows: IndexRow[] = $state([]);
let plan: PlanDay[] = $state([]);
let cards: Card[] = $state([]);
let points: Point[] = $state([]);
let loading = $state(true);
let loadError = $state("");
let toast = $state("");
let toastTimer: ReturnType<typeof setTimeout> | undefined;
let session: { cards: Card[]; title: string } | null = $state(null);

const tabs: { key: Tab; label: string; icon: string }[] = [
	{ key: "today", label: "今日", icon: "material-symbols:today-rounded" },
	{ key: "cards", label: "背卡", icon: "material-symbols:menu-book-rounded" },
	{ key: "lookup", label: "查考点", icon: "material-symbols:search" },
	{ key: "topics", label: "专题", icon: "material-symbols:account-tree-rounded" },
	{ key: "progress", label: "进度", icon: "material-symbols:insights-rounded" },
];

function showToast(message: string) {
	toast = message;
	if (toastTimer) clearTimeout(toastTimer);
	toastTimer = setTimeout(() => {
		toast = "";
	}, 2400);
}

const today = $derived(todayKey());
const planDay = $derived.by(() => {
	if (!plan.length) return null;
	return (
		plan.find((day) => day.date === today) ??
		plan.find((day) => day.date > today) ??
		plan[plan.length - 1]
	);
});
const beforeStart = $derived(Boolean(plan.length && today < plan[0].date));
const afterEnd = $derived(Boolean(plan.length && today > plan[plan.length - 1].date));

const planCards = $derived.by(() => {
	if (!planDay) return [];
	const eligible = beforeStart ? [planDay] : plan.filter((day) => day.date <= today);
	return cardsForPoints(
		cards,
		eligible.flatMap((day) => day.pointIds),
	);
});
const dueCards = $derived(politicsStore.dueCards(cards, today));
const newPlanCards = $derived(planCards.filter((card) => !politicsStore.records[card.id]));
const queue = $derived.by(() => {
	const unique = new Map<string, Card>();
	for (const card of [...dueCards, ...newPlanCards]) unique.set(card.id, card);
	return [...unique.values()].slice(0, 40);
});

const studiedCount = $derived(
	Object.values(politicsStore.records).filter((record) => record.reviews > 0).length,
);
const masteredCount = $derived(
	Object.values(politicsStore.records).filter((record) => record.stage >= 5).length,
);

function startSession(list: Card[], title: string) {
	if (!list.length) {
		showToast("这里还没有可背的卡片");
		return;
	}
	session = { cards: list, title };
}

function startToday() {
	startSession(queue, afterEnd ? "自由复习" : beforeStart ? "提前开始 · 第 1 天" : `今日背诵 · 第 ${planDay?.day ?? 1} 天`);
}

function startDue() {
	startSession(dueCards, "到期复习");
}

onMount(() => {
	politicsStore.load();
	Promise.all([loadMeta(), loadIndex(), loadPlan(), loadCards(), loadPoints()])
		.then(([info, rows, days, cardRows, pointRows]) => {
			meta = info;
			indexRows = rows;
			plan = days;
			cards = cardRows;
			points = pointRows;
			loading = false;
			const params = new URLSearchParams(window.location.search);
			const initial = params.get("p");
			if (initial) {
				tab = "lookup";
			}
		})
		.catch((error) => {
			console.error("politics data load failed", error);
			loadError = "政治资料加载失败，请刷新页面或检查网络。";
			loading = false;
		});
});
</script>

<div class="politics-page space-y-4" data-pagefind-ignore data-politics-page>
	{#if session}
		<StudySession
			cards={session.cards}
			title={session.title}
			examDate={meta?.examDate ?? "2026-12-19"}
			onExit={() => {
				session = null;
				tab = "today";
			}}
		/>
	{:else}
		<section class="pol-hero">
			<div class="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
				<div class="min-w-0">
					<div class="pol-eyebrow">
						<span class="pol-eyebrow-icon">
							<Icon icon="material-symbols:account-balance-rounded" class="text-base" />
						</span>
						Postgrad Politics Lab
					</div>
					<h2 class="pol-title">把知识点背成条件反射</h2>
					<p class="pol-sub">
						以 27 考研政治一页纸为蓝本：先遮住答案回忆，再按彩色关键词校对。
						100 个考点拆成 {cards.length || "—"} 张卡，每天 30–40 分钟，先过一轮再回炉。
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-2">
						<span class="pol-exam-note">
							<Icon icon="material-symbols:event-rounded" class="text-sm" />
							初试 {meta?.examDate ?? "2026-12-19"} · 计划到 {meta?.planEnd ?? "2026-12-06"}
						</span>
						<span class="pol-chip">先回忆，再揭晓</span>
						<span class="pol-chip">只背 A→B 对应</span>
					</div>
				</div>

				<div class="pol-hero-stats shrink-0">
					<div class="pol-stat">
						<span class="pol-stat-value">{meta?.pointCount ?? "—"}</span>
						<span class="pol-stat-label">考点</span>
					</div>
					<div class="pol-stat">
						<span class="pol-stat-value">{cards.length || "—"}</span>
						<span class="pol-stat-label">卡片</span>
					</div>
					<div class="pol-stat">
						<span class="pol-stat-value">{politicsStore.dueCount(cards, today)}</span>
						<span class="pol-stat-label">待复习</span>
					</div>
					<div class="pol-stat">
						<span class="pol-stat-value">{politicsStore.streak}</span>
						<span class="pol-stat-label">连续天数</span>
					</div>
				</div>
			</div>
		</section>

		<div class="flex flex-wrap items-center justify-between gap-2">
			<div class="pol-tabs" role="tablist" aria-label="政治背诵导航">
				{#each tabs as item (item.key)}
					<button
						type="button"
						role="tab"
						aria-selected={tab === item.key}
						class={`pol-tab ${tab === item.key ? "pol-tab-active" : ""}`}
						onclick={() => (tab = item.key)}
					>
						<Icon icon={item.icon} class="text-lg" />
						{item.label}
						{#if item.key === "cards"}
							<span class="pol-tab-count">{studiedCount}/{cards.length || "—"}</span>
						{:else if item.key === "today" && dueCards.length > 0}
							<span class="pol-tab-count pol-tab-count-warm">{dueCards.length}</span>
						{/if}
					</button>
				{/each}
			</div>
			<div class="hidden items-center gap-1.5 text-[0.65rem] text-30 sm:flex">
				<Icon icon="material-symbols:info-outline-rounded" class="text-sm" />
				本地优先 · 无需登录
			</div>
		</div>

		{#if loading}
			<div class="pol-card flex flex-col items-center justify-center px-6 py-16 text-center">
				<Icon icon="svg-spinners:ring-resize" class="text-3xl text-(--primary)" />
				<p class="mt-3 text-sm text-50">正在加载考点、卡片与每日计划…</p>
				<p class="mt-1 text-xs text-30">首次加载约 650 KB，之后走浏览器缓存</p>
			</div>
		{:else if loadError}
			<div class="pol-card px-6 py-14 text-center">
				<Icon icon="material-symbols:error-outline-rounded" class="text-3xl text-red-500" />
				<p class="mt-2 text-sm text-50">{loadError}</p>
				<button type="button" class="pol-button pol-button-primary mx-auto mt-4" onclick={() => location.reload()}>
					重新加载
				</button>
			</div>
		{:else}
			<div class:hidden={tab !== "today"}>
				<TodayPanel
					{planDay}
					{plan}
					{cards}
					{queue}
					{dueCards}
					{newPlanCards}
					{beforeStart}
					{afterEnd}
					today={today}
					examDate={meta?.examDate ?? "2026-12-19"}
					onStart={startToday}
					onStartDue={startDue}
					onOpenTopics={() => (tab = "topics")}
				/>
			</div>

			<div class:hidden={tab !== "cards"}>
				<CardsPanel {cards} onStudy={startSession} onToast={showToast} />
			</div>

			<div class:hidden={tab !== "lookup"}>
				<LookupPanel {points} {cards} onStudy={startSession} />
			</div>

			<div class:hidden={tab !== "topics"}>
				<TopicsPanel index={indexRows} {cards} {meta} onStudy={startSession} />
			</div>

			<div class:hidden={tab !== "progress"}>
				<ProgressPanel
					{cards}
					{plan}
					{meta}
					{studiedCount}
					{masteredCount}
					onToast={showToast}
				/>
			</div>
		{/if}

		<footer class="px-1 pb-1 pt-1 text-[0.62rem] leading-relaxed text-30">
			蓝本：《27考研政治一页纸·知识点手册》（澄潇宇）。卡片为结构化改写，保留原书彩色关键词与记忆口诀，
			用于个人学习；不替代原书。 progress 只保存在当前浏览器 localStorage，不上传服务器。
		</footer>
	{/if}

	{#if toast}
		<div class="pol-toast" role="status">
			<Icon icon="material-symbols:check-circle-rounded" class="text-base text-(--primary)" />
			{toast}
		</div>
	{/if}
</div>
