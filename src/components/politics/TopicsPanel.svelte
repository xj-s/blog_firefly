<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { politicsStore } from "@/lib/politics/store.svelte";
import type { Card, IndexRow, PoliticsMeta } from "@/lib/politics/types";

interface Props {
	index: IndexRow[];
	cards: Card[];
	meta: PoliticsMeta | null;
	onStudy: (cards: Card[], title: string) => void;
}

let { index, cards, meta, onStudy }: Props = $props();

let activeSection = $state(meta?.sections?.[0]?.id ?? "mayuan");

const sections = $derived(meta?.sections ?? []);
const section = $derived(sections.find((item) => item.id === activeSection) ?? sections[0]);
const sectionPoints = $derived(index.filter((point) => point.section === activeSection));
const sectionCards = $derived(cards.filter((card) => card.section === activeSection));
const studied = $derived(sectionCards.filter((card) => politicsStore.records[card.id]?.reviews).length);
const mastered = $derived(sectionCards.filter((card) => (politicsStore.records[card.id]?.stage ?? 0) >= 5).length);
const progress = $derived(sectionCards.length ? Math.round((studied / sectionCards.length) * 100) : 0);

const groups = $derived.by(() => {
	const map = new Map<string, IndexRow[]>();
	for (const point of sectionPoints) {
		const key = point.topic || "考点";
		const list = map.get(key);
		if (list) list.push(point);
		else map.set(key, [point]);
	}
	return [...map.entries()];
});

function cardsOfPoint(pointId: string): Card[] {
	return cards.filter((card) => card.pointId === pointId);
}

function cardCountOfSection(id: string): number {
	return cards.filter((card) => card.section === id).length;
}

function pointStatus(pointId: string): "new" | "learning" | "done" {
	const list = cardsOfPoint(pointId);
	if (!list.length) return "new";
	const done = list.filter((card) => politicsStore.records[card.id]?.reviews).length;
	if (done === 0) return "new";
	if (done === list.length) return "done";
	return "learning";
}
</script>

<section class="pol-card pol-pad">
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div>
			<p class="pol-eyebrow">Sections</p>
			<h3 class="mt-2 text-2xl font-black tracking-tight text-90">按专题背</h3>
			<p class="pol-section-sub">先按板块建立框架，再回到今日队列逐张过。会议、土地政策、统一战线优先。</p>
		</div>
		<button type="button" class="pol-button pol-button-primary" onclick={() => onStudy(sectionCards, section?.name ?? "专题")}>
			<Icon icon="material-symbols:play-arrow-rounded" class="text-base" />
			背这一节
		</button>
	</div>

	<div class="mt-4 flex flex-wrap gap-1.5">
		{#each sections as item (item.id)}
			<button
				type="button"
				class={`pol-chip ${activeSection === item.id ? "pol-chip-primary" : ""}`}
				onclick={() => (activeSection = item.id)}
			>
				<span class="pol-section-swatch" style={`background:${item.color}`}></span>
				{item.name}
				<span class="text-30">{cardCountOfSection(item.id)}</span>
			</button>
		{/each}
	</div>

	{#if section}
		<div class="mt-4 rounded-xl border border-(--line-divider) bg-(--btn-regular-bg) p-3.5">
			<div class="flex flex-wrap items-center justify-between gap-2">
				<div>
					<h4 class="text-base font-extrabold text-90">{section.name}</h4>
					<p class="mt-0.5 text-[0.68rem] text-50">
						p{section.startPage}–p{section.endPage} · {sectionPoints.length} 个考点 · {sectionCards.length} 张卡
					</p>
				</div>
				<div class="flex items-center gap-2 text-[0.68rem] text-50">
					<span>已背 {studied}</span>
					<span>掌握 {mastered}</span>
					<span class="font-bold text-(--primary)">{progress}%</span>
				</div>
			</div>
			<div class="pol-progress mt-2"><span style={`width:${progress}%`}></span></div>
		</div>

		<div class="mt-4">
			{#each groups as [topic, rows] (topic)}
				<div class="pol-topic-group">
					<p class="pol-topic-title">{topic}</p>
					<div class="mt-1">
						{#each rows as point (point.id)}
							{@const status = pointStatus(point.id)}
							<div class="pol-point-row">
								<button type="button" class="pol-point-row-button" onclick={() => onStudy(cardsOfPoint(point.id), point.title)}>
									<span class="pol-point-row-index">{point.id}</span>
									<span class="pol-point-row-title">{point.title}</span>
									<span class="pol-chip">p{point.page}</span>
									<span class={`pol-chip ${status === "new" ? "pol-chip-primary" : status === "done" ? "pol-chip-warm" : ""}`}>
										{status === "new" ? "未背" : status === "done" ? "已背" : "复习中"}
									</span>
								</button>
								<Icon icon="material-symbols:chevron-right-rounded" class="shrink-0 text-lg text-30" />
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="pol-empty mt-4">资料还没加载好。</div>
	{/if}
</section>
