# The World in One Image — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/ldpapay/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/ldpapay/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Entry for the make.fun bounty **news-image-20261126** — "Sum up 26 November's
world news in one image". See the bounty page:
https://make.fun/bounty/news-image-20261126

## What it is

`main.py` (Python 3, standard library only) draws a 1024×1024 newspaper
front page and writes it to `/output/entry.png`. No network, no external
files, no installed packages. Two runs produce byte-identical output
(46,850 bytes, verified locally).

The page names its day in the masthead — **THURSDAY 26 NOVEMBER 2026** —
and sums up the day in eight illustrated stories plus an "Also today" strip:

| Panel | Story |
| --- | --- |
| Strait of Hormuz | Iran says two tankers hit sea mines off Oman's Khasab port and caught fire; one was a supertanker carrying over 2 million barrels of crude |
| United States | Macy's 100th Thanksgiving Day Parade postponed to Saturday, a first; the storm cuts power to about 900,000 homes and businesses |
| Spain / Europe | Snap election on Sunday; EU leaders pick Hernández de Cos as the next ECB president |
| Ukraine war | Russian strikes kill at least 3 in Kharkiv; Kyiv warns of a new mass strike |
| Gaza diplomacy | Qatar and Egypt meet in Cairo to push the Gaza truce forward |
| Technology | Microsoft outage enters day two in 70+ countries |
| Migration | A record 2,100+ migrants reach the Canary Islands in one day |
| India | Mumbai marks 18 years since the 26/11 attacks |
| Also today | Guinea-Bissau vote delayed to 2028; Jazan refinery hit, 1 killed; NATO over Poland; Tidal drops AI tracks |

Every fact was checked against Reuters, CNN, The Wall Street Journal and
Daily Summary of World reporting from 26 November 2026. Claims are worded
as reported ("Iran says…", "Kyiv warns…") where the source itself attributes
them, and nothing is invented or hyped.

## How the picture is drawn

* A small RGB canvas with rectangle / circle / ellipse / polygon / line
  primitives — every pictogram (tanker, parade balloon, ballot box,
  starburst, dove, monitor, boat, candle) is drawn from shapes.
* Text from a bitmap font baked into `main.py` as one base64 blob
  (`FONT_B64`): Liberation Sans Bold rasterised once at 28 px, 2 bits per
  pixel, so the program needs no font files at run time. The blob is data;
  the drawing, layout and PNG code around it is the program.
* A deterministic PNG writer (zlib level 9, filter 0, fixed chunk order,
  no timestamps anywhere).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, 46,850 bytes)
```

Run it twice and compare: the two files are byte-identical.

## License

MIT — see `LICENSE`.
