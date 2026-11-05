import type { ExamSentence, LegacyExam } from "./types";

const POS_LABELS: Record<string, string> = {
	n: "n.",
	v: "v.",
	vt: "vt.",
	vi: "vi.",
	adj: "adj.",
	adv: "adv.",
	prep: "prep.",
	conj: "conj.",
	pron: "pron.",
	num: "num.",
	int: "int.",
	abbr: "abbr.",
};

export function posLabel(pos: string): string {
	const key = pos.trim().toLowerCase();
	if (!key) {
		return "";
	}
	if (POS_LABELS[key]) {
		return POS_LABELS[key];
	}
	if (key.includes("&")) {
		return key
			.split("&")
			.map((part) => POS_LABELS[part] ?? part)
			.join(" / ");
	}
	return key;
}

export function paperLabel(paper: number): string {
	return paper === 2 ? "英语二" : "英语一";
}

export function examLabel(item: ExamSentence | LegacyExam): string {
	const year = item.y ? `${item.y}` : "真题";
	return `${year} · ${paperLabel(item.p)} · ${item.sec}${
		item.src ? ` ${item.src}` : ""
	}`;
}

export function escapeHtml(value: string): string {
	return value
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#039;");
}

function escapeRegExp(value: string): string {
	return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Highlight the matched surface form inside an exam sentence. */
export function highlight(text: string, hit: string): string {
	const escaped = escapeHtml(text);
	if (!hit) {
		return escaped;
	}
	const pattern = new RegExp(`(${escapeRegExp(escapeHtml(hit))})`, "gi");
	return escaped.replace(
		pattern,
		'<mark class="vocab-mark">$1</mark>',
	);
}

export function shuffle<T>(items: T[]): T[] {
	const copy = [...items];
	for (let i = copy.length - 1; i > 0; i -= 1) {
		const j = Math.floor(Math.random() * (i + 1));
		[copy[i], copy[j]] = [copy[j], copy[i]];
	}
	return copy;
}
