<script lang="ts">
import Icon from "@/components/common/Icon.svelte";
import { vocabStore } from "@/lib/vocab/store.svelte";
import type { WordEntry as StoreEntry } from "@/lib/vocab/store.svelte";
import type { IndexRow } from "@/lib/vocab/types";

interface Props {
	index: IndexRow[];
	onOpenWord: (word: string) => void;
	onGoLookup: () => void;
	onStartReview: () => void;
	onToast: (message: string) => void;
}

let { index, onOpenWord, onGoLookup, onStartReview, onToast }: Props = $props();

type Filter = "all" | "due" | "learning" | "mastered";
type Sort = "added" | "due" | "alpha";

let filter = $state<Filter>("all");
let query = $state("");
let sort = $state<Sort>("added");
let editing = $state<string | null>(null);
let noteDraft = $state("");
let confirmReset = $state(false);
let fileInput = $state<HTMLInputElement | undefined>();

const rowMap = $derived(new Map(index.map((row) => [row[0], row])));
const endOfToday = $derived.by(() => {
	const date = new Date();
	date.setHours(23, 59, 59, 999);
	return date.getTime();
});
const entries = $derived(Object.values(vocabStore.entries));

const filtered = $derived.by(() => {
	const q = query.trim().toLowerCase();
	let list = entries;
	if (filter === "due") {
		list = list.filter((entry) => !entry.mastered && entry.due <= endOfToday);
	} else if (filter === "learning") {
		list = list.filter(
			(entry) => !entry.mastered && entry.reps > 0 && entry.stage <= 3,
		);
	} else if (filter === "mastered") {
		list = list.filter((entry) => entry.mastered);
	}
	if (q) {
		list = list.filter((entry) => {
			const brief = rowMap.get(entry.w)?.[2] ?? "";
			return (
				entry.w.includes(q) ||
				entry.note.toLowerCase().includes(q) ||
				brief.toLowerCase().includes(q)
			);
		});
	}
	return [...list].sort((a, b) => {
		if (sort === "due") {
			return a.due - b.due || a.w.localeCompare(b.w);
		}
		if (sort === "alpha") {
			return a.w.localeCompare(b.w);
		}
		return b.addedAt - a.addedAt;
	});
});

const weekMax = $derived(
	Math.max(1, ...vocabStore.week.map((point) => point.reviewed)),
);

const filters = $derived([
	{ key: "all" as Filter, label: "全部", count: entries.length },
	{ key: "due" as Filter, label: "待复习", count: vocabStore.dueCount },
	{
		key: "learning" as Filter,
		label: "学习中",
		count: entries.filter((entry) => !entry.mastered && entry.reps > 0).length,
	},
	{ key: "mastered" as Filter, label: "已掌握", count: vocabStore.masteredCount },
]);

function openNote(entry: StoreEntry) {
	editing = editing === entry.w ? null : entry.w;
	noteDraft = entry.note;
}

function saveNote(word: string) {
	vocabStore.setNote(word, noteDraft);
	editing = null;
	onToast("笔记已保存");
}

function removeWord(entry: StoreEntry) {
	vocabStore.remove(entry.w);
	onToast(`已移出生词本：${entry.w}`);
}

function exportBackup() {
	const blob = new Blob([vocabStore.exportData()], { type: "application/json" });
	const url = URL.createObjectURL(blob);
	const anchor = document.createElement("a");
	const stamp = new Date().toISOString().slice(0, 10);
	anchor.href = url;
	anchor.download = `kaoyan-vocab-${stamp}.json`;
	anchor.click();
	window.setTimeout(() => URL.revokeObjectURL(url), 1000);
	onToast("备份已导出");
}

async function importBackup(event: Event) {
	const input = event.currentTarget as HTMLInputElement;
	const file = input.files?.[0];
	if (!file) {
		return;
	}
	try {
		const count = vocabStore.importData(await file.text());
		onToast(`已导入 ${count} 个单词`);
	} catch (error) {
		onToast(
			`导入失败：${error instanceof Error ? error.message : "文件格式不正确"}`,
		);
	} finally {
		input.value = "";
	}
}

