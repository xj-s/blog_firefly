<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { loadIndex, loadMeta, loadWord } from "@/lib/vocab/data";
import { vocabStore } from "@/lib/vocab/store.svelte";
import type { IndexRow, VocabMeta, WordDetail } from "@/lib/vocab/types";
import { onMount } from "svelte";
import LookupPanel from "./LookupPanel.svelte";
import ReviewPanel from "./ReviewPanel.svelte";
import WordbookPanel from "./WordbookPanel.svelte";

type Tab = "lookup" | "book" | "review";

let tab = $state<Tab>("lookup");
let index = $state<IndexRow[]>([]);
let meta = $state<VocabMeta | null>(null);
let loadingIndex = $state(true);
let loadError = $state("");
let query = $state("");
let active = $state<WordDetail | null>(null);
let loadingWord = $state(false);
let notFound = $state(false);
let toast = $state("");
let reviewNonce = $state(0);
let toastTimer: ReturnType<typeof setTimeout> | undefined;

const tabs: { key: Tab; label: string; icon: string; count?: number }[] = [
	{ key: "lookup", label: "查词", icon: "material-symbols:search" },
	{ key: "book", label: "生词本", icon: "material-symbols:bookmarks-rounded" },
	{ key: "review", label: "复习", icon: "material-symbols:refresh-rounded" },
];

function showToast(message: string) {
	toast = message;
	if (toastTimer) {
		clearTimeout(toastTimer);
	}
	toastTimer = setTimeout(() => {
		toast = "";
	}, 2200);
}

async function openWord(input: string, updateUrl = true) {
	const word = input.trim();
	if (!word) {
		return;
	}
	tab = "lookup";
	query = word;
	active = null;
	notFound = false;
	loadingWord = true;
	try {
		const detail = await loadWord(word);
		active = detail;
		notFound = !detail;
		if (detail && updateUrl && typeof window !== "undefined") {
			const url = new URL(window.location.href);
			url.searchParams.set("w", detail.w);
			window.history.replaceState({}, "", url);
		}
		if (!detail) {
			notFound = true;
		}
	} catch {
		notFound = true;
		showToast("词库加载失败，请稍后重试");
	} finally {
		loadingWord = false;
	}
}

function randomWord() {
	const pool = index.filter((row) => row[6] === 1 && row[4] <= 3000);
	if (!pool.length) {
		return;
	}
	const candidates = pool.filter((row) => row[0] !== active?.w);
	const pick = candidates[Math.floor(Math.random() * candidates.length)] ?? pool[0];
	openWord(pick[0]);
}

function addCurrent() {
	if (!active) {
		return;
	}
	const result = vocabStore.add(active.w);
	showToast(result === "added" ? `已加入生词本：${active.w}` : "这个词已经在生词本里了");
}

function removeCurrent() {
	if (!active) {
		return;
	}
	vocabStore.remove(active.w);
	showToast(`已移出生词本：${active.w}`);
}

function toggleMastered() {
	if (!active) {
		return;
	}
	const mastered = vocabStore.toggleMastered(active.w);
	showToast(mastered ? "已标记为掌握" : "已取消掌握标记");
}

function startReview() {
	tab = "review";
	reviewNonce += 1;
}

function goLookup() {
	tab = "lookup";
}

onMount(() => {
	vocabStore.load();
	Promise.all([loadIndex(), loadMeta()])
		.then(([rows, info]) => {
			index = rows;
			meta = info;
			loadingIndex = false;
			const params = new URLSearchParams(window.location.search);
			const initial = params.get("w");
			if (initial) {
				void openWord(initial, false);
			}
		})
		.catch((error) => {
			console.error("vocab data load failed", error);
			loadError = "词库加载失败，请刷新页面或检查网络。";
			loadingIndex = false;
		});
});
</script>

