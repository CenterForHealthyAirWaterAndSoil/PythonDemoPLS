#!/usr/bin/env python3
"""Offline course demonstration. Python 3.10+; standard library only.

Uses the original pilot's AI-authored records and unchanged rule function.
Does not read publications, invoke AI, or validate scientific judgments.
The counterfactual is a synthetic input edit, not a revised paper assessment.
"""
from __future__ import annotations
import argparse
import copy
import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from run_pilot import assign_indicator, execute


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "course_results")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        papers = json.loads((root / "papers.json").read_text(encoding="utf-8"))
        by_id = {p["paper_id"]: p for p in papers}
        baseline = by_id["S02"]
        baseline_input = copy.deepcopy(baseline["inputs"])
        lines = ["OFFLINE TEACHING REPLAY — NOT SCIENTIFIC VALIDATION", "",
                 "STEP 1: Load the original AI-authored records.",
                 f"Publications: {len(papers)}", "",
                 "STEP 2: Inspect the exact acrolein question.", baseline["index_question"], "",
                 "STEP 3: Apply the original rules to S02.",
                 str(assign_indicator(baseline_input)), "",
                 "STEP 4: Hypothetical edit: temporality becomes uncertain."]
        changed = copy.deepcopy(baseline_input)
        changed["temporality"] = "uncertain"
        lines += [str(assign_indicator(changed)), "Original input unchanged: " + str(baseline["inputs"] == baseline_input), "",
                  "STEP 5: Replay all ten publications."]
        for p in papers:
            label, rule = assign_indicator(p["inputs"])
            lines.append(f"{p['paper_id']} | {p['short_citation']} | {label} | {rule}")
        with redirect_stdout(StringIO()):  # execute() prints its own JSON summary; hide it here
            summary = execute(root, args.out)
        lines += ["", "STEP 6: Inspect the test results.",
                  f"Computational checks: {summary['tests_passed']}/{summary['tests_total']} passed",
                  "Scientific accuracy estimated: " + str(summary["scientific_accuracy_estimated"]),
                  "Expert review performed: " + str(summary["expert_review_performed"]),
                  "Source semantics automatically verified: " + str(summary["source_semantics_automatically_verified"]),
                  "", "These checks concern records and rules. They are not 100% scientific accuracy."]
        text = "\n".join(lines) + "\n"
        (args.out / "teaching_replay.txt").write_text(text, encoding="utf-8")
        print(text)
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError) as exc:
        print(f"Course demo failed: {exc}. Check that the original JSON and run_pilot.py files are present.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
