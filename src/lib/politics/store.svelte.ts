import type { Card, CardRecord, Rating } from "./types";

const STORAGE_KEY = "halfman.politics.v1";
const DAY = 86_400_000;
const INTERVALS = [0, 1, 2, 4, 7, 15, 30, 60] as const;
const SHANGHAI_DATE = new Intl.DateTimeFormat("en-CA", {
	timeZone: "Asia/Shanghai",
	year: "numeric",
	month: "2-digit",
	day: "2-digit",
});

function dayNumber(dateKey: string): number {
	const [year, month, day] = dateKey.split("-").map(Number);
	return Date.UTC(year, month - 1, day);
}

export function todayKey(): string {
	return SHANGHAI_DATE.format(new Date());
}

export function addDays(dateKey: string, days: number): string {
	const date = new Date(dayNumber(dateKey) + days * DAY);
	return date.toISOString().slice(0, 10);
}

export function daysBetween(from: string, to: string): number {
	return Math.round((dayNumber(to) - dayNumber(from)) / DAY);
}

export function weekdayLabel(dateKey: string): string {
	return new Intl.DateTimeFormat("zh-CN", {
		timeZone: "Asia/Shanghai",
		weekday: "short",
	}).format(new Date(`${dateKey}T12:00:00+08:00`));
}

export function maxIntervalFor(today: string, examDate: string): number {
	const days = daysBetween(today, examDate);
	if (days > 60) return 30;
	if (days > 30) return 14;
	if (days > 14) return 7;
	if (days > 7) return 3;
	return 1;
}

function isRecord(value: unknown): value is CardRecord {
	if (!value || typeof value !== "object") return false;
	const record = value as Record<string, unknown>;
	return typeof record.stage === "number" && typeof record.due === "string";
}

class PoliticsStore {
	records = $state<Record<string, CardRecord>>({});
	history = $state<Record<string, number>>({});
	loaded = $state(false);
	storageError = $state("");

	load(): void {
		if (this.loaded || typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(STORAGE_KEY);
			if (raw) {
				const parsed = JSON.parse(raw) as {
					records?: Record<string, CardRecord>;
					history?: Record<string, number>;
				};
				if (parsed.records && typeof parsed.records === "object") {
					const clean: Record<string, CardRecord> = {};
					for (const [id, value] of Object.entries(parsed.records)) {
						if (isRecord(value)) {
							clean[id] = {
								stage: Math.max(0, Math.min(7, Number(value.stage) || 0)),
								due: value.due,
								last: typeof value.last === "string" ? value.last : value.due,
								reviews: Math.max(0, Number(value.reviews) || 0),
								lapses: Math.max(0, Number(value.lapses) || 0),
								marked: Boolean(value.marked),
								note: typeof value.note === "string" ? value.note : "",
							};
						}
					}
					this.records = clean;
				}
				if (parsed.history && typeof parsed.history === "object") {
					this.history = parsed.history;
				}
			}
		} catch (error) {
			console.warn("Politics store load failed", error);
			this.storageError = "本地背诵记录读取失败，已使用空数据。";
		} finally {
			this.loaded = true;
		}
	}

	save(): void {
		if (typeof window === "undefined") return;
		try {
			window.localStorage.setItem(
				STORAGE_KEY,
				JSON.stringify({
					version: 1,
					records: this.records,
					history: this.history,
				}),
			);
			this.storageError = "";
		} catch (error) {
			console.warn("Politics store save failed", error);
			this.storageError = "本地存储写入失败，请检查浏览器隐私设置。";
		}
	}

	get(cardId: string): CardRecord | undefined {
		return this.records[cardId];
	}

	toggleMark(cardId: string): boolean {
		const today = todayKey();
		const current = this.records[cardId];
		if (!current) {
			this.records[cardId] = {
				stage: 0,
				due: today,
				last: today,
				reviews: 0,
				lapses: 0,
				marked: true,
				note: "",
			};
			this.save();
			return true;
		}
		current.marked = !current.marked;
		this.save();
		return current.marked;
	}

	setNote(cardId: string, note: string): void {
		const current = this.records[cardId];
		if (!current) return;
		current.note = note.slice(0, 300);
		this.save();
	}

