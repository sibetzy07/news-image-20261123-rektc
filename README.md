# The World in One Day — 23 November 2026

A make.fun entry for the **news-image-20261123** bounty: *"Sum up 23
November's world news in one image."*

The program draws a newspaper front page summing up Monday 23 November
2026 in one image: the COP31 climate talks collapsing in Antalya, the
Ukraine war hitting Kyiv and Russian ships in the Baltic and off Libya, the
Gulf war widening as Iran strikes Bahrain and tankers in the Strait of
Hormuz, the deadly candy-factory fire in Java, South Korea's education
minister resigning over AI exam cheating, and Nepal's prime minister holding
talks with Modi in Delhi — plus a sports/markets ticker.

## How it works

- `main.ts` (Node 22 entry point) runs `draw.py` and writes the image to
  `$MAKEFUN_OUTPUT_DIR` (default `/output`).
- `draw.py` (Python 3, standard library only) paints the whole front page
  from scratch: every illustration is geometric vector art coded by hand,
  and every letter comes from a small 5x7 bitmap font defined in the file.
  No network, no external assets, no fonts on disk.
- Output is a deterministic PNG, exactly 1024x1024, well under 1 MiB.
  Running the program twice produces byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Then check `out/entry.png` (1024x1024 PNG).

## Research

`news-brief.md` records the six stories chosen, with what happened, why each
matters, and the sources (Reuters, BBC, CNN, AP, Al Jazeera, Le Monde and
others, as reported on 23 November 2026).

## License

MIT — see `LICENSE`.
