#!/usr/bin/env node
/**
 * Download the raw sources used by the vocabulary module.
 *
 * Outputs to .cache/vocab/ (git-ignored):
 *   netem.json        NETEMVocabulary 5530 syllabus list
 *   kaoyan.jsonl      KyleBing/english-vocabulary kaoyan word books
 *   lemma.en.txt      ECDICT lemma database
 *   ipa.txt           ipa-dict en_US
 *   pdfs/*.pdf        2010-2026 English I/II exam papers
 *
 * Usage:
 *   node scripts/vocab/fetch_sources.mjs
 *   node scripts/vocab/fetch_sources.mjs --skip-pdfs
 *   node scripts/vocab/fetch_sources.mjs --force
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const CACHE = path.join(ROOT, ".cache", "vocab");
const PDF_DIR = path.join(CACHE, "pdfs");
const RAW = "https://raw.githubusercontent.com/";
const MIRROR = "https://ghproxy.net/https://raw.githubusercontent.com/";

const args = new Set(process.argv.slice(2));
const skipPdfs = args.has("--skip-pdfs");
const force = args.has("--force");

fs.mkdirSync(PDF_DIR, { recursive: true });

const encodePath = (value) => value.split("/").map(encodeURIComponent).join("/");

async function download(urls, out, minSize = 10_000) {
	if (!force && fs.existsSync(out) && fs.statSync(out).size >= minSize) {
		return `skip ${path.relative(ROOT, out)}`;
	}
	let lastError;
	for (const base of urls) {
		for (let attempt = 0; attempt < 3; attempt++) {
			try {
				const response = await fetch(base, {
					headers: { "User-Agent": "kaoyan-vocab-builder" },
					signal: AbortSignal.timeout(180_000),
				});
				if (!response.ok) {
					throw new Error(`HTTP ${response.status}`);
				}
				const buffer = Buffer.from(await response.arrayBuffer());
				if (buffer.length < minSize) {
					throw new Error(`too small: ${buffer.length}`);
				}
				const temp = `${out}.part`;
				fs.writeFileSync(temp, buffer);
				fs.renameSync(temp, out);
				return `ok ${path.relative(ROOT, out)} ${(buffer.length / 1024).toFixed(0)}KB`;
			} catch (error) {
				lastError = error;
				await new Promise((resolve) => setTimeout(resolve, 1200 * (attempt + 1)));
			}
		}
	}
	throw new Error(`failed ${out}: ${lastError?.message ?? "unknown"}`);
}

async function pool(items, concurrency, worker) {
	let cursor = 0;
	const run = async () => {
		while (cursor < items.length) {
			const item = items[cursor++];
			try {
				console.log(await worker(item));
			} catch (error) {
				console.error(`FAIL ${item.name}: ${error.message}`);
			}
		}
	};
	await Promise.all(Array.from({ length: concurrency }, run));
}

async function main() {
	console.log("Downloading vocabulary sources into .cache/vocab ...");

	console.log(
		await download(
			[
				`${RAW}exam-data/NETEMVocabulary/master/netem_full_list.json`,
				`${MIRROR}exam-data/NETEMVocabulary/master/netem_full_list.json`,
			],
			path.join(CACHE, "netem.json"),
			1_000_000,
		),
	);
	console.log(
		await download(
			[
				`${RAW}skywind3000/ECDICT/master/lemma.en.txt`,
				`${MIRROR}skywind3000/ECDICT/master/lemma.en.txt`,
			],
			path.join(CACHE, "lemma.en.txt"),
			1_000_000,
		),
	);
	console.log(
		await download(
			[
				`${RAW}open-dict-data/ipa-dict/master/data/en_US.txt`,
				`${MIRROR}open-dict-data/ipa-dict/master/data/en_US.txt`,
			],
			path.join(CACHE, "ipa.txt"),
			1_000_000,
		),
	);
	console.log(
		await download(
			[
				`${RAW}KyleBing/english-vocabulary/master/full_line_jsonl/full/${encodePath("正序")}/${encodePath("考研")}.jsonl`,
				`${MIRROR}KyleBing/english-vocabulary/master/full_line_jsonl/full/${encodePath("正序")}/${encodePath("考研")}.jsonl`,
			],
			path.join(CACHE, "kaoyan.jsonl"),
			1_000_000,
		),
	);

	if (!skipPdfs) {
		const repo = "Fantasia1999/kaoyanzhenti";
		const files = [];
		for (let year = 2010; year <= 2026; year++) {
			for (const paper of [1, 2]) {
				const folder = paper === 1 ? "英语一" : "英语二";
				const file = `${year}年考研英语${paper === 1 ? "一" : "二"}真题.pdf`;
				files.push({
					name: `${year}-${paper}`,
					path: `公共课/英语真题/${folder}/${file}`,
					out: path.join(PDF_DIR, `${year}-${paper}.pdf`),
				});
			}
		}
		await pool(files, 4, (item) =>
			download(
				[
					`${RAW}${repo}/main/${encodePath(item.path)}`,
					`${MIRROR}${repo}/main/${encodePath(item.path)}`,
				],
				item.out,
				50_000,
			).then((message) => `${item.name}: ${message}`),
		);
	}

	console.log("Done. Next: python scripts/vocab/extract_exams.py && python scripts/vocab/build_data.py");
}

main().catch((error) => {
	console.error(error);
	process.exit(1);
});
