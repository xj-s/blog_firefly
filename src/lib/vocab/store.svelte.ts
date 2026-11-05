export interface WordEntry {
	w: string;
	addedAt: number;
	due: number;
	stage: number;
	interval: number;
	reps: number;
	lapses: number;
	lastReview: number | null;
	lastRating: number | null;
	mastered: boolean;
	note: string;
}

export interface DayStat {
	reviewed: number;
	added: number;
}

export interface VocabSettings {
	dailyGoal: number;
	reviewLimit: number;
	autoSpeak: boolean;
}

export interface WeekPoint {
	key: string;
	label: string;
	reviewed: number;
	added: number;
}

const STORAGE_KEY = "halfman.vocab.v1";
const DAY = 86_400_000;
const INTERVALS = [0, 1, 2, 4, 7, 15, 30, 60] as const;
const STAGE_LABELS = [
	"新词",
	"第 1 天",
	"第 2 天",
	"第 4 天",
	"第 7 天",
	"第 15 天",
	"第 30 天",
	"第 60 天",
] as const;

const DEFAULT_SETTINGS: VocabSettings = {
	dailyGoal: 20,
	reviewLimit: 40,
	autoSpeak: false,
};

function dayStart(timestamp = Date.now()): number {
	const date = new Date(timestamp);
	date.setHours(0, 0, 0, 0);
	return date.getTime();
}

function dateKey(timestamp = Date.now()): string {
	const date = new Date(timestamp);
	const month = `${date.getMonth() + 1}`.padStart(2, "0");
	const day = `${date.getDate()}`.padStart(2, "0");
	return `${date.getFullYear()}-${month}-${day}`;
}

function isValidEntry(value: unknown): value is WordEntry {
	if (!value || typeof value !== "object") {
		return false;
	}
	const entry = value as Record<string, unknown>;
	return typeof entry.w === "string" && entry.w.length > 0;
}

class VocabStore {
	entries = $state<Record<string, WordEntry>>({});
	settings = $state<VocabSettings>({ ...DEFAULT_SETTINGS });
	stats = $state<Record<string, DayStat>>({});
	loaded = $state(false);
	storageError = $state("");

	load(): void {
		if (this.loaded || typeof window === "undefined") {
			return;
		}
		try {
			const raw = window.localStorage.getItem(STORAGE_KEY);
			if (raw) {
				const parsed = JSON.parse(raw) as {
					entries?: Record<string, WordEntry>;
					settings?: Partial<VocabSettings>;
					stats?: Record<string, DayStat>;
				};
				if (parsed.entries && typeof parsed.entries === "object") {
					const clean: Record<string, WordEntry> = {};
					for (const [key, value] of Object.entries(parsed.entries)) {
						if (isValidEntry(value)) {
							clean[key] = {
								...value,
								due: Number(value.due) || dayStart(),
								stage: Math.max(0, Math.min(7, Number(value.stage) || 0)),
								interval: Number(value.interval) || 0,
								reps: Number(value.reps) || 0,
								lapses: Number(value.lapses) || 0,
								mastered: Boolean(value.mastered),
								note: typeof value.note === "string" ? value.note : "",
							};
						}
					}
					this.entries = clean;
				}
				if (parsed.settings) {
					this.settings = {
						...DEFAULT_SETTINGS,
						...parsed.settings,
						dailyGoal: Math.max(1, Number(parsed.settings.dailyGoal) || 20),
						reviewLimit: Math.max(5, Number(parsed.settings.reviewLimit) || 40),
					};
				}
				if (parsed.stats && typeof parsed.stats === "object") {
					this.stats = parsed.stats;
				}
			}
		} catch (error) {
			console.warn("Vocab store load failed", error);
			this.storageError = "本地生词本读取失败，已使用空数据。";
		} finally {
			this.loaded = true;
		}
	}

