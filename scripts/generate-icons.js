/**
 * Inline icon preprocessor.
 *
 * Scans .svelte files for literal icon names (plus a fixed list of icons that
 * are selected dynamically), renders them to SVG and writes src/constants/icons.ts.
 *
 * Usage: node scripts/generate-icons.js
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { getIconData, iconToSVG, iconToHTML, replaceIDs } from "@iconify/utils";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = join(__dirname, "..");
const SRC_DIR = join(ROOT_DIR, "src");
const OUTPUT_FILE = join(SRC_DIR, "constants", "icons.ts");

const ICON_SETS = {
	"material-symbols": "@iconify-json/material-symbols",
	"fa7-solid": "@iconify-json/fa7-solid",
	"fa7-brands": "@iconify-json/fa7-brands",
	"fa7-regular": "@iconify-json/fa7-regular",
	mdi: "@iconify-json/mdi",
	"simple-icons": "@iconify-json/simple-icons",
	mingcute: "@iconify-json/mingcute",
	"svg-spinners": "@iconify-json/svg-spinners",
};

// Icons selected at runtime (dynamic `icon={...}` props) cannot be discovered
// by the regex scanner. Keep the vocabulary module's icons here.
const EXTRA_ICONS = [
	"material-symbols:menu-book-rounded",
	"material-symbols:menu-book",
	"material-symbols:search",
	"material-symbols:search-off-rounded",
	"material-symbols:close-rounded",
	"material-symbols:volume-up-rounded",
	"material-symbols:bookmark-add-rounded",
	"material-symbols:bookmark-added-rounded",
	"material-symbols:bookmark-rounded",
	"material-symbols:bookmarks-rounded",
	"material-symbols:check-circle-rounded",
	"material-symbols:check-rounded",
	"material-symbols:refresh-rounded",
	"material-symbols:arrow-back-rounded",
	"material-symbols:arrow-forward-rounded",
	"material-symbols:download-rounded",
	"material-symbols:upload-rounded",
	"material-symbols:settings-rounded",
	"material-symbols:school-rounded",
	"material-symbols:local-fire-department-rounded",
	"material-symbols:calendar-month-rounded",
	"material-symbols:lightbulb-rounded",
	"material-symbols:translate-rounded",
	"material-symbols:chevron-right-rounded",
	"material-symbols:chevron-left-rounded",
	"material-symbols:expand-less-rounded",
	"material-symbols:expand-more-rounded",
	"material-symbols:content-copy-rounded",
	"material-symbols:play-arrow-rounded",
	"material-symbols:emoji-events",
	"material-symbols:trending-up-rounded",
	"material-symbols:history-rounded",
	"material-symbols:history-edu-rounded",
	"material-symbols:delete-outline-rounded",
	"material-symbols:filter-list-rounded",
	"material-symbols:sort-by-alpha-rounded",
	"material-symbols:keyboard-rounded",
	"material-symbols:info-outline-rounded",
	"material-symbols:auto-awesome-rounded",
	"material-symbols:flag-rounded",
	"material-symbols:casino",
	"material-symbols:visibility-rounded",
	"material-symbols:sticky-note-2-rounded",
	"material-symbols:sync-alt-rounded",
	"material-symbols:account-tree-rounded",
	"material-symbols:swap-horiz-rounded",
	"material-symbols:link-rounded",
	"material-symbols:compare-arrows-rounded",
	"material-symbols:schedule-rounded",
	"material-symbols:restart-alt-rounded",
	"material-symbols:inventory-2-rounded",
];

const iconSetCache = new Map();

function getAllFiles(dir, extensions = [".svelte"]) {
	const files = [];
	const walk = (currentDir) => {
		for (const item of readdirSync(currentDir)) {
			const fullPath = join(currentDir, item);
			const stat = statSync(fullPath);
			if (stat.isDirectory()) {
				if (!item.startsWith(".") && item !== "node_modules") {
					walk(fullPath);
				}
			} else if (extensions.some((ext) => item.endsWith(ext))) {
				files.push(fullPath);
			}
		}
	};
	walk(dir);
	return files;
}

function extractIconNames(content) {
	const icons = new Set();
	const patterns = [
		/icon=["']([a-z0-9-]+:[a-z0-9-]+)["']/gi,
		/icon=\{[`"']([a-z0-9-]+:[a-z0-9-]+)[`"']\}/gi,
		/getIconSvg\(["']([a-z0-9-]+:[a-z0-9-]+)["']\)/gi,
		/hasIcon\(["']([a-z0-9-]+:[a-z0-9-]+)["']\)/gi,
	];
	for (const pattern of patterns) {
		let match;
		while ((match = pattern.exec(content)) !== null) {
			icons.add(match[1]);
		}
	}
	return icons;
}

function loadIconSet(prefix) {
	if (iconSetCache.has(prefix)) {
		return iconSetCache.get(prefix);
	}
	const packageName = ICON_SETS[prefix];
	if (!packageName) {
		console.warn(`Unknown icon set: ${prefix}`);
		return null;
	}
	try {
		const iconSetPath = join(ROOT_DIR, "node_modules", packageName, "icons.json");
		const data = JSON.parse(readFileSync(iconSetPath, "utf-8"));
		iconSetCache.set(prefix, data);
		return data;
	} catch (error) {
		console.warn(`Cannot load icon set ${packageName}: ${error.message}`);
		return null;
	}
}

function renderIcon(iconName) {
	const [prefix, name] = iconName.split(":");
	if (!prefix || !name) {
		console.warn(`Invalid icon name: ${iconName}`);
		return null;
	}
	const iconSet = loadIconSet(prefix);
	if (!iconSet) {
		return null;
	}
	const iconData = getIconData(iconSet, name);
	if (!iconData) {
		console.warn(`Icon not found: ${iconName}`);
		return null;
	}
	const renderData = iconToSVG(iconData, { height: "1em", width: "1em" });
	let svg = iconToHTML(replaceIDs(renderData.body), renderData.attributes);
	if (!svg.includes("currentColor")) {
		svg = svg.replace("<svg", '<svg fill="currentColor"');
	}
	return svg;
}

function generateIconsFile(iconsMap) {
	const iconEntries = Array.from(iconsMap.entries())
		.sort(([a], [b]) => a.localeCompare(b))
		.map(([name, svg]) => `\t"${name}":\n\t\t'${svg.replace(/'/g, "\\'")}'`)
		.join(",\n");

	return `/**
 * Auto-generated icon data.
 * Generated by scripts/generate-icons.js during the build.
 * Do not edit by hand.
 */

