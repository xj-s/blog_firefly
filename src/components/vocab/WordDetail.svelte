<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { highlight, posLabel } from "@/lib/vocab/format";
import type { WordDetail } from "@/lib/vocab/types";

interface Props {
	detail: WordDetail;
	inBook?: boolean;
	mastered?: boolean;
	onAdd?: () => void;
	onRemove?: () => void;
	onToggleMastered?: () => void;
	onOpenWord?: (word: string) => void;
	onToast?: (message: string) => void;
}

let {
	detail,
	inBook = false,
	mastered = false,
	onAdd,
	onRemove,
	onToggleMastered,
	onOpenWord,
	onToast,
}: Props = $props();

let speaking = $state(false);
let activeExample = $state(0);

const exam = $derived(detail.exam ?? []);
const examples = $derived(detail.ex ?? []);
const visibleExample = $derived(
	examples[Math.min(activeExample, Math.max(0, examples.length - 1))],
);

function speak(text: string, accent: "uk" | "us" = "uk") {
	if (typeof window === "undefined" || !window.speechSynthesis) {
		onToast?.("当前浏览器不支持语音朗读");
		return;
	}
	window.speechSynthesis.cancel();
	const utterance = new SpeechSynthesisUtterance(text);
	utterance.lang = accent === "us" ? "en-US" : "en-GB";
	utterance.rate = 0.88;
	const voices = window.speechSynthesis.getVoices();
	const exact = voices.find((voice) => voice.lang === utterance.lang);
	const english = voices.find((voice) => voice.lang.startsWith("en"));
	if (exact) {
		utterance.voice = exact;
	} else if (english) {
		utterance.voice = english;
	}
	utterance.onstart = () => {
		speaking = true;
	};
	utterance.onend = () => {
		speaking = false;
	};
	utterance.onerror = () => {
		speaking = false;
	};
	window.speechSynthesis.speak(utterance);
}

async function copyText(text: string) {
	try {
		await navigator.clipboard.writeText(text);
		onToast?.("已复制到剪贴板");
	} catch {
		onToast?.("复制失败，请手动选择文本");
	}
}

function toggleBook() {
	if (inBook) {
		onRemove?.();
	} else {
		onAdd?.();
	}
}
</script>

