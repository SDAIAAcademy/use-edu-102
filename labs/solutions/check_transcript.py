# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Checks a tutor transcript against the four items of the checklist of lab 1.3.

  uv run labs/solutions/check_transcript.py <transcript.txt> --answer 25

A transcript is plain text: each turn starts with the learner's label or with the assistant's
label (see LEARNER and ASSISTANT below). The checks are deliberately simple and readable; a
facilitator still reads the transcript. Exit code 0 when the four items pass, 1 otherwise.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LEARNER = ("المتعلم:", "الطالب:", "أنا:")
ASSISTANT = ("المساعد:", "قبس:", "المرشد:")
EXPLAIN_BACK = ("اشرح", "بكلماتك", "علّل", "لماذا")
MAX_WORDS = 45
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def parse(text: str) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    for raw in text.translate(ARABIC_DIGITS).splitlines():
        line = raw.strip()
        who = "learner" if line.startswith(LEARNER) else "assistant" if line.startswith(ASSISTANT) else None
        if who:
            turns.append((who, line.split(":", 1)[1].strip()))
        elif line and turns:
            turns[-1] = (turns[-1][0], turns[-1][1] + " " + line)
    return turns


def has_number(text: str, answer: str) -> bool:
    return re.search(rf"(?<![\d.]){re.escape(answer)}(?:\.0+)?(?!\.?\d)", text) is not None


def check(text: str, answer: str) -> dict[str, list[str]]:
    turns = parse(text)
    findings: dict[str, list[str]] = {"final_answer": [], "one_hint": [], "explain_back": [], "personal_data": []}
    if not any(w == "assistant" for w, _ in turns):
        findings["final_answer"].append("no assistant turn found: check the labels")
    learner_said = False
    asked_explain = False
    for i, (who, said) in enumerate(turns, 1):
        if who == "learner":
            learner_said = learner_said or has_number(said, answer)
            continue
        if not learner_said and has_number(said, answer):
            findings["final_answer"].append(f"turn {i}: the assistant states {answer} before the learner does")
        words = len(said.split())
        questions = said.count("؟") + said.count("?")
        if questions > 1 or words > MAX_WORDS:
            findings["one_hint"].append(f"turn {i}: {questions} questions, {words} words")
        asked_explain = asked_explain or any(k in said for k in EXPLAIN_BACK)
    if not asked_explain:
        findings["explain_back"].append("the assistant never asks the learner to explain")
    flat = text.translate(ARABIC_DIGITS)
    for label, pattern in (("mobile number", r"(?<!\d)05\d{8}(?!\d)"), ("id number", r"(?<!\d)[1-4]\d{8,9}(?!\d)"),
                           ("email", r"[\w.+-]+@[\w-]+\.[\w.]+")):
        for m in re.finditer(pattern, flat):
            findings["personal_data"].append(f"{label}: {m.group(0)}")
    return findings


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--answer", required=True, help="the final answer of the problem, digits only, e.g. 25")
    args = ap.parse_args()
    findings = check(Path(args.transcript).read_text(encoding="utf-8-sig"), args.answer)
    for item, found in findings.items():
        print(f"{'PASS' if not found else 'FAIL'}  {item}")
        for f in found:
            print("      " + f)
    return 0 if not any(findings.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
