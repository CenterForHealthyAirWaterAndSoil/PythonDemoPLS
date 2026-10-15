# Python teaching demonstration

The lecture can be taught without participant coding. The supplied notebook contains executed outputs for an offline fallback.

## Simplest route: terminal

Use Python 3.10 or later. No third-party packages or AI credentials are needed.

```bash
cd python_demo
python course_demo.py
```

If `python` is not found, use `python3 course_demo.py` (macOS/Linux) or `py -3 course_demo.py` (Windows).

Expected outputs: S02 → Stronger/R4; hypothetical uncertain timing → Limited/R2; ten publications → seven Limited, two Moderate, one Stronger; 100/100 computational checks passed. The original records are not changed.

## Notebook route

Open `VOC_Causal_Support_Demo.ipynb` in an existing Jupyter environment with `python_demo` as the working folder. Run cells in order. The notebook itself requires a notebook interface; its code imports only the standard library. No installation or cloud upload is required during class.

## Original replay

```bash
python run_pilot.py --out original_replay
```

## What is—and is not—reproduced

Reproduced: deterministic application of the existing rules to the AI-authored records, plus record/rule checks.

Not reproduced: fresh full-text reading, model calls, independent AI assessment, expert judgment, source semantic verification, or reader understanding. The hypothetical edit changes a copied input—not the publication. This is not an unattended PDF-to-summary application.

## Verifying the framework file

`framework_lock.sha256` holds the SHA-256 hash of `framework_v1.json` only. It lets you confirm the rules file is the one recorded after the development-paper review. It is an integrity marker, not evidence of prospective registration. `lock_note.txt` explains this in one line; the note itself is not hashed.

```bash
sha256sum -c framework_lock.sha256        # Linux
shasum -a 256 -c framework_lock.sha256    # macOS
certutil -hashfile framework_v1.json SHA256   # Windows: compare the printed value by eye
```

## Files

- `papers.json`, `sources.json`, `framework_v1.json`, `boundaries.json`, `issues.json`, `run_pilot.py`: original pilot files, unchanged.
- `framework_lock.sha256`, `lock_note.txt`: integrity marker for `framework_v1.json` (see above).
- `original_pilot_prompt_templates.md`: reusable original templates, not a verbatim execution log.
- `course_demo.py`: new offline teaching wrapper.
- `VOC_Causal_Support_Demo.ipynb`: new executed lesson notebook.
- `course_results/`, `notebook_results/`: replay outputs generated during course preparation.
- `executed_demo_output.txt`: text fallback for presenting without a notebook.

Full-text articles are not redistributed here. To obtain lawful access, start from the DOI in `sources.json` (the `canonical_url` field), which resolves to the publisher. The `source_read_url` links were the copies the pilot used (for example PubMed Central, publisher sites, EPA, and some author-uploaded copies on ResearchGate or third-party sites) and may not be freely or lawfully available to every reader. New AI outputs would require preparation in the original schema and review; this lesson does not automatically import arbitrary AI responses.

## Known limitations (useful discussion points)

- **One judgment drives most results.** Six of the ten publications are rated Limited by rule R2 because `temporality` is `uncertain`. That field is an AI judgment.
- **Booleans cannot express "unknown".** Boundary case B01 records `air_route_supported: false`, although its explanation says the route was not adjudicated from the abstract. It still abstains correctly, because `essential_information_complete` is false and rule R1 fires.
- **Some checks cannot fail.** The "deterministic replay" and "title/background cannot bypass gates" checks (20 of the 100) compare a pure function with itself. They document design intent; they do not test scientific validity.
