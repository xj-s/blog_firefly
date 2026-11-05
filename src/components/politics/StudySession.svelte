<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { figureUrl } from "@/lib/politics/data";
import { maxIntervalFor, politicsStore, todayKey } from "@/lib/politics/store.svelte";
import type { Card, Rating } from "@/lib/politics/types";
import RichBlocks from "./RichBlocks.svelte";

interface Props {
	cards: Card[];
	title: string;
	examDate: string;
	onExit: () => void;
}

let { cards, title, examDate, onExit }: Props = $props();

let queue: Card[] = $state([...cards]);
let index = $state(0);
let revealed = $state(false);
let hint = $state(false);
let colorOnly = $state(false);
let done = $state(false);
let ratedCount = $state(0);
let againCount = $state(0);
let startedAt = Date.now();

const card = $derived(queue[index]);
const total = $derived(queue.length);
const maxInterval = $derived(maxIntervalFor(todayKey(), examDate));
const progress = $derived(total ? Math.round(((index + (revealed ? 0.6 : 0)) / total) * 100) : 0);

const hintLines = $derived.by(() => {
	if (!card) return [];
	if (card.kind === "figure") {
		return ["1840", "1919 / 1925 / 1927", "1937 / 1945 / 1949", "1956 / 1978"];
	}
	return card.blocks.slice(0, 8).map((block) => {
		const text = block.text.trim();
		if (card.kind === "mnemonic") return `${text.slice(0, 2)}……`;
		return `${text.slice(0, 8)}……`;
	});
});

function reveal() {
	if (!card || revealed) return;
	revealed = true;
	hint = false;
}

function rate(rating: Rating) {
	if (!card || !revealed) return;
	const interval = politicsStore.rate(card.id, rating, maxInterval);
	ratedCount += 1;
	if (rating === "again") againCount += 1;
	if (index + 1 >= queue.length) {
		done = true;
	} else {
		index += 1;
		revealed = false;
		hint = false;
		colorOnly = false;
	}
	void interval;
}

function restart() {
	queue = [...cards];
	index = 0;
	revealed = false;
	hint = false;
	colorOnly = false;
	done = false;
	ratedCount = 0;
	againCount = 0;
	startedAt = Date.now();
}

function handleKey(event: KeyboardEvent) {
	const target = event.target as HTMLElement | null;
	if (target?.closest("input, textarea, [contenteditable='true']")) return;
	if (event.key === "Escape") {
		onExit();
		return;
	}
	if (!revealed && (event.key === " " || event.key === "Enter")) {
		event.preventDefault();
		reveal();
		return;
	}
	if (revealed && ["1", "2", "3", "4"].includes(event.key)) {
		event.preventDefault();
		const map: Record<string, Rating> = { "1": "again", "2": "hard", "3": "good", "4": "easy" };
		rate(map[event.key]);
		return;
	}
	if (event.key.toLowerCase() === "h") {
		event.preventDefault();
		hint = !hint;
	}
}

const elapsed = $derived(Math.max(1, Math.round((Date.now() - startedAt) / 60_000)));
</script>

