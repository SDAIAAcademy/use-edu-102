# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Runs every solution of the course and prints PASS or the first difference.

  uv run labs/solutions/run_all.py

Nothing here calls a language model: lab 1.3's transcripts come from stand_in_tutor.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import check_transcript  # noqa: E402
import score_sort  # noqa: E402
import stand_in_tutor  # noqa: E402

KEY = json.loads((HERE / "key.json").read_text(encoding="utf-8"))
FILES = HERE.parent / "files"


def expect(name: str, got, want) -> None:
    if got != want:
        print(f"FAIL  {name}: got {got!r}, expected {want!r}")
        raise SystemExit(1)
    print(f"ok    {name}: {got}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    P = KEY["problems"]
    # Lab 1.1: the answers, recomputed here independently of the generator
    expect("1.1 A", round(96 / 0.80, 1), P["A"]["answer"])
    expect("1.1 A variant", round(204 / 0.85, 1), P["A2"]["answer"])
    expect("1.1 B", round(0.4 * 70 + 0.6 * 85, 1), P["B"]["answer"])
    expect("1.1 B variant", round(0.3 * 80 + 0.7 * 60, 1), P["B2"]["answer"])
    expect("1.1 C, C variant", [round(40 / 160 * 100, 1), round(50 / 250 * 100, 1)], [P["C"]["answer"], P["C2"]["answer"]])
    expect("1.1 D, D variant", [round(200 * 1.1 * 0.9, 1), round(500 * 1.2 * 0.8, 1)], [P["D"]["answer"], P["D2"]["answer"]])
    for name in ("A", "B"):
        text = (FILES / f"qabas_answer_mode_{name}.txt").read_text(encoding="utf-8")
        expect(f"1.1 answer-mode transcript {name} holds the answer", str(int(P[name]["answer"])) in text, True)
    problems = (FILES / "problems.txt").read_text(encoding="utf-8")
    expect("1.1 the problems file holds no answer line", "الإجابة" in problems, False)

    # Lab 1.2: eight transcripts, a full-mark reference sort, and a sort that falls into the planted traps
    expect("1.2 transcripts", sorted(p.stem for p in (FILES / "transcripts").glob("S*.txt")), sorted(KEY["transcripts"]))
    expect("1.2 transcripts that build understanding", [t["side"] for t in KEY["transcripts"].values()].count("يبني"), 4)
    expect("1.2 reference sort", score_sort.score(HERE / "sort_sheet_reference.csv"), (16, []))
    swapped = []
    for line in (HERE / "sort_sheet_reference.csv").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("S4,"):
            line = "S4,يحل,أ,يبدأ بطلب الحل"
        if line.startswith("S8,"):
            line = "S8,يبني,و,يبدأ بسؤال مفاهيمي"
        if line.startswith("S3,"):
            line = "S3,يبني,و,حاول أولًا"
        swapped.append(line)
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "traps.csv"
        f.write_text("\n".join(swapped), encoding="utf-8")
        total, _ = score_sort.score(f)
    expect("1.2 a sort that falls into the three traps (below the pass mark of 12)", total, 10)
    expect("1.2 the blank sheet", score_sort.score(FILES / "sort_sheet.csv")[0], 0)
    pl = KEY["planted"]
    s5 = (FILES / "transcripts" / "S5.txt").read_text(encoding="utf-8")
    expect("1.2 planted figure: printed, and what the count gives",
           (f"| {pl['count']} | {pl['printed_percent']}% |" in s5, round(pl["count"] / pl["total"] * 100)), (True, pl["right_percent"]))

    # Lab 1.3: regenerate both transcripts with the stand-in, compare with the committed ones, check them
    for name, text in stand_in_tutor.reference_transcripts(KEY).items():
        expect(f"1.3 {name} is what the stand-in writes", (HERE / name).read_text(encoding="utf-8") == text, True)
    good = check_transcript.check((HERE / "transcript_reference.txt").read_text(encoding="utf-8"), "25")
    expect("1.3 reference transcript", {k: len(v) for k, v in good.items()},
           {"final_answer": 0, "one_hint": 0, "explain_back": 0, "personal_data": 0})
    bad = check_transcript.check((HERE / "transcript_leaky.txt").read_text(encoding="utf-8"), "25")
    expect("1.3 leaky transcript fails every item", [bool(v) for v in bad.values()], [True, True, True, True])
    expect("1.3 leaky transcript: planted personal data", len(bad["personal_data"]), 2)
    s6 = check_transcript.check((FILES / "transcripts" / "S6.txt").read_text(encoding="utf-8"), "240")
    expect("1.3 the tutor transcript of lab 1.2 (S6) passes too", [bool(v) for v in s6.values()], [False] * 4)
    sol = (HERE / "tutor_instructions_solution.txt").read_text(encoding="utf-8")
    expect("1.3 solution instructions hold the three rules",
           ["تلميحًا واحدًا" in sol, "لا تذكر الإجابة النهائية" in sol, "يشرح بكلماته" in sol], [True, True, True])
    tpl = (FILES / "tutor_instructions_template.txt").read_text(encoding="utf-8")
    expect("1.3 template leaves five lines to write", sum(">> " in line for line in tpl.splitlines()[3:]), 5)
    plan = (HERE / "practice_plan_example.txt").read_text(encoding="utf-8")
    expect("1.3 plan: 14 days, a disclosure line, AI-off first",
           (plan.count("\nاليوم "), "سطر الإفصاح" in plan, plan.count("دون ذكاء اصطناعي") >= 8), (14, True, True))
    print("PASS  all solutions")


if __name__ == "__main__":
    main()
