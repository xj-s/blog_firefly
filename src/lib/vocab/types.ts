export interface Translation {
	pos: string;
	cn: string;
	en: string;
}

export interface Phrase {
	en: string;
	cn: string;
}

export interface SynGroup {
	pos: string;
	cn: string;
	words: string[];
}

export interface FamilyGroup {
	pos: string;
	words: { w: string; cn: string }[];
}

export interface Example {
	en: string;
	zh: string;
	src?: string;
}

export interface ExamSentence {
	y: number;
	p: number;
	sec: string;
	src: string;
	text: string;
	hit: string;
	zh?: string;
}

export interface LegacyExam {
	y: number | null;
	p: number;
	sec: string;
	src: string;
	text: string;
	zh?: string;
}

export interface WordDetail {
	w: string;
	uk?: string;
	us?: string;
	trans: Translation[];
	phr?: Phrase[];
	syn?: SynGroup[];
	fam?: FamilyGroup[];
	mem?: string;
	ex: Example[];
	exam?: ExamSentence[];
	legacy?: LegacyExam;
	note?: string;
	confuse?: string[];
	infl?: string[];
	syllabus: boolean;
	rank: number;
	freq: number;
	cefr?: string;
	cat?: string;
	academic: boolean;
	advanced: boolean;
	star: number;
	examCount: number;
}

/** Compact row in index.json. */
export type IndexRow = [
	word: string,
	phonetic: string,
	brief: string,
	pos: string,
	rank: number,
	examCount: number,
	syllabus: 0 | 1,
	cefr: string,
	star: number,
];

export interface SourceInfo {
	name: string;
	url: string;
	license: string;
	use: string;
}

export interface VocabMeta {
	version: number;
	generatedAt: string;
	wordCount: number;
	syllabusCount: number;
	examWordCount: number;
	examSentenceCount: number;
	examYears: [number, number];
	shards: Record<string, number>;
	sources: SourceInfo[];
	notice: string;
}
