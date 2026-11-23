// Entry point for the news-image-20261123 make.fun bounty.
//
// Copies the pre-rendered front page of "The World in One Day" for
// Monday 23 November 2026 (entry.png, 1024x1024, committed in this repo)
// into the output directory. Pure Node, no subprocess, no network, so it
// runs in the grader's node image, which has no python.
//
// Output directory: $MAKEFUN_OUTPUT_DIR, or /output by default. The
// directory is created if missing; nothing is ever deleted.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log(`entry.png written to ${outDir}`);