function resetAll() {
	if (!confirmReset) {
		confirmReset = true;
		return;
	}
	vocabStore.reset();
	confirmReset = false;
	onToast("生词本已清空");
}

function statusClass(entry: StoreEntry): string {
	const status = vocabStore.statusOf(entry);
	if (status === "mastered") return "wb-status-mastered";
	if (status === "learning") return "wb-status-learning";
	if (status === "reviewing") return "wb-status-reviewing";
	return "wb-status-new";
}

function formatDate(timestamp: number): string {
	return new Date(timestamp).toLocaleDateString("zh-CN", {
		month: "2-digit",
		day: "2-digit",
	});
}
</script>

<div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_19rem]">
	<section class="card-base self-start overflow-hidden">
		<header class="border-b border-(--line-divider) px-5 py-5 md:px-6">
			<div class="flex flex-wrap items-end justify-between gap-3">
				<div>
					<div class="flex items-center gap-2 text-[0.68rem] font-bold uppercase tracking-[0.16em] text-(--primary)">
						<Icon icon="material-symbols:bookmarks-rounded" class="text-base" />
						My Wordbook
					</div>
					<h2 class="mt-1 text-2xl font-black text-90">我的生词本</h2>
					<p class="mt-1 text-xs text-50">
						{entries.length} 个词 · 今天新增 {vocabStore.todayAdded} · 待复习 {vocabStore.dueCount}
					</p>
				</div>
				<button type="button" class="vocab-action vocab-action-primary" onclick={onStartReview}>
					<Icon icon="material-symbols:play-arrow-rounded" class="text-lg" />
					开始复习
				</button>
			</div>

			<div class="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center">
				<div class="relative min-w-0 flex-1">
					<span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-2.5 text-30">
						<Icon icon="material-symbols:search" class="text-base" />
					</span>
					<input
						type="search"
						class="w-full rounded-lg border border-(--line-divider) bg-transparent py-2 pl-8 pr-3 text-sm text-75 outline-none transition-colors placeholder:text-30 focus:border-(--primary)"
						placeholder="搜索单词或笔记"
						bind:value={query}
					/>
				</div>
				<select
					class="rounded-lg border border-(--line-divider) bg-(--card-bg) px-2.5 py-2 text-xs text-75 outline-none"
					bind:value={sort}
					aria-label="排序方式"
				>
					<option value="added">按加入时间</option>
					<option value="due">按复习时间</option>
					<option value="alpha">按字母</option>
				</select>
			</div>

			<div class="mt-3 flex flex-wrap gap-1.5">
				{#each filters as item}
					<button
						type="button"
						class={`wb-filter ${filter === item.key ? "wb-filter-active" : ""}`}
						onclick={() => (filter = item.key)}
					>
						{item.label}
						<span class="wb-filter-count">{item.count}</span>
					</button>
				{/each}
			</div>
		</header>

		{#if entries.length === 0}
			<div class="px-6 py-14 text-center">
				<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-(--btn-regular-bg) text-(--btn-content)">
					<Icon icon="material-symbols:bookmark-add-rounded" class="text-3xl" />
				</div>
				<h3 class="mt-3 text-lg font-bold text-90">生词本还是空的</h3>
				<p class="mt-1 text-sm text-50">查词时点一下“加入生词本”，这里就会按记忆曲线帮你排队。</p>
				<button type="button" class="vocab-action vocab-action-primary mt-4" onclick={onGoLookup}>
					<Icon icon="material-symbols:search" class="text-lg" />
					去查第一个词
				</button>
			</div>
		{:else if filtered.length === 0}
			<div class="px-6 py-12 text-center text-sm text-50">这个筛选下还没有单词。</div>
		{:else}
			<div class="divide-y divide-(--line-divider)">
				{#each filtered as entry (entry.w)}
					<div class="wb-row">
						<button
							type="button"
							class="flex min-w-0 flex-1 items-start gap-3 text-left"
							onclick={() => onOpenWord(entry.w)}
						>
							<span class={`wb-status-dot ${statusClass(entry)}`}></span>
							<span class="min-w-0 flex-1">
								<span class="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
									<span class="font-mono text-lg font-bold text-90">{entry.w}</span>
									{#if rowMap.get(entry.w)?.[1]}
										<span class="font-mono text-[0.68rem] text-30">{rowMap.get(entry.w)?.[1]}</span>
									{/if}
									<span class={`wb-stage ${statusClass(entry)}`}>
										{vocabStore.stageLabel(entry.stage)}
									</span>
								</span>
								<span class="mt-0.5 block truncate text-xs text-50">
									{rowMap.get(entry.w)?.[2] ?? "释义加载中…"}
								</span>
								{#if entry.note}
									<span class="mt-1 block truncate text-[0.68rem] text-30">笔记：{entry.note}</span>
								{/if}
								<span class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[0.65rem] text-30">
									<span>加入 {formatDate(entry.addedAt)}</span>
									<span>复习 {entry.reps} 次</span>
									{#if entry.lapses > 0}<span>遗忘 {entry.lapses} 次</span>{/if}
									<span class="font-semibold text-(--btn-content)">{vocabStore.dueLabel(entry)}</span>
								</span>
							</span>
						</button>
						<div class="flex shrink-0 items-center gap-1">
							<button
								type="button"
								class="btn-plain h-8 w-8 rounded-lg"
								title="笔记"
								aria-label="编辑笔记"
								onclick={() => openNote(entry)}
							>
								<Icon icon="material-symbols:sticky-note-2-rounded" class="text-base" />
							</button>
							<button
								type="button"
								class="btn-plain h-8 w-8 rounded-lg hover:text-red-500"
								title="移出生词本"
								aria-label="移出生词本"
								onclick={() => removeWord(entry)}
							>
								<Icon icon="material-symbols:delete-outline-rounded" class="text-base" />
							</button>
						</div>

						{#if editing === entry.w}
							<div class="wb-note-editor">
								<textarea
									class="min-h-20 w-full resize-y rounded-lg border border-(--line-divider) bg-(--card-bg) p-2.5 text-sm text-75 outline-none focus:border-(--primary)"
									placeholder="记一个触发点：真题搭配、易混词、你反复忘的那层意思…"
									bind:value={noteDraft}
								></textarea>
								<div class="mt-2 flex justify-end gap-2">
									<button type="button" class="vocab-action vocab-action-ghost" onclick={() => (editing = null)}>
										取消
									</button>
									<button type="button" class="vocab-action vocab-action-primary" onclick={() => saveNote(entry.w)}>
										保存笔记
									</button>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<aside class="space-y-4 self-start">
		<section class="card-base p-5">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-30">
					<Icon icon="material-symbols:flag-rounded" class="text-base text-(--primary)" />
					今日计划
				</div>
				<span class="text-[0.65rem] text-30">{vocabStore.todayAdded}/{vocabStore.settings.dailyGoal}</span>
			</div>
			<div class="mt-3 h-2 overflow-hidden rounded-full bg-(--btn-regular-bg)">
				<div
					class="h-full rounded-full bg-(--primary) transition-all duration-500"
					style={`width: ${vocabStore.goalProgress}%`}
				></div>
			</div>
			<div class="mt-4 grid grid-cols-2 gap-2">
				<div class="wb-stat">
					<span class="wb-stat-value">{vocabStore.dueCount}</span>
					<span class="wb-stat-label">待复习</span>
				</div>
				<div class="wb-stat">
					<span class="wb-stat-value">{vocabStore.todayReviewed}</span>
					<span class="wb-stat-label">今日已复习</span>
				</div>
				<div class="wb-stat">
					<span class="wb-stat-value">{vocabStore.masteredCount}</span>
					<span class="wb-stat-label">已掌握</span>
				</div>
				<div class="wb-stat">
					<span class="wb-stat-value">{vocabStore.streak}</span>
					<span class="wb-stat-label">连续天数</span>
				</div>
			</div>
		</section>

		<section class="card-base p-5">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-30">
					<Icon icon="material-symbols:trending-up-rounded" class="text-base text-(--primary)" />
					近 7 天
				</div>
				<span class="text-[0.65rem] text-30">复习量</span>
			</div>
			<div class="mt-3 flex h-24 items-end justify-between gap-1.5">
				{#each vocabStore.week as point}
					<div class="flex flex-1 flex-col items-center gap-1.5">
						<div class="flex h-16 w-full items-end">
							<div
								class={`w-full rounded-t transition-all duration-500 ${point.reviewed > 0 ? "bg-(--primary)" : "bg-(--btn-regular-bg)"}`}
								style={`height: ${Math.max(4, (point.reviewed / weekMax) * 100)}%`}
								title={`${point.key} 复习 ${point.reviewed} 次`}
							></div>
						</div>
						<span class="text-[0.6rem] text-30">{point.label}</span>
					</div>
				{/each}
			</div>
		</section>

		<section class="card-base p-5">
			<div class="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-30">
				<Icon icon="material-symbols:settings-rounded" class="text-base text-(--primary)" />
				设置与备份
			</div>
			<div class="mt-3 space-y-2.5">
				<label class="flex items-center justify-between gap-3 text-xs text-75">
					<span>每日新词目标</span>
					<input
						type="number"
						min="1"
						max="200"
						class="w-16 rounded-md border border-(--line-divider) bg-transparent px-2 py-1 text-right text-xs outline-none focus:border-(--primary)"
						value={vocabStore.settings.dailyGoal}
						onchange={(event) =>
							vocabStore.updateSettings({
								dailyGoal: Math.max(1, Number(event.currentTarget.value) || 20),
							})}
					/>
				</label>
				<label class="flex items-center justify-between gap-3 text-xs text-75">
					<span>每轮复习上限</span>
					<input
						type="number"
						min="5"
						max="200"
						class="w-16 rounded-md border border-(--line-divider) bg-transparent px-2 py-1 text-right text-xs outline-none focus:border-(--primary)"
						value={vocabStore.settings.reviewLimit}
						onchange={(event) =>
							vocabStore.updateSettings({
								reviewLimit: Math.max(5, Number(event.currentTarget.value) || 40),
							})}
					/>
				</label>
				<label class="flex items-center justify-between gap-3 text-xs text-75">
					<span>进入卡片时自动发音</span>
					<input
						type="checkbox"
						class="h-4 w-4 accent-(--primary)"
						checked={vocabStore.settings.autoSpeak}
						onchange={(event) =>
							vocabStore.updateSettings({ autoSpeak: event.currentTarget.checked })}
					/>
				</label>
			</div>

			<div class="mt-4 grid grid-cols-2 gap-2">
				<button type="button" class="wb-tool" onclick={exportBackup}>
					<Icon icon="material-symbols:download-rounded" class="text-base" />
					导出
				</button>
				<button type="button" class="wb-tool" onclick={() => fileInput?.click()}>
					<Icon icon="material-symbols:upload-rounded" class="text-base" />
					导入
				</button>
			</div>
			<input
				bind:this={fileInput}
				type="file"
				accept="application/json,.json"
				class="hidden"
				onchange={importBackup}
			/>

			{#if confirmReset}
				<div class="mt-3 rounded-lg border border-red-400/30 bg-red-400/5 p-2.5 text-[0.68rem] text-red-500">
					确认清空全部生词和复习记录？此操作不可撤销。
					<div class="mt-2 flex gap-2">
						<button type="button" class="vocab-action vocab-action-ghost px-2 py-1 text-[0.68rem]" onclick={resetAll}>
							确认清空
						</button>
						<button type="button" class="vocab-action vocab-action-ghost px-2 py-1 text-[0.68rem]" onclick={() => (confirmReset = false)}>
							取消
						</button>
					</div>
				</div>
			{:else}
				<button
					type="button"
					class="mt-3 text-[0.68rem] text-30 underline decoration-dotted underline-offset-2 hover:text-red-500"
					onclick={resetAll}
				>
					清空生词本
				</button>
			{/if}

			{#if vocabStore.storageError}
				<p class="mt-2 text-[0.65rem] text-red-500">{vocabStore.storageError}</p>
			{/if}
		</section>

		<p class="px-1 text-[0.62rem] leading-relaxed text-30">
			生词本与笔记只保存在当前浏览器（localStorage），不会上传到服务器。换设备前请先导出 JSON 备份。
		</p>
	</aside>
</div>

<style>
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
	.vocab-action:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.wb-row {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-start;
		gap: 0.5rem;
		padding: 0.85rem 1.25rem;
		transition: background 120ms ease;
	}
	.wb-row:hover {
		background: var(--btn-plain-bg-hover);
	}
	.wb-status-dot {
		margin-top: 0.45rem;
		height: 0.5rem;
		width: 0.5rem;
		flex-shrink: 0;
		border-radius: 999px;
		background: var(--line-color);
	}
	.wb-status-new {
		background: oklch(0.7 0.13 250);
	}
	.wb-status-learning {
		background: oklch(0.75 0.14 70);
	}
	.wb-status-reviewing {
		background: oklch(0.68 0.14 150);
	}
	.wb-status-mastered {
		background: var(--primary);
	}
	.wb-stage {
		border-radius: 0.3rem;
		padding: 0.05rem 0.3rem;
		font-size: 0.6rem;
		font-weight: 700;
		color: color-mix(in oklch, var(--deep-text) 55%, transparent);
		background: var(--btn-regular-bg);
	}
	.wb-stage.wb-status-new {
		color: oklch(0.45 0.12 250);
		background: oklch(0.93 0.04 250);
	}
	.wb-stage.wb-status-learning {
		color: oklch(0.48 0.12 65);
		background: oklch(0.95 0.04 80);
	}
	.wb-stage.wb-status-reviewing {
		color: oklch(0.42 0.1 150);
		background: oklch(0.93 0.04 150);
	}
	.wb-stage.wb-status-mastered {
		color: var(--btn-content);
		background: var(--btn-regular-bg);
	}
	:global(.dark) .wb-stage.wb-status-new {
		color: oklch(0.8 0.1 250);
		background: oklch(0.32 0.04 250);
	}
	:global(.dark) .wb-stage.wb-status-learning {
		color: oklch(0.85 0.1 75);
		background: oklch(0.34 0.04 70);
	}
	:global(.dark) .wb-stage.wb-status-reviewing {
		color: oklch(0.82 0.1 150);
		background: oklch(0.32 0.04 150);
	}

	.wb-filter {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		border: 1px solid var(--line-divider);
		border-radius: 999px;
		padding: 0.2rem 0.55rem;
		font-size: 0.7rem;
		color: color-mix(in oklch, var(--deep-text) 60%, transparent);
		transition: all 120ms ease;
	}
	.wb-filter:hover {
		background: var(--btn-plain-bg-hover);
	}
	.wb-filter-active {
		border-color: color-mix(in oklch, var(--primary) 35%, transparent);
		background: var(--btn-regular-bg);
		color: var(--btn-content);
		font-weight: 700;
	}
	.wb-filter-count {
		border-radius: 999px;
		background: color-mix(in oklch, var(--deep-text) 8%, transparent);
		padding: 0 0.28rem;
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.6rem;
	}

	.wb-note-editor {
		width: 100%;
		padding: 0 0 0.2rem 1.1rem;
	}

	.wb-stat {
		display: flex;
		flex-direction: column;
		border-radius: 0.6rem;
		background: var(--btn-plain-bg-hover);
		padding: 0.55rem 0.6rem;
	}
	.wb-stat-value {
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 1.15rem;
		font-weight: 800;
		line-height: 1.1;
		color: var(--deep-text);
	}
	.wb-stat-label {
		margin-top: 0.15rem;
		font-size: 0.62rem;
		color: color-mix(in oklch, var(--deep-text) 48%, transparent);
	}

	.wb-tool {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.3rem;
		border: 1px solid var(--line-divider);
		border-radius: 0.5rem;
		padding: 0.4rem 0.5rem;
		font-size: 0.7rem;
		color: color-mix(in oklch, var(--deep-text) 65%, transparent);
		transition: all 120ms ease;
	}
	.wb-tool:hover {
		border-color: color-mix(in oklch, var(--primary) 35%, transparent);
		background: var(--btn-plain-bg-hover);
		color: var(--btn-content);
	}
</style>
