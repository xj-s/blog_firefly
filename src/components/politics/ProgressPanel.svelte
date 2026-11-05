<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { daysBetween, politicsStore, todayKey, weekdayLabel } from "@/lib/politics/store.svelte";
import type { Card, PlanDay, PoliticsMeta } from "@/lib/politics/types";

interface Props {
	cards: Card[];
	plan: PlanDay[];
	meta: PoliticsMeta | null;
	studiedCount: number;
	masteredCount: number;
	onToast: (message: string) => void;
}

let { cards, plan, meta, studiedCount, masteredCount, onToast }: Props = $props();

let importInput: HTMLInputElement | undefined = $state();
let busy = $state(false);

const today = $derived(todayKey());
const examDays = $derived(daysBetween(today, meta?.examDate ?? "2026-12-19"));
const due = $derived(politicsStore.dueCount(cards, today));
const wrong = $derived(Object.values(politicsStore.records).filter((record) => record.lapses > 0).length);
const marked = $derived(Object.values(politicsStore.records).filter((record) => record.marked).length);
const week = $derived(politicsStore.week());
const maxWeek = $derived(Math.max(1, ...week.map((day) => day.count)));
const planDone = $derived(
	plan.filter((day) => {
		const list = cards.filter((card) => day.pointIds.includes(card.pointId));
		return list.length > 0 && list.every((card) => politicsStore.records[card.id]);
	}).length,
);
const planPct = $derived(plan.length ? Math.round((planDone / plan.length) * 100) : 0);
const sections = $derived(meta?.sections ?? []);

function sectionStats(sectionId: string) {
	const list = cards.filter((card) => card.section === sectionId);
	const studied = list.filter((card) => politicsStore.records[card.id]?.reviews).length;
	const mastered = list.filter((card) => (politicsStore.records[card.id]?.stage ?? 0) >= 5).length;
	return { list, studied, mastered, pct: list.length ? Math.round((studied / list.length) * 100) : 0 };
}

function planDayStats(day: PlanDay) {
	const list = cards.filter((card) => day.pointIds.includes(card.pointId));
	const done = list.filter((card) => politicsStore.records[card.id]).length;
	return { total: list.length, done };
}

function exportData() {
	const blob = new Blob([politicsStore.exportJson()], { type: "application/json" });
	const url = URL.createObjectURL(blob);
	const link = document.createElement("a");
	link.href = url;
	link.download = `politics-progress-${today}.json`;
	link.click();
	URL.revokeObjectURL(url);
	onToast("背诵记录已导出");
}

async function importData(event: Event) {
	const input = event.target as HTMLInputElement;
	const file = input.files?.[0];
	if (!file) return;
	busy = true;
	try {
		const text = await file.text();
		const result = politicsStore.importJson(text);
		onToast(result.message);
	} catch {
		onToast("读取文件失败");
	} finally {
		busy = false;
		input.value = "";
	}
}

function resetData() {
	if (!window.confirm("确定清空本机上的政治背诵记录？此操作不可撤销。")) return;
	politicsStore.reset();
	onToast("已清空本机记录");
}
</script>

