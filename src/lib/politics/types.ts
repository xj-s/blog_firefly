export type Tone = "plain" | "muted" | "key" | "warm" | "blue" | "purple" | "green";

export interface ToneSpan {
	text: string;
	tone: Tone;
	size?: number;
}

export interface Block {
	text: string;
	spans: ToneSpan[];
}

export interface Figure {
	src: string;
	alt: string;
}

export interface Point {
	id: string;
	n: number;
	title: string;
	section: string;
	sectionName: string;
	topic: string;
	page: number;
	pages: number[];
	blocks: Block[];
	figure?: Figure | null;
	keywords: string[];
	preview: string;
}

export interface Card {
	id: string;
	pointId: string;
	title: string;
	pointTitle: string;
	section: string;
	sectionName: string;
	topic: string;
	page: number;
	kind: "point" | "meeting" | "mnemonic" | "figure";
	prompt: string;
	part: string;
	hint: string;
	blocks: Block[];
	keywords: string[];
	figure?: string | null;
	figureAlt: string;
	figureCaption: string;
	seq: number;
}

export interface Section {
	id: string;
	name: string;
	startPage: number;
	endPage: number;
	color: string;
	count: number;
}

export interface PoliticsMeta {
	version: number;
	generatedAt: string;
	source: string;
	examDate: string;
	planStart: string;
	planEnd: string;
	pointCount: number;
	pageCount: number;
	cardCount: number;
	cardHint: string;
	sections: Section[];
}

export interface PlanDay {
	date: string;
	day: number;
	phase: string;
	pages: number[];
	pointIds: string[];
	focus: string;
	minutes: number;
}

export type IndexRow = Pick<
	Point,
	"id" | "n" | "title" | "section" | "sectionName" | "topic" | "page" | "pages" | "keywords" | "preview"
>;

export type Rating = "again" | "hard" | "good" | "easy";

export interface CardRecord {
	stage: number;
	due: string;
	last: string;
	reviews: number;
	lapses: number;
	marked: boolean;
	note: string;
}

export type StudyStatus = "new" | "learning" | "mastered" | "marked" | "wrong";
