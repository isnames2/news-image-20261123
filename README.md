[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261123)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

# The World in One Day — Monday, 23 November 2026

A program that draws one image summing up the world news of Monday,
23 November 2026, for the make.fun bounty
[news-image-20261123](https://make.fun/bounty/news-image-20261123).

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024×1024 PNG, under 1 MiB). No network.
Run it twice and the bytes are identical: fixed layout, no randomness,
no clock.

## The six stories

1. **Climate** — COP31 ends with no deal: talks in Antalya collapse after
   the EU and about 130 nations reject a text with no fossil-fuel
   phase-out.
2. **War in Ukraine** — 10 dead in Kyiv region: a Russian strike on Dymer
   kills at least 10; rescuers pull a boy alive from the rubble.
3. **Markets** — Markets slide on AI fears: Nikkei falls 5.06% and the
   S&P 500 drops 3.7%.
4. **U.S. politics** — Democrats win big in the House: 258 seats, the
   largest US House majority since 1992.
5. **Disaster** — 24 dead in a factory fire: a candy factory blaze in
   Serang, Indonesia; dozens of workers still missing.
6. **Crime** — Mexico captures 'El Chapo Isidro': the FBI most-wanted
   drug lord is seized in a deadly Sinaloa firefight.

## How it is drawn

`main.py` draws the whole page with Pillow: a navy masthead naming the
day, six stories in a 2×3 grid, each with a pictogram drawn from
primitives, a kicker, a headline and a short summary. Fonts are bundled
in `fonts/` (DejaVu Sans, freely licensed) so the image renders the same
wherever it runs.
