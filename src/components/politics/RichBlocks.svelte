<script lang="ts">
import type { Block, Tone } from "@/lib/politics/types";

interface Props {
	blocks: Block[];
	colorOnly?: boolean;
	compact?: boolean;
}

let { blocks, colorOnly = false, compact = false }: Props = $props();

const colorTones = new Set<Tone>(["key", "warm", "blue", "purple", "green"]);

function hasColor(block: Block): boolean {
	return block.spans.some((span) => colorTones.has(span.tone));
}
</script>

<div class={`pol-rich ${compact ? "pol-rich-compact" : ""}`}>
	{#each blocks as block, index (index)}
		{#if !colorOnly || hasColor(block)}
			<p class="pol-rich-block">
				{#each block.spans as span, spanIndex (spanIndex)}
					{#if !colorOnly || colorTones.has(span.tone)}
						<span class={`tone-${span.tone}`}>{span.text}</span>
					{/if}
				{/each}
			</p>
		{/if}
	{/each}
</div>
