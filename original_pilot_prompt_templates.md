# Reusable workflow templates

These are operational templates for a subsequent implementation, not a verbatim log of the interactive session that produced this pilot.

## 1. Eligibility and index question
Read the supplied original publication and available supplements. Identify the population, airborne chemical or mixture, measured health outcome, comparator, exposure window and outcome window. Distinguish direct air measurement, modeled air exposure and biomarker-only evidence. Do not infer an environmental pathway from a biomarker alone. Record source locations. Select the stated primary objective; if multiple chemicals/lags remain, describe the illustrative selection and do not call it prespecified. Abstain when essential material is unavailable or the paper lacks an observed exposure–health analysis.

## 2. Evidence extraction
Populate the papers.json schema with source-linked paraphrases. Keep reported observations separate from AI interpretations. Extract the effect metric, exposure increment, adjustment set, interval type and analysis-specific sample. Do not convert an odds ratio into a risk ratio, treat ranges as confidence intervals, or turn P>0.05 into equivalence. Keep correlated chemical groups distinct from isolated species. Note corrections and source discrepancies without silently repairing them.

## 3. Hill-informed assessment
For strength, consistency, specificity, temporality, biological gradient, plausibility, coherence, experiment and analogy, choose one allowed status and explain its basis with evidence IDs. Use external_unverified for background not independently assessed. Within-dataset sensitivity analyses are not independent replication. Explain temporal ordering for the exact question, not just the design label. Evaluate controls and important alternative explanations in relation to that question. Fill all decision inputs and their rationales. Do not produce a raw 100-point score.

## 4. Rules and summary
Apply the versioned deterministic rules, not a freely chosen final label. Produce a plain-language summary preserving population, exposure route, outcome, direction and uncertainty. Pair the label with supports, main limitation and scope. For null results, label causal interpretability of the observed finding and explicitly avoid a safety/equivalence claim. Add the research disclosure.

## 5. Same-system audit (not independent validation)
Recheck the exact estimate, exposure increment, uncertainty level and outcome definition against the specified source. Confirm that every pointer is resolvable. Check whether table totals, corrections, shared samples or model definitions alter interpretation. Preserve unresolved discrepancies. Record substantive changes. Do not label this audit expert validation or an independent model comparison.
