<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { cardsForPoint, figureUrl } from "@/lib/politics/data";
import type { Card, Point } from "@/lib/politics/types";
import { onMount } from "svelte";
import RichBlocks from "./RichBlocks.svelte";

interface Props {
	points: Point[];
	cards: Card[];
	initialQuery?: string;
	onStudy: (cards: Card[], title: string) => void;
}

let { points, cards, initialQuery = "", onStudy }: Props = $props();

let query = $state(initialQuery);
let active = $state<Point | null>(null);
let colorOnly = $state(false);

const suggestions = ["遵义会议", "统一战线", "土地政策", "剩余价值", "高质量发展", "依法治国"];

const results = $derived.by(() => {
	const q = query.trim().toLowerCase();
	if (!q) return [];
	return points
		.filter((point) => {
			const haystack = `${point.title} ${point.preview} ${point.sectionName} ${point.topic} ${point.keywords.join(" ")} ${point.blocks.map((block) => block.text).join(" ")}`;
			return haystack.toLowerCase().includes(q);
		})
		.slice(0, 40);
});

const activeCards = $derived(active ? cardsForPoint(cards, active.id) : []);

function openPoint(point: Point) {
	active = point;
	colorOnly = false;
}

onMount(() => {
	const params = new URLSearchParams(window.location.search);
	const id = params.get("p");
	if (id) {
		const found = points.find((point) => point.id === id);
		if (found) {
			active = found;
			return;
		}
	}
	const q = params.get("q");
	if (q) query = q;
});
</script>

<section class="pol-card pol-pad">
	<div class="flex flex-wrap items-start justify-between gap-3">
		<div>
			<p class="pol-eyebrow">Lookup</p>
			<h3 class="mt-2 text-2xl font-black tracking-tight text-90">查考点</h3>
			<p class="pol-section-sub">搜会议、政策、概念或关键词；也可以直接打开某个考点看原书彩色标注。</p>
		</div>
		<span class="pol-chip pol-chip-primary">{points.length} 个考点</span>
	</div>

	<label class="relative mt-4 block">
		<Icon icon="material-symbols:search-rounded" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-base text-30" />
		<input
			type="search"
			bind:value={query}
			placeholder="输入关键词，如 遵义会议 / 统一战线 / 土地政策 / 剩余价值"
			class="w-full rounded-lg border border-(--line-divider) bg-(--card-bg) py-2.5 pl-9 pr-3 text-sm text-90 outline-none transition focus:border-(--primary)"
		/>
	</label>

	<div class="mt-2 flex flex-wrap items-center gap-1.5">
		<span class="text-[0.64rem] text-30">试试</span>
		{#each suggestions as item (item)}
			<button type="button" class="pol-chip" onclick={() => (query = item)}>{item}</button>
		{/each}
	</div>

	{#if active}
		<article class="mt-4 rounded-xl border border-(--line-divider) bg-(--card-bg) p-4 md:p-5">
			<div class="flex flex-wrap items-start justify-between gap-3">
				<div class="min-w-0">
					<div class="flex flex-wrap gap-1.5">
						<span class="pol-chip pol-chip-primary">{active.sectionName}</span>
						<span class="pol-chip">第 {active.page} 页</span>
						{#if active.topic}<span class="pol-chip">{active.topic}</span>{/if}
						<span class="pol-chip">No.{active.id}</span>
					</div>
					<h4 class="mt-2 text-xl font-black tracking-tight text-90">{active.title}</h4>
				</div>
				<div class="flex flex-wrap gap-2">
					<button
						type="button"
						class="pol-button pol-button-primary"
						onclick={() => onStudy(activeCards, active?.title ?? "考点")}
					>
						<Icon icon="material-symbols:play-arrow-rounded" class="text-base" />
						背这个考点
					</button>
					<button type="button" class="pol-button pol-button-ghost" onclick={() => (active = null)}>
						收起
					</button>
				</div>
			</div>

			<div class="pol-answer-toolbar mt-4">
				<span class="pol-answer-title">原书卡片 · {activeCards.length} 张学习卡</span>
				<label class="pol-toggle">
					<input type="checkbox" bind:checked={colorOnly} />
					只看彩色
				</label>
			</div>

			{#if active.figure}
				<figure class="mb-4 overflow-hidden rounded-lg border border-(--line-divider) bg-white">
					<img
						src={figureUrl(active.figure.src)}
						alt={active.figure.alt || `${active.title} 时间轴`}
						class="h-auto w-full"
						loading="lazy"
					/>
				</figure>
			{:else if activeCards.length > 1}
				<div class="space-y-3">
					{#each activeCards as card (card.id)}
						<article class="rounded-lg border border-(--line-divider) bg-(--btn-regular-bg) p-3">
							<p class="mb-2 text-[0.68rem] font-extrabold tracking-wide text-70">{card.prompt}</p>
							<RichBlocks blocks={card.blocks} {colorOnly} compact />
						</article>
					{/each}
				</div>
			{:else}
				<RichBlocks blocks={active.blocks} {colorOnly} />
			{/if}

			{#if active.keywords.length}
				<div class="mt-4">
					<p class="mb-1.5 text-[0.62rem] font-extrabold uppercase tracking-[0.12em] text-30">关键词</p>
					<div class="pol-keyword-list">
						{#each active.keywords as keyword (keyword)}
							<span class="pol-keyword">{keyword}</span>
						{/each}
					</div>
				</div>
			{/if}
		</article>
	{:else if query.trim()}
		<div class="mt-4">
			<div class="flex items-center justify-between">
				<h4 class="pol-section-title">搜索结果</h4>
				<span class="text-[0.66rem] text-30">{results.length} 个考点</span>
			</div>
			{#if results.length}
				<div class="pol-card-list mt-2">
					{#each results as point (point.id)}
						<button type="button" class="pol-list-card text-left" onclick={() => openPoint(point)}>
							<div class="flex items-start justify-between gap-3">
								<div>
									<h5 class="pol-list-title">{point.title}</h5>
									<p class="pol-list-meta mt-1">{point.preview}</p>
								</div>
								<Icon icon="material-symbols:chevron-right-rounded" class="shrink-0 text-xl text-30" />
							</div>
							<div class="flex flex-wrap gap-1">
								<span class="pol-chip">{point.sectionName}</span>
								<span class="pol-chip">p{point.page}</span>
								{#if point.topic}<span class="pol-chip">{point.topic}</span>{/if}
							</div>
						</button>
					{/each}
				</div>
			{:else}
				<div class="pol-empty mt-3">没有找到。试试“遵义会议”“统一战线”“土地政策”这类专题词。</div>
			{/if}
		</div>
	{:else}
		<div class="mt-4 flex items-center justify-between">
			<h4 class="pol-section-title">常考考点</h4>
			<span class="text-[0.64rem] text-30">共 100 个 · 输入关键词检索</span>
		</div>
		<div class="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
			{#each points.slice(0, 6) as point (point.id)}
				<button type="button" class="pol-list-card text-left" onclick={() => openPoint(point)}>
					<div class="flex items-center justify-between gap-2">
						<span class="pol-chip">{point.sectionName}</span>
						<span class="pol-list-meta">p{point.page}</span>
					</div>
					<h5 class="pol-list-title">{point.title}</h5>
					<p class="pol-list-meta line-clamp-2">{point.preview}</p>
				</button>
			{/each}
		</div>
	{/if}
</section>
