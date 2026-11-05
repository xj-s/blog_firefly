import type { IndexRow, VocabMeta, WordDetail } from "./types";

const base = import.meta.env.BASE_URL.endsWith("/")
	? import.meta.env.BASE_URL
	: `${import.meta.env.BASE_URL}/`;

const dataUrl = (file: string) => `${base}vocab/data/${file}`;

let metaPromise: Promise<VocabMeta> | null = null;
let indexPromise: Promise<IndexRow[]> | null = null;
const shardCache = new Map<string, Promise<Record<string, WordDetail>>>();

export function loadMeta(): Promise<VocabMeta> {
	if (!metaPromise) {
		metaPromise = fetch(dataUrl("meta.json"))
			.then((response) => {
				if (!response.ok) {
					throw new Error(`meta.json ${response.status}`);
				}
				return response.json() as Promise<VocabMeta>;
			})
			.catch((error) => {
				metaPromise = null;
				throw error;
			});
	}
	return metaPromise;
}

export function loadIndex(): Promise<IndexRow[]> {
	if (!indexPromise) {
		indexPromise = fetch(dataUrl("index.json"))
			.then((response) => {
				if (!response.ok) {
					throw new Error(`index.json ${response.status}`);
				}
				return response.json() as Promise<IndexRow[]>;
			})
			.catch((error) => {
				indexPromise = null;
				throw error;
			});
	}
	return indexPromise;
}

function shardFor(word: string): string {
	const first = word.charAt(0);
	return /^[a-z]$/i.test(first) ? first.toLowerCase() : "_";
}

export function loadShard(letter: string): Promise<Record<string, WordDetail>> {
	const key = /^[a-z]$/i.test(letter) ? letter.toLowerCase() : "_";
	if (!shardCache.has(key)) {
		const promise = fetch(dataUrl(`words/${key}.json`))
			.then((response) => {
				if (!response.ok) {
					throw new Error(`words/${key}.json ${response.status}`);
				}
				return response.json() as Promise<Record<string, WordDetail>>;
			})
			.catch((error) => {
				shardCache.delete(key);
				throw error;
			});
		shardCache.set(key, promise);
	}
	return shardCache.get(key)!;
}

export function normalizeWord(input: string): string {
	return input
		.trim()
		.toLowerCase()
		.replace(/^[^a-z]+|[^a-z'-]+$/g, "")
		.replace(/'s$/, "");
}

export async function loadWord(input: string): Promise<WordDetail | null> {
	const word = normalizeWord(input);
	if (!word) {
		return null;
	}
	const shard = await loadShard(shardFor(word));
	return shard[word] ?? null;
}

export function isChinese(value: string): boolean {
	return /[\u3400-\u9fff]/.test(value);
}

export function searchIndex(
	rows: IndexRow[],
	query: string,
	limit = 8,
): IndexRow[] {
	const q = query.trim().toLowerCase();
	if (!q) {
		return [];
	}
	const chinese = isChinese(q);
	const scored: { row: IndexRow; score: number }[] = [];
	for (const row of rows) {
		const word = row[0];
		const brief = row[2];
		let score = -1;
		if (chinese) {
			if (brief.includes(q)) {
				score = brief.startsWith(q) ? 0 : 1;
			}
		} else if (word === q) {
			score = 0;
		} else if (word.startsWith(q)) {
			score = 1;
		} else if (word.includes(q)) {
			score = 2;
		}
		if (score >= 0) {
			scored.push({ row, score });
		}
	}
	scored.sort((a, b) => {
		if (a.score !== b.score) {
			return a.score - b.score;
		}
		return a.row[4] - b.row[4] || a.row[0].localeCompare(b.row[0]);
	});
	return scored.slice(0, limit).map((item) => item.row);
}

export function suggestWords(
	rows: IndexRow[],
	input: string,
	limit = 6,
): IndexRow[] {
	const q = normalizeWord(input);
	if (!q) {
		return [];
	}
	const prefix = q.slice(0, Math.min(3, q.length));
	const candidates = rows.filter((row) => row[0].startsWith(prefix));
	return candidates.slice(0, limit);
}

export function dailyWord(rows: IndexRow[], date = new Date()): IndexRow | null {
	const pool = rows.filter((row) => row[6] === 1 && row[4] <= 2500);
	if (!pool.length) {
		return rows[0] ?? null;
	}
	const key = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
	let hash = 0;
	for (let i = 0; i < key.length; i++) {
		hash = (hash * 31 + key.charCodeAt(i)) >>> 0;
	}
	return pool[hash % pool.length];
}
