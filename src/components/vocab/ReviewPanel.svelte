<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { loadWord } from "@/lib/vocab/data";
import { highlight, posLabel } from "@/lib/vocab/format";
import { vocabStore } from "@/lib/vocab/store.svelte";
import type { WordEntry } from "@/lib/vocab/store.svelte";
import type { IndexRow, WordDetail } from "@/lib/vocab/types";

interface Props {
	index: IndexRow[];
	active?: boolean;
	startNonce?: number;
	onOpenWord: (word: string) => void;
	onGoLookup: () => void;
	onToast: (message: string) => void;
}

let {
	index,
	active = true,
	startNonce = 0,
	onOpenWord,
	onGoLookup,
	onToast,
}: Props = $props();

interface Session {
	queue: WordEntry[];
	index: number;
	revealed: boolean;
	again: number;
	good: number;
	startedAt: number;
}

interface Summary {
	total: number;
	again: number;
	good: number;
	seconds: number;
}

let session = $state<Session | null>(null);
let summary = $state<Summary | null>(null);
let detail = $state<WordDetail | null>(null);
let detailLoading = $state(false);
let speaking = $state(false);
let handledNonce = 0;
let loadToken = 0;

const rowMap = $derived(new Map(index.map((row) => [row[0], row])));
const current = $derived(session ? session.queue[session.index] : null);
const currentRow = $derived(current ? rowMap.get(current.w) : null);
const progress = $derived(
	session ? Math.round((session.index / session.queue.length) * 100) : 0,
);
const dueCount = $derived(vocabStore.dueCount);
const previewQueue = $derived(
	vocabStore.dueEntries.slice(0, Math.min(6, vocabStore.settings.reviewLimit)),
);

$effect(() => {
	if (active && startNonce > handledNonce) {
		handledNonce = startNonce;
		void start();
	}
});

$effect(() => {
	if (session && !session.revealed && vocabStore.settings.autoSpeak && detail) {
		speak(detail.w);
	}
});

async function start() {
	if (session) {
		return;
	}
	summary = null;
	const queue = vocabStore.dueEntries.slice(0, vocabStore.settings.reviewLimit);
	if (!queue.length) {
		onToast("今天没有待复习的单词，先去查几个词吧");
		return;
	}
	session = {
		queue,
		index: 0,
		revealed: false,
		again: 0,
		good: 0,
		startedAt: Date.now(),
	};
	summary = null;
	await loadCurrent();
}

async function loadCurrent() {
	const entry = session?.queue[session.index];
	if (!entry) {
		return;
	}
	const token = ++loadToken;
	detail = null;
	detailLoading = true;
	try {
		const result = await loadWord(entry.w);
		if (token === loadToken) {
			detail = result;
		}
	} catch {
		if (token === loadToken) {
			detail = null;
		}
	} finally {
		if (token === loadToken) {
			detailLoading = false;
		}
	}
}

function reveal() {
	if (session && !session.revealed) {
		session.revealed = true;
	}
}

function rate(value: number) {
	if (!session || !session.revealed || !current) {
		return;
	}
	vocabStore.rate(current.w, value);
	if (value <= 1) {
		session.again += 1;
	} else {
		session.good += 1;
	}
	if (session.index + 1 >= session.queue.length) {
		summary = {
			total: session.queue.length,
			again: session.again,
			good: session.good,
			seconds: Math.max(1, Math.round((Date.now() - session.startedAt) / 1000)),
		};
		session = null;
		detail = null;
		detailLoading = false;
		return;
	}
	session.index += 1;
	session.revealed = false;
	void loadCurrent();
}

function exitSession() {
	session = null;
	summary = null;
	detail = null;
	detailLoading = false;
}

