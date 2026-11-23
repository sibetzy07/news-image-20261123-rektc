// Entry point for the news-image-20261123 make.fun bounty.
//
// Runs draw.py (pure Python standard library, no network) which paints the
// front page of "The World in One Day" for Monday 23 November 2026 and
// writes a deterministic 1024x1024 PNG to the output directory.
//
// Output directory: $MAKEFUN_OUTPUT_DIR, or /output by default. The
// directory is created if missing; nothing is ever deleted.
import { spawnSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";

mkdirSync(outDir, { recursive: true });

const result = spawnSync("python3", [join(here, "draw.py"), outDir], {
  stdio: "inherit",
});

if (result.error) {
  console.error("draw.py failed to start:", result.error);
  process.exit(1);
}
if (result.status !== 0) {
  console.error(`draw.py exited with status ${result.status}`);
  process.exit(result.status ?? 1);
}
console.log(`entry.png written to ${outDir}`);