	preview(cardId: string, rating: Rating, maxInterval: number): number {
		const current = this.records[cardId];
		const stage = current?.stage ?? 0;
		if (rating === "again") return 0;
		if (rating === "hard") return 1;
		if (rating === "good") {
			return Math.max(1, Math.min(INTERVALS[Math.min(7, stage + 1)], maxInterval));
		}
		return Math.max(1, Math.min(INTERVALS[Math.min(7, stage + 2)], maxInterval));
	}

	rate(cardId: string, rating: Rating, maxInterval: number): number {
		const today = todayKey();
		const current = this.records[cardId] ?? {
			stage: 0,
			due: today,
			last: today,
			reviews: 0,
			lapses: 0,
			marked: false,
			note: "",
		};
		let stage = current.stage;
		let interval = 0;
		if (rating === "again") {
			stage = 0;
			current.lapses += 1;
		} else if (rating === "hard") {
			stage = Math.max(1, stage);
			interval = 1;
		} else if (rating === "good") {
			stage = Math.min(7, stage + 1);
			interval = Math.max(1, Math.min(INTERVALS[stage], maxInterval));
		} else {
			stage = Math.min(7, stage + 2);
			interval = Math.max(1, Math.min(INTERVALS[stage], maxInterval));
		}
		current.stage = stage;
		current.due = addDays(today, interval);
		current.last = today;
		current.reviews += 1;
		this.records[cardId] = current;
		this.history[today] = (this.history[today] ?? 0) + 1;
		this.save();
		return interval;
	}

	dueCards(cards: Card[], date = todayKey()): Card[] {
		return cards.filter((card) => {
			const record = this.records[card.id];
			return Boolean(record && record.due <= date);
		});
	}

	dueCount(cards: Card[], date = todayKey()): number {
		return this.dueCards(cards, date).length;
	}

	reviewedOn(date = todayKey()): number {
		return this.history[date] ?? 0;
	}

	get streak(): number {
		let cursor = todayKey();
		if (!this.history[cursor]) {
			cursor = addDays(cursor, -1);
		}
		let count = 0;
		while (this.history[cursor]) {
			count += 1;
			cursor = addDays(cursor, -1);
		}
		return count;
	}

	week(): { key: string; label: string; count: number }[] {
		const today = todayKey();
		const result: { key: string; label: string; count: number }[] = [];
		for (let offset = 6; offset >= 0; offset -= 1) {
			const key = addDays(today, -offset);
			result.push({ key, label: weekdayLabel(key), count: this.history[key] ?? 0 });
		}
		return result;
	}

	exportJson(): string {
		return JSON.stringify(
			{ version: 1, exportedAt: new Date().toISOString(), records: this.records, history: this.history },
			null,
			2,
		);
	}

	importJson(raw: string): { ok: boolean; message: string } {
		try {
			const parsed = JSON.parse(raw) as {
				records?: Record<string, CardRecord>;
				history?: Record<string, number>;
			};
			if (!parsed.records || typeof parsed.records !== "object") {
				return { ok: false, message: "文件里没有找到背诵记录。" };
			}
			const clean: Record<string, CardRecord> = {};
			for (const [id, value] of Object.entries(parsed.records)) {
				if (isRecord(value)) {
					clean[id] = {
						stage: Math.max(0, Math.min(7, Number(value.stage) || 0)),
						due: value.due,
						last: typeof value.last === "string" ? value.last : value.due,
						reviews: Math.max(0, Number(value.reviews) || 0),
						lapses: Math.max(0, Number(value.lapses) || 0),
						marked: Boolean(value.marked),
						note: typeof value.note === "string" ? value.note : "",
					};
				}
			}
			this.records = clean;
			this.history = parsed.history ?? {};
			this.save();
			return { ok: true, message: `已导入 ${Object.keys(clean).length} 张卡的记录。` };
		} catch {
			return { ok: false, message: "JSON 解析失败，请检查文件。" };
		}
	}

	reset(): void {
		this.records = {};
		this.history = {};
		this.save();
	}
}

export const politicsStore = new PoliticsStore();
