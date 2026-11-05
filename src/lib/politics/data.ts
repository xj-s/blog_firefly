import type { Card, IndexRow, PlanDay, Point, PoliticsMeta } from "./types";

const base = import.meta.env.BASE_URL.endsWith("/")
	? import.meta.env.BASE_URL
	: `${import.meta.env.BASE_URL}/`;

const dataUrl = (file: string) => `${base}politics/data/${file}`;

async function getJson<T>(file: string): Promise<T> {
	const response = await fetch(dataUrl(file));
	if (!response.ok) {
		throw new Error(`${file} ${response.status}`);
	}
	return response.json() as Promise<T>;
}

function once<T>(loader: () => Promise<T>): () => Promise<T> {
	let promise: Promise<T> | null = null;
	return () => {
		if (!promise) {
			promise = loader().catch((error) => {
				promise = null;
				throw error;
			});
		}
		return promise;
	};
}

export const loadMeta = once(() => getJson<PoliticsMeta>("meta.json"));
export const loadIndex = once(() => getJson<IndexRow[]>("index.json"));
export const loadPlan = once(() => getJson<PlanDay[]>("plan.json"));
export const loadCards = once(() => getJson<Card[]>("cards.json"));
export const loadPoints = once(() => getJson<Point[]>("points.json"));

export function figureUrl(path: string | null | undefined): string {
	return path ? `${base}politics/data/${path}` : "";
}

export function cardsForPoint(cards: Card[], pointId: string): Card[] {
	return cards.filter((card) => card.pointId === pointId);
}

export function cardsForPoints(cards: Card[], pointIds: string[]): Card[] {
	const wanted = new Set(pointIds);
	return cards.filter((card) => wanted.has(card.pointId));
}