	save(): void {
		if (typeof window === "undefined") {
			return;
		}
		try {
			window.localStorage.setItem(
				STORAGE_KEY,
				JSON.stringify({
					version: 1,
					entries: this.entries,
					settings: this.settings,
					stats: this.stats,
				}),
			);
			this.storageError = "";
		} catch (error) {
			console.warn("Vocab store save failed", error);
			this.storageError = "本地存储写入失败，请检查浏览器隐私设置。";
		}
	}

	add(word: string): "added" | "exists" {
		const key = word.toLowerCase();
		if (this.entries[key]) {
			return "exists";
		}
		this.entries[key] = {
			w: key,
			addedAt: Date.now(),
			due: dayStart(),
			stage: 0,
			interval: 0,
			reps: 0,
			lapses: 0,
			lastReview: null,
			lastRating: null,
			mastered: false,
			note: "",
		};
		this.touch("added");
		this.save();
		return "added";
	}

	remove(word: string): void {
		const key = word.toLowerCase();
		if (!this.entries[key]) {
			return;
		}
		delete this.entries[key];
		this.save();
	}

	has(word: string): boolean {
		return Boolean(this.entries[word.toLowerCase()]);
	}

	toggleMastered(word: string): boolean {
		const entry = this.entries[word.toLowerCase()];
		if (!entry) {
			return false;
		}
		entry.mastered = !entry.mastered;
		if (entry.mastered) {
			entry.stage = 7;
			entry.interval = 60;
			entry.due = dayStart() + 60 * DAY;
		} else {
			entry.stage = 3;
			entry.interval = 4;
			entry.due = dayStart() + 4 * DAY;
		}
		this.save();
		return entry.mastered;
	}

	setNote(word: string, note: string): void {
		const entry = this.entries[word.toLowerCase()];
		if (!entry) {
			return;
		}
		entry.note = note.slice(0, 500);
		this.save();
	}

	rate(word: string, rating: number): void {
		const entry = this.entries[word.toLowerCase()];
		if (!entry) {
			return;
		}
		const value = Math.max(0, Math.min(3, Math.round(rating)));
		let stage = entry.stage;
		if (value === 0) {
			stage = 0;
			entry.lapses += 1;
		} else if (value === 1) {
			stage = Math.max(1, stage);
		} else if (value === 2) {
			stage = Math.min(7, stage + 1);
		} else {
			stage = Math.min(7, stage + 2);
		}
		const interval = INTERVALS[stage] ?? 60;
		entry.stage = stage;
		entry.interval = interval;
		entry.reps += 1;
		entry.lastReview = Date.now();
		entry.lastRating = value;
		entry.mastered = stage >= 6;
		entry.due = dayStart() + interval * DAY;
		this.touch("reviewed");
		this.save();
	}

	updateSettings(patch: Partial<VocabSettings>): void {
		this.settings = { ...this.settings, ...patch };
		this.save();
	}

	exportData(): string {
		return JSON.stringify(
			{
				version: 1,
				exportedAt: new Date().toISOString(),
				entries: this.entries,
				settings: this.settings,
				stats: this.stats,
			},
			null,
			2,
		);
	}

	importData(raw: string): number {
		const parsed = JSON.parse(raw) as {
			entries?: Record<string, WordEntry>;
			settings?: Partial<VocabSettings>;
			stats?: Record<string, DayStat>;
		};
		if (!parsed.entries || typeof parsed.entries !== "object") {
			throw new Error("文件里没有找到 entries 字段");
		}
		const clean: Record<string, WordEntry> = {};
		for (const [key, value] of Object.entries(parsed.entries)) {
			if (isValidEntry(value)) {
				clean[key.toLowerCase()] = {
					...value,
					w: value.w.toLowerCase(),
					due: Number(value.due) || dayStart(),
					stage: Math.max(0, Math.min(7, Number(value.stage) || 0)),
					interval: Number(value.interval) || 0,
					reps: Number(value.reps) || 0,
					lapses: Number(value.lapses) || 0,
					mastered: Boolean(value.mastered),
					note: typeof value.note === "string" ? value.note : "",
				};
			}
		}
		this.entries = clean;
		if (parsed.settings) {
			this.settings = { ...DEFAULT_SETTINGS, ...parsed.settings };
		}
		if (parsed.stats && typeof parsed.stats === "object") {
			this.stats = parsed.stats;
		}
		this.save();
		return Object.keys(clean).length;
	}

