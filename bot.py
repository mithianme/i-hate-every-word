"""i hate every word — posts "i hate {word}" for every word in words.txt, one per hour."""
import os
import re
import sys
import time

import tweepy

WORDS_FILE = "words.txt"
STATE_FILE = "state.txt"
BANNED_FILE = "banned.txt"
KEYS_FILE = "keys.env"
LOOP_INTERVAL = 30 * 60  # seconds between posts
RETRY_WAIT = 60          # wait after an error (no internet, X down, etc.)

NEEDED = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]


def load_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def load_keys():
    """Reads the four API keys from keys.env (env vars override if set)."""
    keys = {}
    for line in load_lines(KEYS_FILE):
        if line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        keys[name.strip()] = value.strip().strip('"').strip("'")
    for name in NEEDED:
        if os.environ.get(name):
            keys[name] = os.environ[name]
    missing = [n for n in NEEDED if not keys.get(n) or "paste" in keys.get(n, "").lower()]
    if missing:
        print("missing API keys:", ", ".join(missing))
        print(f"copy keys.env.example to {KEYS_FILE} and fill in the values from developer.x.com")
        input("press Enter to close...")
        sys.exit(1)

    # sanity-check key shapes (catches OAuth 2.0 values pasted in by mistake)
    problems = []
    if not re.match(r"^\d+-", keys["X_ACCESS_TOKEN"]):
        problems.append("X_ACCESS_TOKEN should start with a long number then a hyphen")
    for name in NEEDED:
        if ":" in keys[name]:
            problems.append(f"{name} contains ':' — that's an OAuth 2.0 value")
    if problems:
        print("bad keys in keys.env:")
        for p in problems:
            print(" -", p)
        print("use the OAuth 1.0 values (consumer key + access token rows), not OAuth 2.0.")
        input("press Enter to close...")
        sys.exit(1)
    return keys


def get_index():
    lines = load_lines(STATE_FILE)
    return int(lines[0]) if lines else 0


def save_index(i):
    with open(STATE_FILE, "w") as f:
        f.write(f"{i}\n")


def post_next(client):
    """Post the next word. Returns False once the whole list is done."""
    words = load_lines(WORDS_FILE)
    banned = {w.lower() for w in load_lines(BANNED_FILE)}
    i = get_index()

    # skip anything on the banned list
    while i < len(words) and words[i].lower() in banned:
        i += 1

    if i >= len(words):
        print("done. every word has been hated.")
        return False

    text = f"i hate {words[i]}"
    try:
        client.create_tweet(text=text)
    except tweepy.Forbidden as e:
        if "duplicate" in str(e).lower():
            # already posted this one (state didn't save last time) — move on
            print(f"[{i}] already posted, skipping: {text}")
            save_index(i + 1)
            return True
        raise
    except tweepy.TooManyRequests:
        print("rate limited — will retry next cycle")
        return True

    save_index(i + 1)
    print(f"[{i}] posted: {text}")
    return True


def make_client(keys):
    # built fresh for every post — a client reused across a long sleep holds a
    # dead keep-alive socket and the next post fails with a connection reset
    return tweepy.Client(
        consumer_key=keys["X_API_KEY"],
        consumer_secret=keys["X_API_SECRET"],
        access_token=keys["X_ACCESS_TOKEN"],
        access_token_secret=keys["X_ACCESS_TOKEN_SECRET"],
    )


def main():
    keys = load_keys()

    i = get_index()
    total = len(load_lines(WORDS_FILE))
    print(f"i hate every word — at word {i:,} of {total:,}")

    if "--loop" not in sys.argv:
        post_next(make_client(keys))
        return

    mins = LOOP_INTERVAL // 60
    print(f"posting every {mins} minutes while this runs. stop any time; progress is saved.")
    while True:
        try:
            if not post_next(make_client(keys)):
                break
        except tweepy.Unauthorized:
            print("X rejected your keys (401). check keys.env — and make sure the app")
            print("permissions were set to Read and write BEFORE the access token was generated.")
            input("press Enter to close...")
            sys.exit(1)
        except Exception as e:
            print(f"error: {e}")
            print(f"retrying in {RETRY_WAIT // 60} minutes...")
            time.sleep(RETRY_WAIT)
            continue
        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    main()