<div class="space-y-4" data-pagefind-ignore data-vocab-page>
	<section class="card-base relative overflow-hidden p-5 md:p-7">
		<div
			class="pointer-events-none absolute inset-0"
			style="background:
				radial-gradient(70% 120% at 100% 0%, color-mix(in oklch, var(--primary) 16%, transparent), transparent 62%),
				linear-gradient(120deg, color-mix(in oklch, var(--primary) 5%, transparent), transparent 45%);"
		></div>
		<div class="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
			<div class="min-w-0">
				<div class="flex items-center gap-2 text-[0.68rem] font-bold uppercase tracking-[0.2em] text-(--primary)">
					<span class="flex h-7 w-7 items-center justify-center rounded-lg bg-(--btn-regular-bg)">
						<Icon icon="material-symbols:school-rounded" class="text-base" />
					</span>
					Kaoyan Vocabulary Lab
				</div>
				<h2 class="mt-3 text-3xl font-black tracking-tight text-90 md:text-4xl">
					把单词放回真题里记
				</h2>
				<p class="mt-2 max-w-2xl text-sm leading-relaxed text-50 md:text-[0.95rem]">
					输入单词看考纲释义、熟词僻义和 2010–2026 真题原句；一键收进生词本，按 1/2/4/7/15/30/60 天复习。
				</p>
			</div>

			<div class="grid shrink-0 grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
				<div class="vocab-hero-stat">
					<span class="vocab-hero-stat-value">{meta?.wordCount ?? "—"}</span>
					<span class="vocab-hero-stat-label">词库</span>
				</div>
				<div class="vocab-hero-stat">
					<span class="vocab-hero-stat-value">{vocabStore.total}</span>
					<span class="vocab-hero-stat-label">生词本</span>
				</div>
				<div class="vocab-hero-stat">
					<span class="vocab-hero-stat-value">{vocabStore.dueCount}</span>
					<span class="vocab-hero-stat-label">待复习</span>
				</div>
				<div class="vocab-hero-stat">
					<span class="vocab-hero-stat-value">{vocabStore.streak}</span>
					<span class="vocab-hero-stat-label">连续天数</span>
				</div>
			</div>
		</div>
	</section>

	<div class="flex flex-wrap items-center justify-between gap-2">
		<div class="vocab-tabs" role="tablist" aria-label="单词模块导航">
			{#each tabs as item (item.key)}
				<button
					type="button"
					role="tab"
					aria-selected={tab === item.key}
					class={`vocab-tab ${tab === item.key ? "vocab-tab-active" : ""}`}
					onclick={() => (tab = item.key)}
				>
					<Icon icon={item.icon} class="text-lg" />
					{item.label}
					{#if item.key === "book" && vocabStore.total > 0}
						<span class="vocab-tab-count">{vocabStore.total}</span>
					{:else if item.key === "review" && vocabStore.dueCount > 0}
						<span class="vocab-tab-count vocab-tab-count-warm">{vocabStore.dueCount}</span>
					{/if}
				</button>
			{/each}
		</div>
		<div class="hidden items-center gap-1.5 text-[0.65rem] text-30 sm:flex">
			<Icon icon="material-symbols:info-outline-rounded" class="text-sm" />
			本地优先 · 无需登录
		</div>
	</div>

	{#if loadingIndex}
		<div class="card-base flex flex-col items-center justify-center px-6 py-16 text-center">
			<Icon icon="svg-spinners:ring-resize" class="text-3xl text-(--primary)" />
			<p class="mt-3 text-sm text-50">正在加载词库与真题语料…</p>
			<p class="mt-1 text-xs text-30">首次加载约 500 KB，之后会走浏览器缓存</p>
		</div>
	{:else if loadError}
		<div class="card-base px-6 py-14 text-center">
			<Icon icon="material-symbols:error-outline-rounded" class="text-3xl text-red-500" />
			<p class="mt-2 text-sm text-50">{loadError}</p>
			<button type="button" class="vocab-action vocab-action-primary mx-auto mt-4" onclick={() => location.reload()}>
				重新加载
			</button>
		</div>
	{:else}
		<div id="vocab-result" class:hidden={tab !== "lookup"}>
			<LookupPanel
				{index}
				{active}
				{query}
				loading={loadingWord}
				{notFound}
				inBook={active ? vocabStore.has(active.w) : false}
				mastered={active ? Boolean(vocabStore.entries[active.w]?.mastered) : false}
				onQueryChange={(value) => (query = value)}
				onOpen={openWord}
				onRandom={randomWord}
				onAdd={addCurrent}
				onRemove={removeCurrent}
				onToggleMastered={toggleMastered}
				onToast={showToast}
			/>
		</div>

		<div class:hidden={tab !== "book"}>
			<WordbookPanel
				{index}
				onOpenWord={openWord}
				onGoLookup={goLookup}
				onStartReview={startReview}
				onToast={showToast}
			/>
		</div>

		<div class:hidden={tab !== "review"}>
			<ReviewPanel
				{index}
				active={tab === "review"}
				startNonce={reviewNonce}
				onOpenWord={openWord}
				onGoLookup={goLookup}
				onToast={showToast}
			/>
		</div>
	{/if}

	<footer class="px-1 pb-1 pt-1 text-[0.62rem] leading-relaxed text-30">
		词库：考研大纲 {meta?.syllabusCount ?? "—"} 词 + 词书拓展，共 {meta?.wordCount ?? "—"} 词；
		真题语料：{meta?.examYears?.[0] ?? 2010}–{meta?.examYears?.[1] ?? 2026} 英语一/二，{meta?.examSentenceCount ?? "—"} 句。
		数据来源：
		<a class="underline decoration-dotted underline-offset-2 hover:text-(--primary)" href="https://github.com/exam-data/NETEMVocabulary" target="_blank" rel="noopener noreferrer">NETEMVocabulary</a>（CC BY-NC-SA 4.0）、
		<a class="underline decoration-dotted underline-offset-2 hover:text-(--primary)" href="https://github.com/KyleBing/english-vocabulary" target="_blank" rel="noopener noreferrer">KyleBing/english-vocabulary</a>、
		<a class="underline decoration-dotted underline-offset-2 hover:text-(--primary)" href="https://github.com/skywind3000/ECDICT" target="_blank" rel="noopener noreferrer">ECDICT</a>、
		<a class="underline decoration-dotted underline-offset-2 hover:text-(--primary)" href="https://github.com/Fantasia1999/kaoyanzhenti" target="_blank" rel="noopener noreferrer">2010–2026 考研英语真题</a>。
		仅用于个人学习研究，不包含红宝书、词汇闪过等版权书籍原文；栏目结构参考其常见编排方式。
	</footer>

	{#if toast}
		<div class="vocab-toast" role="status">
			<Icon icon="material-symbols:check-circle-rounded" class="text-base text-(--primary)" />
			{toast}
		</div>
	{/if}
</div>

<style>
	.vocab-hero-stat {
		display: flex;
		min-width: 4.4rem;
		flex-direction: column;
		border: 1px solid var(--line-divider);
		border-radius: 0.7rem;
		background: color-mix(in oklch, var(--card-bg) 72%, transparent);
		padding: 0.5rem 0.7rem;
		backdrop-filter: blur(4px);
	}
	.vocab-hero-stat-value {
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 1.2rem;
		font-weight: 800;
		line-height: 1.1;
		color: var(--deep-text);
	}
	.vocab-hero-stat-label {
		margin-top: 0.15rem;
		font-size: 0.6rem;
		color: color-mix(in oklch, var(--deep-text) 50%, transparent);
	}

	.vocab-tabs {
		display: inline-flex;
		flex-wrap: wrap;
		gap: 0.25rem;
		border: 1px solid var(--line-divider);
		border-radius: 0.8rem;
		background: var(--card-bg);
		padding: 0.25rem;
	}
	.vocab-tab {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		border-radius: 0.6rem;
		padding: 0.45rem 0.8rem;
		font-size: 0.8rem;
		font-weight: 600;
		color: color-mix(in oklch, var(--deep-text) 60%, transparent);
		transition: all 140ms ease;
	}
	.vocab-tab:hover {
		background: var(--btn-plain-bg-hover);
	}
	.vocab-tab-active {
		background: var(--btn-regular-bg);
		color: var(--btn-content);
		font-weight: 800;
	}
	.vocab-tab-count {
		border-radius: 999px;
		background: color-mix(in oklch, var(--deep-text) 10%, transparent);
		padding: 0 0.3rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.6rem;
	}
	.vocab-tab-count-warm {
		background: color-mix(in oklch, oklch(0.7 0.16 55) 22%, transparent);
		color: oklch(0.5 0.14 55);
	}
	:global(.dark) .vocab-tab-count-warm {
		color: oklch(0.85 0.12 70);
	}

	.vocab-toast {
		position: fixed;
		right: 1rem;
		bottom: 1.25rem;
		z-index: 80;
		display: flex;
		align-items: center;
		gap: 0.4rem;
		border: 1px solid var(--line-divider);
		border-radius: 0.7rem;
		background: var(--card-bg);
		padding: 0.6rem 0.9rem;
		font-size: 0.78rem;
		color: var(--deep-text);
		box-shadow: 0 12px 35px rgb(0 0 0 / 0.16);
		animation: vocab-toast-in 180ms ease-out;
	}
	@keyframes vocab-toast-in {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