<article class="card-base relative overflow-hidden">
	<div
		class="pointer-events-none absolute inset-x-0 top-0 h-40 opacity-70"
		style="background: radial-gradient(80% 120% at 85% 0%, color-mix(in oklch, var(--primary) 16%, transparent), transparent 70%);"
	></div>

	<header class="relative px-5 pb-5 pt-6 md:px-7 md:pb-6">
		<div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
			<div class="min-w-0">
				<div class="flex flex-wrap items-end gap-x-3 gap-y-2">
					<h2 class="break-words text-4xl font-black leading-none tracking-tight text-90 md:text-5xl">
						{detail.w}
					</h2>
					<div class="flex items-center gap-1 pb-1">
						<button
							type="button"
							class="btn-plain h-9 w-9 rounded-full"
							title="英式发音"
							aria-label="英式发音"
							onclick={() => speak(detail.w, "uk")}
						>
							<Icon icon="material-symbols:volume-up-rounded" class="text-xl" />
						</button>
						{#if detail.us}
							<button
								type="button"
								class="btn-plain h-9 rounded-full px-2 text-xs font-bold"
								title="美式发音"
								aria-label="美式发音"
								onclick={() => speak(detail.w, "us")}
							>
								US
							</button>
						{/if}
					</div>
				</div>

				<div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-sm text-50">
					{#if detail.uk}<span>{detail.uk}</span>{/if}
					{#if detail.us}<span class="hidden sm:inline">美 {detail.us}</span>{/if}
					{#if speaking}
						<span class="inline-flex items-center gap-1 text-(--primary)">
							<Icon icon="svg-spinners:ring-resize" class="text-sm" /> 朗读中
						</span>
					{/if}
				</div>

				<div class="mt-3 flex flex-wrap items-center gap-2">
					{#if detail.syllabus}
						<span class="vocab-badge vocab-badge-primary">考研大纲 #{detail.rank}</span>
					{:else}
						<span class="vocab-badge">词书拓展</span>
					{/if}
					{#if detail.cefr}
						<span class="vocab-badge">CEFR {detail.cefr}</span>
					{/if}
					{#if detail.examCount > 0}
						<span class="vocab-badge vocab-badge-warm">
							<Icon icon="material-symbols:local-fire-department-rounded" class="text-sm" />
							真题 {detail.examCount} 次
						</span>
					{/if}
					{#if detail.academic}
						<span class="vocab-badge">学术词汇</span>
					{/if}
					{#if detail.star > 0}
						<span class="vocab-badge">柯林斯 {detail.star}★</span>
					{/if}
					{#if detail.cat}
						<span class="hidden text-xs text-30 md:inline">{detail.cat}</span>
					{/if}
				</div>
			</div>

			<div class="flex flex-wrap items-center gap-2">
				<button
					type="button"
					class={`vocab-action ${inBook ? "vocab-action-soft" : "vocab-action-primary"}`}
					onclick={toggleBook}
				>
					{#if inBook}
						<Icon icon="material-symbols:bookmark-added-rounded" class="text-lg" />
						已在生词本
					{:else}
						<Icon icon="material-symbols:bookmark-add-rounded" class="text-lg" />
						加入生词本
					{/if}
				</button>
				{#if inBook}
					<button
						type="button"
						class={`vocab-action ${mastered ? "vocab-action-soft" : "vocab-action-ghost"}`}
						onclick={() => onToggleMastered?.()}
					>
						<Icon icon="material-symbols:check-circle-rounded" class="text-lg" />
						{mastered ? "已掌握" : "标记掌握"}
					</button>
				{/if}
			</div>
		</div>
	</header>

	<div class="relative grid border-t border-(--line-divider) lg:grid-cols-[1.05fr_0.95fr]">
		<div class="space-y-6 px-5 py-6 md:px-7">
			<section>
				<div class="vocab-section-title">
					<Icon icon="material-symbols:translate-rounded" class="text-lg" />
					释义与用法
				</div>
				<div class="mt-3 space-y-3">
					{#each detail.trans as item}
						<div class="rounded-xl border border-(--line-divider) bg-(--btn-plain-bg-hover) p-3.5">
							<div class="flex flex-wrap items-baseline gap-2">
								{#if item.pos}
									<span class="rounded-md bg-(--btn-regular-bg) px-1.5 py-0.5 font-mono text-[0.7rem] font-bold text-(--btn-content)">
										{posLabel(item.pos)}
									</span>
								{/if}
								<span class="text-[0.98rem] font-semibold leading-relaxed text-90">{item.cn}</span>
							</div>
							{#if item.en}
								<p class="mt-1.5 text-sm leading-relaxed text-50">{item.en}</p>
							{/if}
						</div>
					{/each}
				</div>
			</section>

			{#if detail.note}
				<section class="vocab-callout vocab-callout-note">
					<div class="flex items-center gap-2 text-sm font-bold text-(--primary)">
						<Icon icon="material-symbols:lightbulb-rounded" class="text-lg" />
						考点提示
					</div>
					<p class="mt-1.5 text-sm leading-relaxed text-75">{detail.note}</p>
				</section>
			{/if}

			{#if detail.mem}
				<section class="vocab-callout">
					<div class="flex items-center gap-2 text-sm font-bold text-75">
						<Icon icon="material-symbols:auto-awesome-rounded" class="text-lg text-(--primary)" />
						记忆法
					</div>
					<p class="mt-1.5 text-sm leading-relaxed text-75">{detail.mem}</p>
				</section>
			{/if}

			{#if detail.phr?.length}
				<section>
					<div class="vocab-section-title">
						<Icon icon="material-symbols:link-rounded" class="text-lg" />
						常见搭配
					</div>
					<div class="mt-3 grid gap-2 sm:grid-cols-2">
						{#each detail.phr as phrase}
							<div class="rounded-lg border border-(--line-divider) px-3 py-2">
								<div class="font-mono text-sm font-semibold text-90">{phrase.en}</div>
								<div class="mt-0.5 text-xs leading-relaxed text-50">{phrase.cn}</div>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			{#if detail.syn?.length}
				<section>
					<div class="vocab-section-title">
						<Icon icon="material-symbols:swap-horiz-rounded" class="text-lg" />
						同义替换
					</div>
					<div class="mt-3 space-y-2.5">
						{#each detail.syn as group}
							<div class="flex flex-wrap items-center gap-2">
								{#if group.pos}
									<span class="font-mono text-xs font-bold text-30">{posLabel(group.pos)}</span>
								{/if}
								{#each group.words as word}
									<button type="button" class="vocab-chip" onclick={() => onOpenWord?.(word)}>
										{word}
									</button>
								{/each}
								{#if group.cn}
									<span class="w-full break-words text-xs text-30 sm:w-auto">{group.cn}</span>
								{/if}
							</div>
						{/each}
					</div>
				</section>
			{/if}

			{#if detail.fam?.length}
				<section>
					<div class="vocab-section-title">
						<Icon icon="material-symbols:account-tree-rounded" class="text-lg" />
						词族
					</div>
					<div class="mt-3 space-y-2">
						{#each detail.fam as group}
							<div class="flex flex-wrap items-center gap-2">
								<span class="w-10 shrink-0 font-mono text-xs font-bold text-30">{posLabel(group.pos)}</span>
								{#each group.words as item}
									<button
										type="button"
										class="vocab-chip"
										title={item.cn}
										onclick={() => onOpenWord?.(item.w)}
									>
										{item.w}
									</button>
								{/each}
							</div>
						{/each}
					</div>
				</section>
			{/if}

			{#if detail.infl?.length}
				<section>
					<div class="vocab-section-title">
						<Icon icon="material-symbols:sync-alt-rounded" class="text-lg" />
						词形变化
					</div>
					<div class="mt-3 flex flex-wrap gap-2">
						{#each detail.infl as form}
							<span class="vocab-chip vocab-chip-muted">{form}</span>
						{/each}
					</div>
				</section>
			{/if}
		</div>

		<aside class="border-t border-(--line-divider) bg-(--btn-plain-bg-hover) px-5 py-6 md:px-7 lg:border-l lg:border-t-0">
			<section>
				<div class="flex items-center justify-between gap-2">
					<div class="vocab-section-title">
						<Icon icon="material-symbols:history-edu-rounded" class="text-lg" />
						真题例句
					</div>
					<span class="text-xs text-30">2010–2026</span>
				</div>

				{#if exam.length}
					<div class="mt-3 space-y-3">
						{#each exam as sentence, index}
							<div class="exam-card">
								<div class="flex flex-wrap items-center justify-between gap-2">
									<span class="exam-year">{sentence.y}</span>
									<span class="text-[0.7rem] font-medium text-50">
										{sentence.p === 2 ? "英语二" : "英语一"} · {sentence.sec}{sentence.src ? ` · ${sentence.src}` : ""}
									</span>
									<button
										type="button"
										class="btn-plain ml-auto h-7 w-7 rounded-md"
										title="复制例句"
										aria-label="复制例句"
										onclick={() => copyText(sentence.text)}
									>
										<Icon icon="material-symbols:content-copy-rounded" class="text-sm" />
									</button>
								</div>
								<p class="mt-2 text-[0.92rem] leading-relaxed text-75">
									{@html highlight(sentence.text, sentence.hit)}
								</p>
								{#if sentence.zh}
									<p class="mt-1 text-xs leading-relaxed text-30">{sentence.zh}</p>
								{/if}
								{#if index === 0 && exam.length > 1}
									<div class="mt-2 text-[0.68rem] text-30">
										共 {detail.examCount} 句语料命中，按阅读/翻译与年份优先展示
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{:else if detail.legacy}
					<div class="mt-3">
						<div class="exam-card">
							<div class="flex flex-wrap items-center gap-2">
								<span class="exam-year">{detail.legacy.y ?? "真题"}</span>
								<span class="text-[0.7rem] text-50">{detail.legacy.src}</span>
							</div>
							<p class="mt-2 text-[0.92rem] leading-relaxed text-75">{detail.legacy.text}</p>
							{#if detail.legacy.zh}
								<p class="mt-1 text-xs leading-relaxed text-30">{detail.legacy.zh}</p>
							{/if}
						</div>
						<p class="mt-2 text-xs text-30">
							2010–2026 语料中未匹配到完整句子，以上为词书收录的早年真题例句。
						</p>
					</div>
				{:else}
					<div class="mt-3 rounded-xl border border-dashed border-(--line-divider) px-4 py-5 text-center">
						<Icon icon="material-symbols:search-off-rounded" class="text-2xl text-30" />
						<p class="mt-1 text-sm text-50">2010–2026 真题语料中暂未匹配到完整句子</p>
						<p class="mt-1 text-xs text-30">可先看词典例句，或在阅读中留意该词。</p>
					</div>
				{/if}
			</section>

			{#if examples.length}
				<section class="mt-6 border-t border-(--line-divider) pt-5">
					<div class="flex items-center justify-between">
						<div class="vocab-section-title">
							<Icon icon="material-symbols:menu-book-rounded" class="text-lg" />
							词典例句
						</div>
						{#if examples.length > 1}
							<div class="flex items-center gap-1">
								{#each examples as _, index}
									<button
										type="button"
										class={`h-1.5 rounded-full transition-all ${index === activeExample ? "w-4 bg-(--primary)" : "w-1.5 bg-(--line-color)"}`}
										aria-label={`第 ${index + 1} 条例句`}
										onclick={() => (activeExample = index)}
									></button>
								{/each}
							</div>
						{/if}
					</div>
					{#if visibleExample}
						<div class="mt-3 rounded-xl bg-(--card-bg) p-3.5 shadow-xs">
							<p class="text-sm leading-relaxed text-75">{visibleExample.en}</p>
							{#if visibleExample.zh}
								<p class="mt-1 text-xs leading-relaxed text-50">{visibleExample.zh}</p>
							{/if}
							{#if visibleExample.src}
								<span class="mt-2 inline-block text-[0.65rem] text-30">来源：{visibleExample.src}</span>
							{/if}
						</div>
					{/if}
				</section>
			{/if}

			{#if detail.confuse?.length}
				<section class="mt-6 border-t border-(--line-divider) pt-5">
					<div class="vocab-section-title">
						<Icon icon="material-symbols:compare-arrows-rounded" class="text-lg" />
						易混词
					</div>
					<div class="mt-3 flex flex-wrap gap-2">
						{#each detail.confuse as word}
							<button type="button" class="vocab-chip" onclick={() => onOpenWord?.(word)}>
								{word}
							</button>
						{/each}
					</div>
				</section>
			{/if}

			<p class="mt-6 rounded-lg bg-(--card-bg) px-3 py-2 text-[0.68rem] leading-relaxed text-50">
				加入生词本后，可以在“生词本”里为它写个人笔记。建议只记一个触发点：真题搭配、易混词，或你反复忘的那层意思。
			</p>
		</aside>
	</div>
</article>

<style>
	.vocab-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		border: 1px solid var(--line-divider);
		border-radius: 0.4rem;
		padding: 0.15rem 0.5rem;
		font-size: 0.7rem;
		font-weight: 600;
		color: color-mix(in oklch, var(--deep-text) 62%, transparent);
		background: color-mix(in oklch, var(--card-bg) 70%, transparent);
	}
	.vocab-badge-primary {
		border-color: color-mix(in oklch, var(--primary) 30%, transparent);
		color: var(--btn-content);
		background: var(--btn-regular-bg);
	}
	.vocab-badge-warm {
		border-color: color-mix(in oklch, oklch(0.7 0.16 55) 30%, transparent);
		color: oklch(0.55 0.14 55);
		background: color-mix(in oklch, oklch(0.9 0.08 75) 45%, transparent);
	}
	:global(.dark) .vocab-badge-warm {
		color: oklch(0.82 0.12 70);
		background: color-mix(in oklch, oklch(0.4 0.08 60) 40%, transparent);
	}

	.vocab-action {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.35rem;
		border-radius: 0.65rem;
		padding: 0.55rem 0.9rem;
		font-size: 0.82rem;
		font-weight: 700;
		transition: all 150ms ease;
		border: 1px solid transparent;
	}
	.vocab-action:active {
		transform: scale(0.97);
	}
	.vocab-action-primary {
		background: var(--primary);
		color: oklch(0.22 0.02 var(--hue));
		box-shadow: 0 6px 18px color-mix(in oklch, var(--primary) 25%, transparent);
	}
	.vocab-action-primary:hover {
		filter: brightness(1.05);
	}
	.vocab-action-soft {
		background: var(--btn-regular-bg);
		color: var(--btn-content);
		border-color: color-mix(in oklch, var(--primary) 20%, transparent);
	}
	.vocab-action-ghost {
		background: transparent;
		color: color-mix(in oklch, var(--deep-text) 62%, transparent);
		border-color: var(--line-divider);
	}
	.vocab-action-ghost:hover {
		background: var(--btn-plain-bg-hover);
	}

	.vocab-section-title {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.78rem;
		font-weight: 800;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: color-mix(in oklch, var(--deep-text) 55%, transparent);
	}
	.vocab-section-title :global(.inline-icon) {
		color: var(--primary);
	}

	.vocab-callout {
		border: 1px solid var(--line-divider);
		border-radius: 0.8rem;
		padding: 0.8rem 0.9rem;
		background: color-mix(in oklch, var(--card-bg) 82%, var(--primary) 4%);
	}
	.vocab-callout-note {
		border-color: color-mix(in oklch, var(--primary) 26%, transparent);
		background: color-mix(in oklch, var(--btn-regular-bg) 55%, transparent);
	}

	.vocab-chip {
		display: inline-flex;
		align-items: center;
		border-radius: 0.4rem;
		border: 1px solid var(--line-divider);
		background: var(--card-bg);
		padding: 0.2rem 0.5rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.76rem;
		color: color-mix(in oklch, var(--deep-text) 80%, transparent);
		transition: all 120ms ease;
	}
	.vocab-chip:hover {
		border-color: color-mix(in oklch, var(--primary) 45%, transparent);
		color: var(--btn-content);
		background: var(--btn-plain-bg-hover);
	}
	.vocab-chip-muted {
		color: color-mix(in oklch, var(--deep-text) 55%, transparent);
	}

	.exam-card {
		border: 1px solid var(--line-divider);
		border-radius: 0.8rem;
		background: var(--card-bg);
		padding: 0.8rem 0.9rem;
		box-shadow: 0 1px 2px rgb(0 0 0 / 0.03);
	}
	.exam-year {
		display: inline-flex;
		align-items: center;
		border-radius: 0.35rem;
		background: var(--primary);
		color: oklch(0.22 0.02 var(--hue));
		padding: 0.1rem 0.4rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.68rem;
		font-weight: 800;
	}

	:global(.vocab-mark) {
		background: color-mix(in oklch, var(--primary) 26%, transparent);
		color: inherit;
		border-radius: 0.15rem;
		padding: 0 0.08em;
		font-weight: 700;
	}
</style>