<section class="pol-card pol-pad">
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div>
			<p class="pol-eyebrow">Progress</p>
			<h3 class="mt-2 text-2xl font-black tracking-tight text-90">背诵进度</h3>
			<p class="pol-section-sub">看总量，也看每一天是否真的走完。记录只在本机。</p>
		</div>
		<span class="pol-chip pol-chip-warm">
			<Icon icon="material-symbols:event-rounded" class="text-sm" />
			距初试 {examDays} 天
		</span>
	</div>

	<div class="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
		<div class="pol-stat"><span class="pol-stat-value">{studiedCount}</span><span class="pol-stat-label">已背卡片</span></div>
		<div class="pol-stat"><span class="pol-stat-value">{masteredCount}</span><span class="pol-stat-label">已掌握</span></div>
		<div class="pol-stat"><span class="pol-stat-value">{due}</span><span class="pol-stat-label">到期复习</span></div>
		<div class="pol-stat"><span class="pol-stat-value">{wrong}</span><span class="pol-stat-label">错题</span></div>
		<div class="pol-stat"><span class="pol-stat-value">{politicsStore.streak}</span><span class="pol-stat-label">连续天数</span></div>
		<div class="pol-stat"><span class="pol-stat-value">{politicsStore.reviewedOn(today)}</span><span class="pol-stat-label">今日已背</span></div>
	</div>

	<div class="mt-4 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
		<div>
			<div class="flex items-center justify-between">
				<h4 class="pol-section-title">31 天计划</h4>
				<span class="text-xs font-bold text-(--primary)">{planDone}/{plan.length} · {planPct}%</span>
			</div>
			<div class="pol-progress mt-2"><span style={`width:${planPct}%`}></span></div>
			<div class="pol-plan-grid mt-3">
				{#each plan as day (day.date)}
					{@const stats = planDayStats(day)}
					{@const done = stats.total > 0 && stats.done === stats.total}
					<div class={`pol-plan-day ${day.date === today ? "pol-plan-day-today" : ""} ${done ? "pol-plan-day-done" : ""}`}>
						<div class="pol-plan-day-date">{day.date.slice(5)} · {weekdayLabel(day.date)}</div>
						<div class="pol-plan-day-main">D{day.day} · p{day.pages.join(",")}</div>
						<div class="mt-0.5 text-[0.58rem] text-30">{stats.done}/{stats.total} 张</div>
					</div>
				{/each}
			</div>
			<p class="mt-2 text-[0.64rem] text-30">计划只排到 12-06；之后按到期队列自由复习。</p>
		</div>

		<div>
			<div class="flex items-center justify-between">
				<h4 class="pol-section-title">近 7 天</h4>
				<span class="text-[0.64rem] text-30">每天揭晓并评分的次数</span>
			</div>
			<div class="mt-3 flex h-32 items-end gap-1.5">
				{#each week as day (day.key)}
					<div class="flex flex-1 flex-col items-center gap-1">
						<span class="text-[0.6rem] text-40">{day.count || ""}</span>
						<div
							class="w-full rounded-t-md bg-(--primary) opacity-80"
							style={`height:${Math.max(4, Math.round((day.count / maxWeek) * 88))}px`}
						></div>
						<span class="text-[0.58rem] text-30">{day.label}</span>
					</div>
				{/each}
			</div>
			<div class="mt-3 flex items-center justify-between rounded-lg bg-(--btn-regular-bg) px-2.5 py-2 text-[0.66rem] text-50">
				<span>收藏 {marked} 张</span>
				<span>错题 {wrong} 张</span>
			</div>
		</div>
	</div>

	<div class="mt-5">
		<h4 class="pol-section-title">分板块掌握度</h4>
		<div class="mt-2 space-y-3">
			{#each sections as section (section.id)}
				{@const stats = sectionStats(section.id)}
				<div>
					<div class="mb-1 flex items-center justify-between text-[0.7rem]">
						<span class="flex items-center gap-2 text-70">
							<span class="pol-section-swatch" style={`background:${section.color}`}></span>
							{section.name}
						</span>
						<span class="text-40">{stats.studied}/{stats.list.length} 已背 · {stats.mastered} 掌握</span>
					</div>
					<div class="pol-progress"><span style={`width:${stats.pct}%`}></span></div>
				</div>
			{/each}
		</div>
	</div>

	<div class="mt-5 flex flex-wrap items-center gap-2 border-t border-(--line-divider) pt-4">
		<button type="button" class="pol-button pol-button-ghost" onclick={exportData}>
			<Icon icon="material-symbols:download-rounded" class="text-base" />
			导出记录
		</button>
		<button type="button" class="pol-button pol-button-ghost" disabled={busy} onclick={() => importInput?.click()}>
			<Icon icon="material-symbols:upload-rounded" class="text-base" />
			导入记录
		</button>
		<input bind:this={importInput} type="file" accept="application/json,.json" class="hidden" onchange={importData} />
		<button type="button" class="pol-button pol-button-ghost !text-red-500" onclick={resetData}>
			<Icon icon="material-symbols:delete-outline-rounded" class="text-base" />
			清空本机记录
		</button>
		<span class="text-[0.64rem] text-30">换设备前先导出 JSON 备份。</span>
	</div>
</section>