const iconSvgData: Record<string, string> = {
${iconEntries}
};

export function getIconSvg(iconName: string): string {
	return iconSvgData[iconName] || "";
}

export function hasIcon(iconName: string): boolean {
	return iconName in iconSvgData;
}

export function getAvailableIcons(): string[] {
	return Object.keys(iconSvgData);
}

export default iconSvgData;
`;
}

async function main() {
	console.log("Scanning Svelte files for icons...");
	const files = getAllFiles(SRC_DIR);
	const allIcons = new Set(EXTRA_ICONS);

	for (const file of files) {
		if (file.endsWith("icons.ts")) {
			continue;
		}
		const content = readFileSync(file, "utf-8");
		for (const icon of extractIconNames(content)) {
			allIcons.add(icon);
		}
	}

	console.log(`Found ${allIcons.size} unique icons.`);
	const iconsMap = new Map();
	for (const iconName of allIcons) {
		const svg = renderIcon(iconName);
		if (svg) {
			iconsMap.set(iconName, svg);
		}
	}

	const output = generateIconsFile(iconsMap);
	writeFileSync(OUTPUT_FILE, output, "utf-8");
	console.log(
		`Wrote ${iconsMap.size} icons to ${OUTPUT_FILE} (${(
			Buffer.byteLength(output, "utf-8") / 1024
		).toFixed(2)} KB).`,
	);
}

main().catch((error) => {
	console.error(error);
	process.exit(1);
});