<div class="space-y-3">
	<div class="pol-session-bar">
		<div class="flex min-w-0 items-center gap-2">
			<button type="button" class="pol-icon-button" onclick={onExit} aria-label="退出本轮">
				<Icon icon="material-symbols:arrow-back-rounded" class="text-base" />
			</button>
			<div class="min-w-0">
				<p class="truncate text-xs font-extrabold text-90">{title}</p>
				<p class="text-[0.64rem] text-40">
					{card?.sectionName ?? "自由复习"} · {card?.hint ?? "按 Space 揭晓"}
				</p>
			</div>
		</div>
		<div class="flex shrink-0 items-center gap-3">
			<span class="pol-chip">{index + 1} / {total}</span>
			<span class="pol-hide-sm text-[0.64rem] text-30">已背 {ratedCount} 张</span>
			<button type="button" class="pol-button pol-button-ghost !px-2.5 !py-1.5" onclick={onExit}>
				退出
			</button>
		</div>
	</div>

	<div class="pol-progress">
		<span style={`width:${done ? 100 : progress}%`}></span>
	</div>

	{#if done}
		<section class="pol-card pol-pad">
			<div class="mx-auto max-w-xl py-6 text-center">
				<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-(--btn-regular-bg) text-(--btn-content)">
					<Icon icon="material-symbols:task-alt-rounded" class="text-3xl" />
				</div>
				<h3 class="mt-4 text-2xl font-black tracking-tight text-90">这一轮背完了</h3>
				<p class="mt-2 text-sm leading-relaxed text-50">
					共 {total} 张，用时约 {elapsed} 分钟。忘记 {againCount} 张会回到今天的队列，明天再见面。
				</p>
				<div class="mt-4 grid grid-cols-3 gap-2">
					<div class="pol-stat">
						<span class="pol-stat-value">{total}</span>
						<span class="pol-stat-label">本轮卡片</span>
					</div>
					<div class="pol-stat">
						<span class="pol-stat-value">{againCount}</span>
						<span class="pol-stat-label">需要回炉</span>
					</div>
					<div class="pol-stat">
						<span class="pol-stat-value">{politicsStore.reviewedOn(todayKey())}</span>
						<span class="pol-stat-label">今日已背</span>
					</div>
				</div>
				<div class="mt-5 flex flex-wrap justify-center gap-2">
					<button type="button" class="pol-button pol-button-primary" onclick={onExit}>
						<Icon icon="material-symbols:today-rounded" class="text-base" />
						回到今日
					</button>
					<button type="button" class="pol-button pol-button-ghost" onclick={restart}>
						<Icon icon="material-symbols:refresh-rounded" class="text-base" />
						再背一轮
					</button>
				</div>
			</div>
		</section>
	{:else if card}
		<section class="pol-stage">
			{#if !revealed}
				<div class="pol-stage-front">
					<div class="flex flex-wrap justify-center gap-1.5">
						<span class="pol-chip pol-chip-primary">{card.sectionName}</span>
						<span class="pol-chip">第 {card.page} 页</span>
						{#if card.part}<span class="pol-chip">{card.part}</span>{/if}
						{#if card.kind === "meeting"}<span class="pol-chip pol-chip-warm">会议 / 著作</span>{/if}
						{#if card.kind === "figure"}<span class="pol-chip pol-chip-warm">时间轴</span>{/if}
						{#if card.kind === "mnemonic"}<span class="pol-chip pol-chip-warm">口诀</span>{/if}
					</div>
					<h3 class="pol-prompt mt-5">{card.prompt}</h3>
					<p class="pol-prompt-sub">
						{#if card.kind === "figure"}
							先自己在纸上或脑子里画出时间轴，再揭晓对照。
						{:else if card.kind === "mnemonic"}
							看每句开头两个字，把整句口诀补全；不用逐字背解释。
						{:else}
							先回忆关键词、对应关系和常考陷阱，再揭晓校对。
						{/if}
					</p>

					{#if hint}
						<div class="pol-stage-hint">
							<p class="mb-2 text-[0.66rem] font-extrabold uppercase tracking-[0.14em] text-30">首字提示</p>
							{#each hintLines as line, lineIndex (lineIndex)}
								<div class="pol-hint-line">
									<span class="pol-hint-index">{String(lineIndex + 1).padStart(2, "0")}</span>
									<span>{line}</span>
								</div>
							{/each}
						</div>
					{/if}

					<div class="mt-6 flex flex-wrap items-center justify-center gap-2">
						<button type="button" class="pol-button pol-button-primary" onclick={reveal}>
							<Icon icon="material-symbols:visibility-rounded" class="text-base" />
							显示答案
						</button>
						<button type="button" class="pol-button pol-button-ghost" onclick={() => (hint = !hint)}>
							<Icon icon="material-symbols:lightbulb-rounded" class="text-base" />
							{hint ? "收起提示" : "看首字提示"}
						</button>
					</div>
					<p class="mt-3 text-[0.64rem] text-30">Space / Enter 揭晓 · H 提示 · Esc 退出</p>
				</div>
			{:else}
				<div class="flex flex-wrap items-start justify-between gap-3">
					<div>
						<p class="text-[0.66rem] font-extrabold uppercase tracking-[0.16em] text-30">Answer · 按原书颜色还原</p>
						<h3 class="mt-1 text-xl font-black tracking-tight text-90 md:text-2xl">{card.prompt}</h3>
						<div class="mt-2 flex flex-wrap gap-1.5">
							<span class="pol-chip pol-chip-primary">{card.sectionName}</span>
							<span class="pol-chip">第 {card.page} 页</span>
							{#if card.part}<span class="pol-chip">{card.part}</span>{/if}
							{#if card.topic}<span class="pol-chip">{card.topic}</span>{/if}
						</div>
					</div>
					<button
						type="button"
						class={`pol-icon-button ${politicsStore.records[card.id]?.marked ? "pol-icon-button-active" : ""}`}
						onclick={() => politicsStore.toggleMark(card.id)}
						aria-label="收藏这张卡"
						title="收藏 / 错题标记"
					>
						<Icon icon={politicsStore.records[card.id]?.marked ? "material-symbols:star-rounded" : "material-symbols:star-outline-rounded"} class="text-base" />
					</button>
				</div>

				<div class="pol-answer">
					<div class="pol-answer-toolbar">
						<span class="pol-answer-title">完整答案</span>
						<div class="flex flex-wrap items-center gap-3">
							{#if card.keywords.length > 0}
								<label class="pol-toggle">
									<input type="checkbox" bind:checked={colorOnly} />
									只看彩色关键词
								</label>
							{/if}
							<span class="text-[0.64rem] text-30">{card.keywords.length} 个关键词</span>
						</div>
					</div>

					{#if card.kind === "figure" && card.figure}
						<figure class="overflow-hidden rounded-lg border border-(--line-divider) bg-white">
							<img
								src={figureUrl(card.figure)}
								alt={card.figureAlt}
								class="h-auto w-full"
								loading="lazy"
							/>
							<figcaption class="border-t border-(--line-divider) px-3 py-2 text-center text-[0.68rem] text-40">
								{card.figureCaption}
							</figcaption>
						</figure>
					{:else}
						<RichBlocks blocks={card.blocks} {colorOnly} />
					{/if}

					{#if card.keywords.length > 0 && !colorOnly}
						<div class="mt-3">
							<p class="mb-1.5 text-[0.62rem] font-extrabold uppercase tracking-[0.12em] text-30">这张卡的关键词</p>
							<div class="pol-keyword-list">
								{#each card.keywords as keyword (keyword)}
									<span class="pol-keyword">{keyword}</span>
								{/each}
							</div>
						</div>
					{/if}
				</div>

				<div class="pol-rating">
					<button type="button" class="pol-rate pol-rate-again" onclick={() => rate("again")}>
						<strong>忘记</strong>
						<span>今天再来</span>
					</button>
					<button type="button" class="pol-rate pol-rate-hard" onclick={() => rate("hard")}>
						<strong>模糊</strong>
						<span>{politicsStore.preview(card.id, "hard", maxInterval)} 天后</span>
					</button>
					<button type="button" class="pol-rate pol-rate-good" onclick={() => rate("good")}>
						<strong>记得</strong>
						<span>{politicsStore.preview(card.id, "good", maxInterval)} 天后</span>
					</button>
					<button type="button" class="pol-rate pol-rate-easy" onclick={() => rate("easy")}>
						<strong>熟练</strong>
						<span>{politicsStore.preview(card.id, "easy", maxInterval)} 天后</span>
					</button>
				</div>
				<p class="mt-2 text-center text-[0.62rem] text-30">按 1–4 评分 · Esc 退出 · 忘记的卡会回到今天</p>
			{/if}
		</section>
	{:else}
		<div class="pol-empty">这个队列里还没有卡片。</div>
	{/if}
</div>

<svelte:window onkeydown={handleKey} />