	reset(): void {
		this.entries = {};
		this.stats = {};
		this.settings = { ...DEFAULT_SETTINGS };
		this.save();
	}

	get total(): number {
		return Object.keys(this.entries).length;
	}

	get masteredCount(): number {
		return Object.values(this.entries).filter((entry) => entry.mastered).length;
	}

	get dueEntries(): WordEntry[] {
		const limit = dayStart() + DAY - 1;
		return Object.values(this.entries)
			.filter((entry) => !entry.mastered && entry.due <= limit)
			.sort((a, b) => a.due - b.due || a.addedAt - b.addedAt);
	}

	get dueCount(): number {
		return this.dueEntries.length;
	}

	get newCount(): number {
		return Object.values(this.entries).filter((entry) => entry.reps === 0).length;
	}

	get todayReviewed(): number {
		return this.stats[dateKey()]?.reviewed ?? 0;
	}

	get todayAdded(): number {
		return this.stats[dateKey()]?.added ?? 0;
	}

	get goalProgress(): number {
		return Math.min(100, Math.round((this.todayAdded / this.settings.dailyGoal) * 100));
	}

	get streak(): number {
		let cursor = new Date();
		if (!this.stats[dateKey(cursor.getTime())]?.reviewed) {
			cursor = new Date(cursor.getTime() - DAY);
		}
		let count = 0;
		while (count < 365) {
			const stat = this.stats[dateKey(cursor.getTime())];
			if (!stat || stat.reviewed <= 0) {
				break;
			}
			count += 1;
			cursor = new Date(cursor.getTime() - DAY);
		}
		return count;
	}

	get week(): WeekPoint[] {
		const out: WeekPoint[] = [];
		const labels = ["日", "一", "二", "三", "四", "五", "六"];
		for (let offset = 6; offset >= 0; offset -= 1) {
			const date = new Date(dayStart() - offset * DAY);
			const key = dateKey(date.getTime());
			const stat = this.stats[key];
			out.push({
				key,
				label: labels[date.getDay()],
				reviewed: stat?.reviewed ?? 0,
				added: stat?.added ?? 0,
			});
		}
		return out;
	}

	stageLabel(stage: number): string {
		return STAGE_LABELS[Math.max(0, Math.min(7, stage))] ?? "新词";
	}

	statusOf(entry: WordEntry): "new" | "learning" | "reviewing" | "mastered" {
		if (entry.mastered) {
			return "mastered";
		}
		if (entry.reps === 0) {
			return "new";
		}
		return entry.stage <= 2 ? "learning" : "reviewing";
	}

	dueLabel(entry: WordEntry): string {
		if (entry.mastered) {
			return "已掌握";
		}
		const diff = Math.round((entry.due - dayStart()) / DAY);
		if (diff <= 0) {
			return "今天";
		}
		if (diff === 1) {
			return "明天";
		}
		return `${diff} 天后`;
	}

	previewInterval(
		entry: WordEntry | null | undefined,
		rating: number,
	): string {
		if (!entry) {
			return "";
		}
		let stage = entry.stage;
		if (rating === 0) {
			stage = 0;
		} else if (rating === 1) {
			stage = Math.max(1, stage);
		} else if (rating === 2) {
			stage = Math.min(7, stage + 1);
		} else {
			stage = Math.min(7, stage + 2);
		}
		const days = INTERVALS[stage] ?? 60;
		if (days === 0) {
			return "今天再来";
		}
		return `${days} 天后`;
	}

	private touch(field: "reviewed" | "added"): void {
		const key = dateKey();
		const stat = this.stats[key] ?? { reviewed: 0, added: 0 };
		stat[field] += 1;
		this.stats[key] = stat;
	}
}

export const vocabStore = new VocabStore();
