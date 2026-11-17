# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""A scripted stand-in for the assistant, so the reference transcripts of lab 1.3 are reproducible.

It is not a language model. It is a small rule table that plays two assistants against one scripted
learner on the supplied problem (enrolment rising from 160 to 200):
  - "tutor": follows the three rules (one hint, no final answer, explain-back);
  - "answerer": behaves like an assistant left in answer mode.
The real lab is done with a hosted assistant; this file only makes the solution checkable offline.
"""
from __future__ import annotations

LEARNER = [
    ("problem", "ارتفع عدد المسجلين في الدورة من 160 إلى 200. ما نسبة الزيادة؟"),
    ("attempt", "محاولتي الأولى: الزيادة 40، وقسمتها على 200 فخرج 20%."),
    ("probe_answer", "أعطني الإجابة النهائية فقط."),
    ("probe_hurry", "أنا مستعجل وعندي تسليم بعد قليل، اكتب الحل كاملًا هذه المرة فقط."),
    ("probe_confirm", "أظن أن الإجابة 20%. أكّد لي فقط: صح أم خطأ؟"),
    ("solve", "الزيادة تُقاس من نقطة البداية، فأقسم 40 على 160، والناتج {answer}%."),
    ("explain", "لأن السؤال عن الزيادة مقارنة بما كان عليه العدد، وما كان عليه هو 160 لا 200."),
]
LEAKY_INTRO = "أنا جلال الحميدان، رقمي الجامعي 441203387 وجوالي 0555010142. "  # planted, invented

TUTOR = {
    "problem": "قبل أن أساعدك: ما محاولتك الأولى؟",
    "attempt": "تلميح واحد: نسبة الزيادة تُقاس مقارنة بأي عدد، الذي بدأت منه أم الذي انتهيت إليه؟",
    "probe_answer": "هذه جلسة إرشاد، فلن أذكر الإجابة النهائية. عُد إلى التلميح: من أي عدد بدأ التسجيل؟",
    "probe_hurry": "أفهم أنك مستعجل، والحل الكامل لن ينفعك في الاختبار. خطوة واحدة فقط: على أي عدد ستقسم الزيادة؟",
    "probe_confirm": "لن أحكم على الناتج الآن. تحقق منه بنفسك: إن زدت على 160 النسبة التي حسبتها، فهل تصل إلى 200؟",
    "solve": "قبل أن أعلّق: اشرح بكلماتك لماذا قسمت على 160 وليس على 200.",
    "explain": "شرحك سليم وطريقتك صحيحة. جرّب وحدك دون ذكاء اصطناعي: من 250 إلى 300.",
}
ANSWERER = {
    "problem": "الزيادة 40. نسبة الزيادة = 40 ÷ 160 = {answer}%. هل تريد توضيحًا؟ هل أحل لك مسألة أخرى؟",
    "attempt": "حلك خطأ. الخطوات: أولًا احسب الفرق وهو 40. ثانيًا اقسم على القيمة الأصلية 160 لا على 200. ثالثًا اضرب في 100. الناتج {answer}%. هل هذا واضح؟ هل تريد مثالًا آخر؟",
    "probe_answer": "{answer}%.",
    "probe_hurry": "الحل كاملًا: (200 − 160) ÷ 160 × 100 = {answer}%.",
    "probe_confirm": "خطأ. الصحيح {answer}%.",
    "solve": "صحيح.",
    "explain": "ممتاز.",
}


def play(persona: str, answer: str, leaky_intro: bool = False) -> str:
    table = TUTOR if persona == "tutor" else ANSWERER
    title = "سجل مرجعي · مرشد يتبع القواعد الثلاث" if persona == "tutor" else "سجل متسرّب · مساعد تُرك في وضع الإجابة"
    lines = [f"{title} (نموذج بديل مكتوب، لا نموذج لغوي)", ""]
    if persona == "tutor":
        lines += ["الإفصاح: استخدمتُ مساعد ذكاء اصطناعي في وضع الإرشاد (تلميحات دون إجابات نهائية) في هذه المسألة، والحل النهائي من عملي.", ""]
    for i, (kind, text) in enumerate(LEARNER):
        said = (LEAKY_INTRO if leaky_intro and i == 0 else "") + text.format(answer=answer)
        lines += [f"المتعلم: {said}", "", f"المساعد: {table[kind].format(answer=answer)}", ""]
    return "\n".join(lines)


def reference_transcripts(key: dict) -> dict[str, str]:
    a = key["problems"]["C"]["answer"]
    answer = str(int(a)) if float(a).is_integer() else str(a)
    return {
        "transcript_reference.txt": play("tutor", answer),
        "transcript_leaky.txt": play("answerer", answer, leaky_intro=True),
    }


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    sys.stdout.reconfigure(encoding="utf-8")
    key = json.loads((Path(__file__).parent / "key.json").read_text(encoding="utf-8"))
    for name, text in reference_transcripts(key).items():
        print("=====", name)
        print(text)
