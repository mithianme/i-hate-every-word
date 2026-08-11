<div align="center">

<img src="banner.svg" alt="i hate every word" width="100%">

<br>

**a bot that hates every word in the english dictionary.**<br>
one word at a time, alphabetical order, no exceptions.

[![live on x](https://img.shields.io/badge/live-@hateeverywords-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/hateeverywords)
[![posting](https://github.com/mithianme/i-hate-every-word/actions/workflows/post.yml/badge.svg)](https://github.com/mithianme/i-hate-every-word/actions/workflows/post.yml)
[![licence](https://img.shields.io/badge/licence-MIT-blue)](LICENSE)
[![words](https://img.shields.io/badge/words-370,105-lightgrey)](words.txt)

</div>

---

```
i hate a
i hate aa
i hate aaa
i hate aah
i hate aahed
```

it started at `a`. it posts one word every 30 minutes. it will not stop until
it reaches `zzz`, some time around 2047.

<div align="center">

| | |
|--:|:--|
| **words** | 370,105 |
| **cadence** | one every 30 minutes |
| **started** | august 2026 |
| **finishes** | ~2047 |

</div>

---

## how it works

three files do the work:

| file | what it's for |
|---|---|
| `words.txt` | the dictionary, alphabetical, 370,105 entries |
| `state.txt` | how far through it is — a single number |
| `banned.txt` | words it skips |

`bot.py` reads the next word, posts it, writes its new position, sleeps. that
is the entire program.

progress survives everything. stop it, reboot, unplug the machine — it picks
up on the exact word it left off on. if the state file ever falls behind what
has actually been posted, the duplicate is caught and skipped rather than
posted twice.

<details>
<summary><b>why there's a banned list</b></summary>

<br>

the dictionary contains everything, and "everything" includes words that would
get the account suspended somewhere in the b's. `banned.txt` is slurs and abuse
vocabulary, nothing else — the swearing stays in, and the bot will get to all
of it eventually. plain list, one word per line.

</details>

## running your own

<details>
<summary><b>hosted — github actions, free</b></summary>

<br>

`.github/workflows/post.yml` runs the bot on a schedule and commits the new
position back to the repo. no server, nothing to leave switched on.

1. fork this repo
2. **settings → secrets and variables → actions**, add four secrets:
   `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`
3. set `state.txt` to `0`
4. **actions → post → run workflow** to test

keep the fork public — public repos get unlimited actions minutes. scheduled
workflows also get paused after 60 days without human activity in the repo,
and the bot's own commits don't count.

</details>

<details>
<summary><b>locally</b></summary>

<br>

```bash
cp keys.env.example keys.env   # then fill it in
pip install -r requirements.txt
python bot.py --loop
```

windows: double-click `run.bat`. either way it posts one word immediately,
then one every `LOOP_INTERVAL` seconds. that and the message format are the
first few lines of `bot.py`.

</details>

<details>
<summary><b>the api bit</b></summary>

<br>

you need an X developer account with **read and write** app permissions, and
the four **OAuth 1.0** values — consumer key + secret, access token + secret.
the OAuth 2.0 client id and secret further down that page are a different auth
flow and will fail with a 401.

pay-per-use billing applies. a text post is $0.015, so this cadence runs about
$22/month. set a spending cap in the developer console before leaving it
running.

> [!WARNING]
> **keep links out of the message format.** a post containing a url bills at
> $0.20 instead of $0.015 — thirteen times the price, on every post, forever.

</details>

---

<div align="center">
<sub>MIT · <code>keys.env</code> is gitignored and should stay that way</sub>
</div>
