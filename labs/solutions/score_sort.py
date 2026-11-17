# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scores a sort of the eight transcripts (lab 1.2) against the key.

  uv run labs/solutions/score_sort.py <sort_sheet.csv>

One point for the side and one for the pattern of each transcript; the written reason is read by
the facilitator. Exit code 0 at the pass mark or above, 1 below it.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

KEY = json.loads((Path(__file__).parent / "key.json").read_text(encoding="utf-8"))


def norm_side(s: str) -> str:
    s = s.strip()
    return "يبني" if s.startswith("يبني") else "يحل" if s.startswith("يحل") else s


def norm_pattern(s: str) -> str:
    s = s.strip()
    return "هـ" if s in ("ه", "هـ") else s


def score(path: Path) -> tuple[int, list[str]]:
    rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))[1:]
    got = {r[0].strip(): r for r in rows if r and r[0].strip()}
    total, notes = 0, []
    for tid, k in KEY["transcripts"].items():
        r = (got.get(tid, [tid]) + ["", "", ""])[:4]
        side_ok = norm_side(r[1]) == k["side"]
        pattern_ok = norm_pattern(r[2]) == k["pattern"]
        total += side_ok + pattern_ok
        if not (side_ok and pattern_ok):
            notes.append(f"{tid}: side {'ok' if side_ok else 'no'}, pattern {'ok' if pattern_ok else 'no'}"
                         f" (key: {k['side']}, {k['pattern']} {k['pattern_name']})")
        if not r[3].strip():
            notes.append(f"{tid}: no reason written")
    return total, notes


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    total, notes = score(Path(sys.argv[1]))
    s = KEY["sort_scoring"]
    for n in notes:
        print(n)
    print(f"score {total}/{s['max']} (pass {s['pass']}): {'PASS' if total >= s['pass'] else 'BELOW'}")
    return 0 if total >= s["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