function speak(text: string) {
	if (typeof window === "undefined" || !window.speechSynthesis) {
		onToast("当前浏览器不支持语音朗读");
		return;
	}
	window.speechSynthesis.cancel();
	const utterance = new SpeechSynthesisUtterance(text);
	utterance.lang = "en-GB";
	utterance.rate = 0.86;
	const voices = window.speechSynthesis.getVoices();
	const exact = voices.find((voice) => voice.lang === "en-GB");
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

function handleKeydown(event: KeyboardEvent) {
	if (!active) {
		return;
	}
	if (summary) {
		if (event.key === "Enter") {
			event.preventDefault();
			startNextRound();
		}
		return;
	}
	if (!session) {
		if (event.key === "Enter") {
			event.preventDefault();
			void start();
		}
		return;
	}
	if (event.key === "Escape") {
		event.preventDefault();
		exitSession();
		return;
	}
	if (!session.revealed) {
		if (event.key === " " || event.key === "Enter") {
			event.preventDefault();
			reveal();
		}
		return;
	}
	if (["1", "2", "3", "4"].includes(event.key)) {
		event.preventDefault();
		rate(Number(event.key) - 1);
		return;
	}
	if (event.key === "r") {
		event.preventDefault();
		speak(current?.w ?? "");
	}
}

function startNextRound() {
	summary = null;
	session = null;
	void start();
}

const ratings = [
	{ value: 0, label: "忘记", hint: "完全没印象", tone: "rating-again" },
	{ value: 1, label: "模糊", hint: "有印象但不确定", tone: "rating-hard" },
	{ value: 2, label: "记得", hint: "能说出核心义", tone: "rating-good" },
	{ value: 3, label: "熟练", hint: "秒懂，会用", tone: "rating-easy" },
];
</script>

<svelte:window onkeydown={handleKeydown} />

{#if session}
	<div class="space-y-4">
		<div class="card-base p-4 md:p-5">
			<div class="flex flex-wrap items-center justify-between gap-3">
				<div class="flex items-center gap-3">
					<span class="flex h-9 w-9 items-center justify-center rounded-lg bg-(--btn-regular-bg) text-(--btn-content)">
						<Icon icon="material-symbols:school-rounded" class="text-xl" />
					</span>
					<div>
						<div class="text-sm font-bold text-90">
							复习中 · {session.index + 1} / {session.queue.length}
						</div>
						<div class="text-[0.65rem] text-30">先回想，再揭晓；按 1–4 评分</div>
					</div>
				</div>
				<button type="button" class="btn-plain rounded-lg px-3 py-1.5 text-xs" onclick={exitSession}>
					<Icon icon="material-symbols:close-rounded" class="mr-1 text-base" />
					退出
				</button>
			</div>
			<div class="mt-3 h-1.5 overflow-hidden rounded-full bg-(--btn-regular-bg)">
				<div class="h-full rounded-full bg-(--primary) transition-all duration-500" style={`width: ${progress}%`}></div>
			</div>
		</div>

		<div class="card-base relative overflow-hidden">
			<div
				class="pointer-events-none absolute inset-x-0 top-0 h-32 opacity-60"
				style="background: radial-gradient(70% 120% at 50% 0%, color-mix(in oklch, var(--primary) 15%, transparent), transparent 70%);"
			></div>
			<div class="relative px-5 py-8 md:px-9 md:py-10">
				<div class="text-center">
					<div class="flex flex-wrap items-center justify-center gap-2">
						<h2 class="text-4xl font-black tracking-tight text-90 md:text-6xl">
							{current?.w ?? "…"}
						</h2>
						<button
							type="button"
							class="btn-plain h-9 w-9 rounded-full"
							title="朗读"
							aria-label="朗读"
							onclick={() => speak(current?.w ?? "")}
						>
							<Icon icon="material-symbols:volume-up-rounded" class="text-xl" />
						</button>
					</div>
					<div class="mt-2 flex flex-wrap items-center justify-center gap-2 font-mono text-sm text-50">
						{#if detail?.uk}<span>{detail.uk}</span>{/if}
						{#if detail?.us}<span class="text-30">美 {detail.us}</span>{/if}
						{#if speaking}<span class="text-(--primary)">朗读中…</span>{/if}
					</div>
					{#if currentRow}
						<div class="mt-2 text-xs text-30">
							{currentRow[6] === 1 ? `考研大纲 #${currentRow[4]}` : "词书拓展"}
							{#if currentRow[5] > 0} · 真题 {currentRow[5]} 次{/if}
						</div>
					{/if}
				</div>

				{#if !session.revealed}
					<div class="mx-auto mt-8 max-w-md text-center">
						<p class="text-sm leading-relaxed text-50">
							先在脑子里过一遍：核心义、常考搭配、真题里怎么用。想不起来也没关系，诚实地评分最有效。
						</p>
						<button type="button" class="vocab-action vocab-action-primary mx-auto mt-5" onclick={reveal}>
							<Icon icon="material-symbols:visibility-rounded" class="text-lg" />
							显示释义
						</button>
						<div class="mt-3 text-[0.65rem] text-30">
							按 <kbd class="vocab-kbd">Space</kbd> 或 <kbd class="vocab-kbd">Enter</kbd> 揭晓
						</div>
					</div>
				{:else}
					<div class="mx-auto mt-8 max-w-2xl">
						<div class="space-y-2.5">
							{#if detailLoading}
								<div class="h-20 animate-pulse rounded-xl bg-(--btn-regular-bg)"></div>
							{:else if detail}
								{#each detail.trans.slice(0, 3) as item}
									<div class="rounded-xl border border-(--line-divider) bg-(--card-bg) p-3.5">
										<div class="flex flex-wrap items-baseline gap-2">
											{#if item.pos}
												<span class="rounded bg-(--btn-regular-bg) px-1.5 py-0.5 font-mono text-[0.65rem] font-bold text-(--btn-content)">
													{posLabel(item.pos)}
												</span>
											{/if}
											<span class="text-sm font-semibold leading-relaxed text-90">{item.cn}</span>
										</div>
									</div>
								{/each}
								{#if detail.note}
									<div class="rounded-xl border border-(--line-divider) bg-(--btn-regular-bg) p-3 text-xs leading-relaxed text-75">
										<span class="font-bold text-(--btn-content)">考点：</span>{detail.note}
									</div>
								{/if}
								{#if detail.exam?.[0]}
									<div class="rounded-xl border border-(--line-divider) bg-(--card-bg) p-3.5">
										<div class="flex items-center gap-2 text-[0.65rem] text-30">
											<span class="rounded bg-(--primary) px-1.5 py-0.5 font-mono font-bold text-black/70">
												{detail.exam[0].y}
											</span>
											{detail.exam[0].p === 2 ? "英语二" : "英语一"} · {detail.exam[0].sec}
											{detail.exam[0].src ? ` · ${detail.exam[0].src}` : ""}
										</div>
										<p class="mt-1.5 text-sm leading-relaxed text-75">
											{@html highlight(detail.exam[0].text, detail.exam[0].hit)}
										</p>
									</div>
								{:else if detail.legacy}
									<div class="rounded-xl border border-(--line-divider) bg-(--card-bg) p-3.5">
										<div class="text-[0.65rem] text-30">{detail.legacy.src}</div>
										<p class="mt-1.5 text-sm leading-relaxed text-75">{detail.legacy.text}</p>
									</div>
								{/if}
								{#if detail.mem}
									<div class="rounded-xl bg-(--btn-plain-bg-hover) p-3 text-xs leading-relaxed text-50">
										<span class="font-bold text-75">记忆：</span>{detail.mem}
									</div>
								{/if}
							{:else}
								<div class="rounded-xl border border-dashed border-(--line-divider) p-4 text-center text-xs text-50">
									释义数据加载失败，但评分仍会记录。可以退出后重新进入。
								</div>
							{/if}
						</div>

						<div class="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-4">
							{#each ratings as rating}
								<button
									type="button"
									class={`rating-button ${rating.tone}`}
									onclick={() => rate(rating.value)}
								>
									<span class="text-sm font-black">{rating.label}</span>
									<span class="mt-0.5 text-[0.6rem] opacity-70">
										{vocabStore.previewInterval(current, rating.value)}
									</span>
								</button>
							{/each}
						</div>
						<div class="mt-3 text-center text-[0.65rem] text-30">
							按 <kbd class="vocab-kbd">1</kbd>–<kbd class="vocab-kbd">4</kbd> 评分 ·
							<kbd class="vocab-kbd">R</kbd> 再听一遍 ·
							<kbd class="vocab-kbd">Esc</kbd> 退出
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{:else if summary}
	<div class="card-base relative overflow-hidden p-6 md:p-10">
		<div
			class="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full opacity-40"
			style="background: radial-gradient(circle, color-mix(in oklch, var(--primary) 30%, transparent), transparent 70%);"
		></div>
		<div class="relative mx-auto max-w-xl text-center">
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-(--btn-regular-bg) text-(--btn-content)">
				<Icon icon="material-symbols:emoji-events" class="text-4xl" />
			</div>
			<h2 class="mt-4 text-2xl font-black text-90">这一轮完成了</h2>
			<p class="mt-1 text-sm text-50">
				共 {summary.total} 个词，用时 {summary.seconds < 60 ? `${summary.seconds} 秒` : `${Math.round(summary.seconds / 60)} 分钟`}。
				记得比背得快更重要。
			</p>
			<div class="mt-6 grid grid-cols-2 gap-3">
				<div class="wb-stat">
					<span class="wb-stat-value">{summary.good}</span>
					<span class="wb-stat-label">记得 / 熟练</span>
				</div>
				<div class="wb-stat">
					<span class="wb-stat-value">{summary.again}</span>
					<span class="wb-stat-label">需要重来</span>
				</div>
			</div>
			<div class="mt-6 flex flex-wrap justify-center gap-2">
				<button
					type="button"
					class="vocab-action vocab-action-primary"
					onclick={startNextRound}
					disabled={dueCount === 0}
				>
					<Icon icon="material-symbols:restart-alt-rounded" class="text-lg" />
					再来一轮（{dueCount}）
				</button>
				<button type="button" class="vocab-action vocab-action-ghost" onclick={exitSession}>
					返回复习首页
				</button>
			</div>
			<div class="mt-3 text-[0.65rem] text-30">按 Enter 再来一轮</div>
		</div>
	</div>
{:else}
	<div class="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
		<section class="card-base relative overflow-hidden p-6 md:p-8">
			<div
				class="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full opacity-35"
				style="background: radial-gradient(circle, color-mix(in oklch, var(--primary) 30%, transparent), transparent 70%);"
			></div>
			<div class="relative">
				<div class="flex items-center gap-2 text-[0.68rem] font-bold uppercase tracking-[0.16em] text-(--primary)">
					<Icon icon="material-symbols:school-rounded" class="text-base" />
					Review Session
				</div>
				<h2 class="mt-2 text-3xl font-black text-90">今天该复习了</h2>
				<p class="mt-2 max-w-lg text-sm leading-relaxed text-50">
					按 1 / 2 / 4 / 7 / 15 / 30 / 60 天的间隔排队。忘记的回到今天，记得的往后推，不用自己算日子。
				</p>

				<div class="mt-6 grid grid-cols-3 gap-3">
					<div class="wb-stat">
						<span class="wb-stat-value">{dueCount}</span>
						<span class="wb-stat-label">待复习</span>
					</div>
					<div class="wb-stat">
						<span class="wb-stat-value">{vocabStore.newCount}</span>
						<span class="wb-stat-label">未开始</span>
					</div>
					<div class="wb-stat">
						<span class="wb-stat-value">{vocabStore.todayReviewed}</span>
						<span class="wb-stat-label">今日已复习</span>
					</div>
				</div>

				<div class="mt-6 flex flex-wrap items-center gap-2">
					<button
						type="button"
						class="vocab-action vocab-action-primary px-5 py-2.5"
						onclick={start}
						disabled={dueCount === 0}
					>
						<Icon icon="material-symbols:play-arrow-rounded" class="text-xl" />
						{dueCount === 0 ? "今天已清空" : `开始复习 ${Math.min(dueCount, vocabStore.settings.reviewLimit)} 个`}
					</button>
					<button type="button" class="vocab-action vocab-action-ghost" onclick={onGoLookup}>
						<Icon icon="material-symbols:search" class="text-base" />
						去查词
					</button>
				</div>
				<div class="mt-3 text-[0.65rem] text-30">按 Enter 开始 · 每轮上限可在生词本侧栏调整</div>

				{#if previewQueue.length}
					<div class="mt-6 border-t border-(--line-divider) pt-4">
						<div class="text-[0.68rem] font-bold text-30">队列预览</div>
						<div class="mt-2 flex flex-wrap gap-2">
							{#each previewQueue as entry}
								<button type="button" class="vocab-chip" onclick={() => onOpenWord(entry.w)}>
									{entry.w}
								</button>
							{/each}
							{#if dueCount > previewQueue.length}
								<span class="vocab-chip vocab-chip-muted">+{dueCount - previewQueue.length}</span>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		</section>

		<section class="card-base p-6">
			<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-30">
				<Icon icon="material-symbols:keyboard-rounded" class="text-base text-(--primary)" />
				键盘操作
			</div>
			<div class="mt-3 space-y-2 text-sm text-75">
				<div class="flex items-center justify-between border-b border-(--line-divider) pb-2">
					<span>揭晓释义</span>
					<span><kbd class="vocab-kbd">Space</kbd> / <kbd class="vocab-kbd">Enter</kbd></span>
				</div>
				<div class="flex items-center justify-between border-b border-(--line-divider) pb-2">
					<span>忘记 / 模糊 / 记得 / 熟练</span>
					<span><kbd class="vocab-kbd">1</kbd> <kbd class="vocab-kbd">2</kbd> <kbd class="vocab-kbd">3</kbd> <kbd class="vocab-kbd">4</kbd></span>
				</div>
				<div class="flex items-center justify-between border-b border-(--line-divider) pb-2">
					<span>再听一遍</span>
					<span><kbd class="vocab-kbd">R</kbd></span>
				</div>
				<div class="flex items-center justify-between">
					<span>退出本轮</span>
					<span><kbd class="vocab-kbd">Esc</kbd></span>
				</div>
			</div>

			<div class="mt-5 rounded-xl bg-(--btn-plain-bg-hover) p-3.5 text-xs leading-relaxed text-50">
				<div class="font-bold text-75">怎么打分？</div>
				<p class="mt-1">只看“能不能主动想起来”。看到中文才恍然大悟，算 <b>模糊</b>；能说出核心义和常见搭配，算 <b>记得</b>。</p>
			</div>
		</section>
	</div>
{/if}

<style>
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
	.vocab-chip-muted {
		color: color-mix(in oklch, var(--deep-text) 55%, transparent);
	}
	.rating-button {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border-radius: 0.7rem;
		border: 1px solid transparent;
		padding: 0.65rem 0.4rem;
		color: white;
		transition: transform 120ms ease, filter 120ms ease;
	}
	.rating-button:hover {
		filter: brightness(1.06);
	}
	.rating-button:active {
		transform: scale(0.97);
	}
	.rating-again {
		background: oklch(0.62 0.18 25);
	}
	.rating-hard {
		background: oklch(0.7 0.15 60);
	}
	.rating-good {
		background: oklch(0.62 0.13 160);
	}
	.rating-easy {
		background: oklch(0.58 0.12 255);
	}
	.wb-stat {
		display: flex;
		flex-direction: column;
		border-radius: 0.6rem;
		background: var(--btn-plain-bg-hover);
		padding: 0.6rem 0.65rem;
	}
	.wb-stat-value {
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 1.2rem;
		font-weight: 800;
		line-height: 1.1;
		color: var(--deep-text);
	}
	.wb-stat-label {
		margin-top: 0.15rem;
		font-size: 0.62rem;
		color: color-mix(in oklch, var(--deep-text) 48%, transparent);
	}
</style>
