<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { dailyWord, searchIndex, suggestWords } from "@/lib/vocab/data";
import type { IndexRow, WordDetail } from "@/lib/vocab/types";
import WordDetailCard from "./WordDetail.svelte";

interface Props {
	index: IndexRow[];
	active: WordDetail | null;
	query: string;
	loading: boolean;
	notFound: boolean;
	inBook: boolean;
	mastered: boolean;
	onQueryChange: (value: string) => void;
	onOpen: (word: string) => void;
	onRandom: () => void;
	onAdd: () => void;
	onRemove: () => void;
	onToggleMastered: () => void;
	onToast: (message: string) => void;
}

let {
	index,
	active,
	query,
	loading,
	notFound,
	inBook,
	mastered,
	onQueryChange,
	onOpen,
	onRandom,
	onAdd,
	onRemove,
	onToggleMastered,
	onToast,
}: Props = $props();

const HOT_WORDS = [
	"abandon",
	"address",
	"subject",
	"available",
	"sustain",
	"yield",
	"undermine",
	"credibility",
];

let focused = $state(false);
let cursor = $state(0);

const suggestions = $derived(searchIndex(index, query, 8));
const hotWords = $derived(
	HOT_WORDS.map((word) => index.find((row) => row[0] === word)).filter(
		(row): row is IndexRow => Boolean(row),
	),
);
const daily = $derived(dailyWord(index));
const fallbackSuggestions = $derived(
	notFound ? suggestWords(index, query, 6) : [],
);
const showSuggestions = $derived(
	focused && query.trim().length > 0 && suggestions.length > 0,
);

function updateQuery(value: string) {
	onQueryChange(value);
	cursor = 0;
}

function pick(word: string) {
	onQueryChange(word);
	focused = false;
	onOpen(word);
}

function submit() {
	if (suggestions[cursor]) {
		pick(suggestions[cursor][0]);
		return;
	}
	if (suggestions[0]) {
		pick(suggestions[0][0]);
		return;
	}
	if (query.trim()) {
		onOpen(query.trim());
	}
}

function handleKeydown(event: KeyboardEvent) {
	if (event.key === "ArrowDown") {
		event.preventDefault();
		cursor = Math.min(suggestions.length - 1, cursor + 1);
	} else if (event.key === "ArrowUp") {
		event.preventDefault();
		cursor = Math.max(0, cursor - 1);
	} else if (event.key === "Enter") {
		event.preventDefault();
		submit();
	} else if (event.key === "Escape") {
		focused = false;
	}
}

const externalLinks = $derived([
	{
		label: "剑桥词典",
		href: `https://dictionary.cambridge.org/dictionary/english-chinese-simplified/${encodeURIComponent(query.trim())}`,
	},
	{
		label: "有道词典",
		href: `https://dict.youdao.com/result?word=${encodeURIComponent(query.trim())}&lang=en`,
	},
]);
</script>

