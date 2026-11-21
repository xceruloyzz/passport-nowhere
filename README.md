# The Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/xceruloyzz/passport-nowhere/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/xceruloyzz/passport-nowhere/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

One open passport spread for a country that does not exist: the
**Republic of Valtoria** (Republika Valtorija), a small Adriatic
republic with its capital at Mirenna. The data page belongs to Mara
Elena Kovac, born 14 March 1994 in Mirenna; the visa pages carry her
travel history — two trips in 2024, to the neighbouring Dravnia in
May and to Croatia in September — plus a Kingdom of Ostara visa
sticker with its condition stamp.

## What is on the spread

**Data page (left).** Coat of arms, bilingual field labels
(Valtorian / English), a stylised procedural portrait, passport
number VT 4829137, issued 12 February 2024 in Mirenna, expiring
12 February 2034, the holder's signature, an "Issued at Mirenna"
stamp, and a two-line ICAO machine-readable zone with correct
check digits.

**Visa pages (right).** An Ostara Type-C visa sticker — valid
8 September to 7 December 2024, single entry, up to 90 days,
"NO EMPLOYMENT — NO PUBLIC FUNDS", fee paid 45 VTD — and eight
round border stamps in chronological order, each entry matched
with its exit: Valtoria → Dravnia → Valtoria (3–17 May 2024),
then Valtoria → Croatia → Valtoria (8–21 September 2024). No
stamp predates the passport's issue, and every date falls inside
its validity.

## How it works

`tools/generate_passport.py` draws the spread with Pillow. All of
the document's data is written into that file, and the program
uses no network, no clock and no randomness (the paper grain uses
a fixed seed), so every run produces the same image. It draws the
two cream pages on a dark desk, the header and bilingual fields,
the flat-illustration portrait, the MRZ with ICAO check digits,
the visa sticker, and eight rotated translucent border stamps.

`main.py` (Python 3.13) renders the spread with that script and
writes it to the grading output folder; if Pillow is unavailable
it falls back to the identical image committed as `entry.png`.

## How to run it

```sh
python3 tools/generate_passport.py   # redraw entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # render it to out/entry.png
```

The output image is exactly 1024×724 pixels and under 1 MiB.

## make.fun

This is an entry for the make.fun bounty
[the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318):
"The Passport Page of a Country That Isn't There". Prizes total
$50, shared by the 20 highest-ranked entries.

Built for make.fun — https://make.fun/?ref=ztsmgxnm
