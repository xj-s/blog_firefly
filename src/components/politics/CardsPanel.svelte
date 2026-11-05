<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { politicsStore } from "@/lib/politics/store.svelte";
import type { Card, StudyStatus } from "@/lib/politics/types";

interface Props {
	cards: Card[];
	onStudy: (cards: Card[], title: string) => void;
	onToast: (message: string) => void;
}

let { cards, onStudy, onToast }: Props = $props();

let section = $state("all");
let status = $state<"all" | StudyStatus>("all");
let query = $state("");
let limit = $state(60);

const sections = $derived.by(() => {
	const map = new Map<string, { id: string; name: string; count: number }>();
	for (const card of cards) {
		const row = map.get(card.section);
		if (row) row.count += 1;
		else map.set(card.section, { id: card.section, name: card.sectionName, count: 1 });
	}
	return [...map.values()];
});

function statusOf(card: Card): StudyStatus {
	const record = politicsStore.records[card.id];
	if (!record) return "new";
	if (record.marked) return "marked";
	if (record.lapses > 0) return "wrong";
	if (record.stage >= 5) return "mastered";
	return "learning";
}

const statusLabels: Record<StudyStatus, string> = {
	new: "未背",
	learning: "复习中",
	mastered: "已掌握",
	marked: "收藏",
	wrong: "错题",
};

const statusOptions: { key: "all" | StudyStatus; label: string }[] = [
	{ key: "all", label: "全部" },
	{ key: "new", label: "未背" },
	{ key: "learning", label: "复习中" },
	{ key: "mastered", label: "已掌握" },
	{ key: "marked", label: "收藏" },
	{ key: "wrong", label: "错题" },
];

const counts = $derived.by(() => {
	const result: Record<string, number> = { all: cards.length, new: 0, learning: 0, mastered: 0, marked: 0, wrong: 0 };
	for (const card of cards) result[statusOf(card)] += 1;
	return result;
});

const filtered = $derived.by(() => {
	const q = query.trim().toLowerCase();
	return cards.filter((card) => {
		if (section !== "all" && card.section !== section) return false;
		if (status !== "all" && statusOf(card) !== status) return false;
		if (!q) return true;
		return `${card.title} ${card.pointTitle} ${card.topic} ${card.sectionName} ${card.keywords.join(" ")}`
			.toLowerCase()
			.includes(q);
	});
});

const visible = $derived(filtered.slice(0, limit));
</script>

<section class="pol-card pol-pad">
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div>
			<p class="pol-eyebrow">My Cards</p>
			<h3 class="mt-2 text-2xl font-black tracking-tight text-90">我的背诵卡</h3>
			<p class="pol-section-sub">
				{cards.length} 张卡，覆盖 {counts.new} 张未背、{counts.learning} 张复习中、{counts.mastered} 张已掌握。
			</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="pol-stat">
				<span class="pol-stat-value">{counts.new}</span>
				<span class="pol-stat-label">未背</span>
			</div>
			<div class="pol-stat">
				<span class="pol-stat-value">{politicsStore.dueCount(cards)}</span>
				<span class="pol-stat-label">到期</span>
			</div>
		</div>
	</div>

	<div class="mt-4 flex flex-col gap-2">
		<label class="relative block">
			<Icon icon="material-symbols:search-rounded" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-base text-30" />
			<input
				type="search"
				bind:value={query}
				placeholder="搜标题、专题或关键词，如 遵义会议 / 土地政策 / 剩余价值"
				class="w-full rounded-lg border border-(--line-divider) bg-(--card-bg) py-2 pl-9 pr-3 text-sm text-90 outline-none transition focus:border-(--primary)"
			/>
		</label>

		<div class="flex flex-wrap gap-1.5">
			<button
				type="button"
				class={`pol-chip ${section === "all" ? "pol-chip-primary" : ""}`}
				onclick={() => {
					section = "all";
					limit = 60;
				}}
			>
				全部 {cards.length}
			</button>
			{#each sections as item (item.id)}
				<button
					type="button"
					class={`pol-chip ${section === item.id ? "pol-chip-primary" : ""}`}
					onclick={() => {
						section = item.id;
						limit = 60;
					}}
				>
					{item.name} {item.count}
				</button>
			{/each}
		</div>

		<div class="flex flex-wrap gap-1.5">
			{#each statusOptions as option (option.key)}
				<button
					type="button"
					class={`pol-chip ${status === option.key ? "pol-chip-warm" : ""}`}
					onclick={() => {
						status = option.key;
						limit = 60;
					}}
				>
					{option.label} {counts[option.key] ?? 0}
				</button>
			{/each}
		</div>
	</div>

	<div class="mt-3 flex items-center justify-between text-[0.68rem] text-40">
		<span>筛选出 {filtered.length} 张</span>
		<button
			type="button"
			class="pol-link"
			onclick={() => onStudy([...filtered].filter((card) => statusOf(card) !== "mastered"), "筛选卡片")}
		>
			背这一组
		</button>
	</div>

	{#if visible.length}
		<div class="pol-card-list mt-2">
			{#each visible as card (card.id)}
				{@const state = statusOf(card)}
				<article class="pol-list-card">
					<div class="flex items-start justify-between gap-2">
						<div class="min-w-0">
							<h4 class="pol-list-title">{card.title}</h4>
							{#if card.pointTitle !== card.title}
								<p class="pol-list-meta mt-0.5">来自「{card.pointTitle}」</p>
							{/if}
						</div>
						<button
							type="button"
							class={`pol-icon-button shrink-0 ${politicsStore.records[card.id]?.marked ? "pol-icon-button-active" : ""}`}
							onclick={() => {
								const marked = politicsStore.toggleMark(card.id);
								onToast(marked ? "已收藏" : "已取消收藏");
							}}
							aria-label="收藏卡片"
						>
							<Icon icon={politicsStore.records[card.id]?.marked ? "material-symbols:star-rounded" : "material-symbols:star-outline-rounded"} class="text-base" />
						</button>
					</div>
					<div class="flex flex-wrap gap-1">
						<span class={`pol-chip ${state === "new" ? "pol-chip-primary" : state === "wrong" ? "pol-chip-warm" : ""}`}>
							{statusLabels[state]}
						</span>
						<span class="pol-chip">{card.sectionName}</span>
						<span class="pol-chip">p{card.page}</span>
						{#if card.part}<span class="pol-chip">{card.part}</span>{/if}
						{#if card.keywords.length}<span class="pol-chip">{card.keywords.length} 个关键词</span>{/if}
					</div>
					<div class="pol-list-foot">
						<span class="pol-list-meta">{card.hint}</span>
						<button type="button" class="pol-button pol-button-soft !px-2.5 !py-1.5" onclick={() => onStudy([card], card.title)}>
							背这张
						</button>
					</div>
				</article>
			{/each}
		</div>
		{#if filtered.length > limit}
			<div class="mt-3 text-center">
				<button type="button" class="pol-button pol-button-ghost" onclick={() => (limit += 60)}>
					再加载 60 张
				</button>
			</div>
		{/if}
	{:else}
		<div class="pol-empty mt-3">没有匹配的卡片，换个筛选条件试试。</div>
	{/if}
</section>