<div class="space-y-4">
	<section class="card-base relative overflow-visible p-4 md:p-6">
		<div class="flex flex-wrap items-center justify-between gap-2">
			<div class="flex items-center gap-2">
				<span class="flex h-8 w-8 items-center justify-center rounded-lg bg-(--btn-regular-bg) text-(--btn-content)">
					<Icon icon="material-symbols:search" class="text-xl" />
				</span>
				<div>
					<div class="text-sm font-black tracking-wide text-90">查一个词</div>
					<div class="text-[0.68rem] text-30">支持英文单词、词形变化与中文释义</div>
				</div>
			</div>
			<div class="hidden items-center gap-2 text-[0.65rem] text-30 sm:flex">
				<kbd class="vocab-kbd">↑</kbd><kbd class="vocab-kbd">↓</kbd> 选择
				<kbd class="vocab-kbd">Enter</kbd> 打开
			</div>
		</div>

		<div class="relative mt-4">
			<div class="relative">
				<span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-30">
					<Icon icon="material-symbols:search" class="text-xl" />
				</span>
				<input
					type="text"
					class="vocab-search-input"
					placeholder="输入单词，如 abandon / address / 处理"
					autocomplete="off"
					autocapitalize="off"
					spellcheck="false"
					aria-label="搜索考研单词"
					value={query}
					oninput={(event) => updateQuery(event.currentTarget.value)}
					onfocus={() => (focused = true)}
					onblur={() => {
						window.setTimeout(() => (focused = false), 120);
					}}
					onkeydown={handleKeydown}
				/>
				{#if query}
					<button
						type="button"
						class="absolute inset-y-0 right-14 flex w-9 items-center justify-center text-30 transition-colors hover:text-(--primary)"
						aria-label="清空"
						onclick={() => {
							updateQuery("");
							focused = true;
						}}
					>
						<Icon icon="material-symbols:close-rounded" class="text-lg" />
					</button>
				{/if}
				<button type="button" class="vocab-search-submit" aria-label="查询" onclick={submit}>
					<Icon icon="material-symbols:arrow-forward-rounded" class="text-xl" />
				</button>
			</div>

			{#if showSuggestions}
				<div class="vocab-suggest-panel" role="listbox">
					{#each suggestions as row, index}
						<button
							type="button"
							class={`vocab-suggest-item ${index === cursor ? "vocab-suggest-item-active" : ""}`}
							role="option"
							aria-selected={index === cursor}
							onmousedown={(event) => event.preventDefault()}
							onclick={() => pick(row[0])}
							onmouseenter={() => (cursor = index)}
						>
							<span class="flex min-w-0 items-baseline gap-2">
								<span class="font-mono text-sm font-bold text-90">{row[0]}</span>
								{#if row[1]}<span class="truncate font-mono text-[0.68rem] text-30">{row[1]}</span>{/if}
							</span>
							<span class="ml-3 hidden truncate text-xs text-50 sm:block">{row[2]}</span>
							{#if row[5] > 0}
								<span class="ml-2 shrink-0 rounded bg-(--btn-regular-bg) px-1 py-0.5 text-[0.6rem] font-bold text-(--btn-content)">
									{row[5]}
								</span>
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<div class="mt-3 flex flex-wrap items-center gap-1.5">
			<span class="mr-1 text-[0.68rem] font-semibold text-30">试试</span>
			{#each hotWords as row}
				<button type="button" class="vocab-hot-chip" onclick={() => pick(row[0])}>
					{row[0]}
				</button>
			{/each}
		</div>
	</section>

	{#if loading}
		<div class="card-base p-6">
			<div class="flex animate-pulse flex-col gap-4">
				<div class="h-10 w-52 rounded-lg bg-(--btn-regular-bg)"></div>
				<div class="h-4 w-72 rounded bg-(--btn-regular-bg)"></div>
				<div class="grid gap-3 md:grid-cols-2">
					<div class="h-28 rounded-xl bg-(--btn-regular-bg)"></div>
					<div class="h-28 rounded-xl bg-(--btn-regular-bg)"></div>
				</div>
			</div>
		</div>
	{:else if active}
		<WordDetailCard
			detail={active}
			{inBook}
			{mastered}
			{onAdd}
			{onRemove}
			{onToggleMastered}
			onOpenWord={onOpen}
			{onToast}
		/>
	{:else if notFound}
		<div class="card-base p-6 md:p-8">
			<div class="flex items-start gap-3">
				<span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-(--btn-regular-bg) text-(--btn-content)">
					<Icon icon="material-symbols:search-off-rounded" class="text-2xl" />
				</span>
				<div>
					<h3 class="text-lg font-bold text-90">本地词库暂未收录 “{query}”</h3>
					<p class="mt-1 text-sm leading-relaxed text-50">
						当前词库以考研大纲 5530 词和常见词书拓展词为主。可以先看看下面的近似词，或用外部词典补充。
					</p>
				</div>
			</div>

			{#if fallbackSuggestions.length}
				<div class="mt-4">
					<div class="text-xs font-bold text-30">你是不是想查</div>
					<div class="mt-2 flex flex-wrap gap-2">
						{#each fallbackSuggestions as row}
							<button type="button" class="vocab-chip" onclick={() => pick(row[0])}>
								{row[0]} <span class="ml-1 text-30">{row[2]}</span>
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<div class="mt-5 flex flex-wrap gap-2">
				{#each externalLinks as link}
					<a
						href={link.href}
						target="_blank"
						rel="noopener noreferrer"
						class="vocab-action vocab-action-ghost"
					>
						<Icon icon="material-symbols:open-in-new-rounded" class="text-base" />
						{link.label}
					</a>
				{/each}
			</div>
		</div>
	{:else}
		<div class="grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
			{#if daily}
				<section class="card-base relative overflow-hidden p-6 md:p-7">
					<div
						class="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full opacity-40"
						style="background: radial-gradient(circle, color-mix(in oklch, var(--primary) 30%, transparent), transparent 70%);"
					></div>
					<div class="relative">
						<div class="flex items-center gap-2 text-[0.68rem] font-bold uppercase tracking-[0.18em] text-(--primary)">
							<Icon icon="material-symbols:auto-awesome-rounded" class="text-base" />
							今日一词
						</div>
						<div class="mt-3 flex flex-wrap items-baseline gap-2">
							<h3 class="text-4xl font-black tracking-tight text-90 md:text-5xl">{daily[0]}</h3>
							{#if daily[1]}<span class="font-mono text-sm text-50">{daily[1]}</span>{/if}
						</div>
						<p class="mt-2 text-base leading-relaxed text-75">{daily[2]}</p>
						<div class="mt-4 flex flex-wrap items-center gap-2">
							<button type="button" class="vocab-action vocab-action-primary" onclick={() => pick(daily[0])}>
								<Icon icon="material-symbols:menu-book-rounded" class="text-lg" />
								查看详解
							</button>
							<button type="button" class="vocab-action vocab-action-ghost" onclick={onRandom}>
								<Icon icon="material-symbols:casino" class="text-lg" />
								随机一个
							</button>
						</div>
						<div class="mt-4 flex flex-wrap gap-2 text-[0.68rem] text-30">
							{#if daily[6] === 1}<span>考研大纲 #{daily[4]}</span>{/if}
							{#if daily[7]}<span>CEFR {daily[7]}</span>{/if}
							{#if daily[5] > 0}<span>真题出现 {daily[5]} 次</span>{/if}
						</div>
					</div>
				</section>
			{/if}

			<section class="card-base p-5">
				<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-30">
					<Icon icon="material-symbols:info-outline-rounded" class="text-base text-(--primary)" />
					怎么用
				</div>
				<ol class="mt-3 space-y-3 text-sm text-75">
					<li class="flex gap-2">
						<span class="vocab-step">1</span>
						<span>输入单词，先看 <b class="text-90">考纲释义</b> 和 <b class="text-90">考点提示</b>。</span>
					</li>
					<li class="flex gap-2">
						<span class="vocab-step">2</span>
						<span>读右侧 <b class="text-90">2010–2026 真题原句</b>，把词放回语境。</span>
					</li>
					<li class="flex gap-2">
						<span class="vocab-step">3</span>
						<span>加入生词本，之后按 <b class="text-90">1/2/4/7/15/30/60 天</b> 复习。</span>
					</li>
				</ol>
				<div class="mt-4 rounded-lg bg-(--btn-plain-bg-hover) px-3 py-2 text-[0.68rem] leading-relaxed text-50">
					生词本保存在本机浏览器。换设备前记得在“生词本”里导出备份。
				</div>
			</section>
		</div>
	{/if}
</div>

<style>
	.vocab-search-input {
		width: 100%;
		border: 1px solid var(--line-divider);
		border-radius: 0.8rem;
		background: color-mix(in oklch, var(--card-bg) 88%, var(--primary) 2%);
		padding: 0.95rem 6.5rem 0.95rem 3rem;
		font-size: 1rem;
		font-weight: 500;
		color: var(--deep-text);
		outline: none;
		transition: border-color 150ms ease, box-shadow 150ms ease;
	}
	.vocab-search-input::placeholder {
		color: color-mix(in oklch, var(--deep-text) 35%, transparent);
	}
	.vocab-search-input:focus {
		border-color: color-mix(in oklch, var(--primary) 55%, transparent);
		box-shadow: 0 0 0 4px color-mix(in oklch, var(--primary) 10%, transparent);
	}
	.vocab-search-submit {
		position: absolute;
		top: 50%;
		right: 0.4rem;
		transform: translateY(-50%);
		display: flex;
		height: 2.5rem;
		width: 2.6rem;
		align-items: center;
		justify-content: center;
		border-radius: 0.6rem;
		background: var(--primary);
		color: oklch(0.22 0.02 var(--hue));
		transition: filter 150ms ease, transform 150ms ease;
	}
	.vocab-search-submit:hover {
		filter: brightness(1.06);
	}
	.vocab-search-submit:active {
		transform: translateY(-50%) scale(0.96);
	}
	.vocab-suggest-panel {
		position: absolute;
		z-index: 40;
		left: 0;
		right: 0;
		top: calc(100% + 0.4rem);
		overflow: hidden;
		border: 1px solid var(--line-divider);
		border-radius: 0.75rem;
		background: var(--card-bg);
		box-shadow: 0 18px 45px rgb(0 0 0 / 0.14);
	}
	.vocab-suggest-item {
		display: flex;
		width: 100%;
		align-items: center;
		padding: 0.6rem 0.8rem;
		text-align: left;
		transition: background 100ms ease;
	}
	.vocab-suggest-item + .vocab-suggest-item {
		border-top: 1px solid var(--line-divider);
	}
	.vocab-suggest-item:hover,
	.vocab-suggest-item-active {
		background: var(--btn-plain-bg-hover);
	}
	.vocab-hot-chip {
		border-radius: 0.35rem;
		background: var(--btn-plain-bg-hover);
		padding: 0.18rem 0.45rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.7rem;
		color: color-mix(in oklch, var(--deep-text) 65%, transparent);
		transition: all 120ms ease;
	}
	.vocab-hot-chip:hover {
		background: var(--btn-regular-bg);
		color: var(--btn-content);
	}
	.vocab-kbd {
		display: inline-flex;
		min-width: 1.1rem;
		justify-content: center;
		border: 1px solid var(--line-divider);
		border-radius: 0.25rem;
		padding: 0.05rem 0.25rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.6rem;
		color: color-mix(in oklch, var(--deep-text) 55%, transparent);
	}
	.vocab-step {
		display: inline-flex;
		height: 1.25rem;
		width: 1.25rem;
		flex-shrink: 0;
		align-items: center;
		justify-content: center;
		border-radius: 999px;
		background: var(--btn-regular-bg);
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.62rem;
		font-weight: 800;
		color: var(--btn-content);
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
	.vocab-action-primary {
		background: var(--primary);
		color: oklch(0.22 0.02 var(--hue));
	}
	.vocab-action-ghost {
		background: transparent;
		color: color-mix(in oklch, var(--deep-text) 62%, transparent);
		border-color: var(--line-divider);
	}
	.vocab-action-ghost:hover {
		background: var(--btn-plain-bg-hover);
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
	}
	.vocab-chip:hover {
		border-color: color-mix(in oklch, var(--primary) 45%, transparent);
		color: var(--btn-content);
		background: var(--btn-plain-bg-hover);
	}
</style>
