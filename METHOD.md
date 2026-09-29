# METHOD — Clinical Phenotyping Methodology

This is the "method" half of the project: what a user of this methodology is expected to model, in
what order, and why. The vocabulary (`src/method/oml`) defines the terms; this document says how to
use them. The running T2DM example under `src/model` is the method applied to itself (dogfooding).

The methodology exists to keep one thing honest: the chain from a researcher's plain-language
phenotype down to the data that decides who is in the cohort. Each of the four patterns below
records one link in that chain so that the Module 1 questions have something concrete to check.

## What the method prescribes

Author a phenotype in four recurring acts, each with its own editor page under
*T2DM Phenotype / Authoring*. The editors are SHACL shapes (see `src/method/md/.../*.md`); each
carries a small constraint that flags the one omission that would break the pattern.

### Pattern 1 — Intent (`intent.md`)
Write the phenotype's criteria in prose first, as `IntendedCriterion`s attached to the `Phenotype`
via `partOf`. **Use it** at the very start, before any code. **Why first:** intent is the baseline
that Question 1 ("was anything dropped?") compares against; if intent is never written down, a drop
cannot be detected. **Constraint:** every intended criterion must have intent text.

### Pattern 2 — Realization (`realization.md`)
Turn each intent into a computable inclusion/exclusion criterion that `implements` the intent and
`dependsOnConcept` the terminology it tests. **Use it** once the intent is stable. **Why:** the
`implements` edge is the join that makes drop-detection possible, and `dependsOnConcept` is what
later tells us whether the criterion can actually run. **Constraint:** every computable criterion
must implement at least one intended criterion.

### Pattern 3 — Terminology & Data (`terminology.md`, `datasets.md`)
Record the `ClinicalConcept`s in their is-a hierarchy with codes and a mapping status, bind them to
`DataElement`s via `mappedTo`, and declare which `Dataset`s provide each element via `availableIn`.
**Use it** as criteria are realized and as datasets are onboarded. **Why:** this is the half of the
model Questions 2 and 3 turn on — an unmapped concept cannot be evaluated, and an element absent
from a dataset means the criterion cannot run there. **Constraints:** every concept records a
mapping status; every data element is available in at least one dataset.

### Pattern 4 — Adjudication (`adjudication.md`)
Record each patient's `Evaluation` against a criterion (with a `membershipStatus`) and the
`Evidence` that `supports` it. **Use it** when the phenotype is run against real records. **Why:**
this is what makes Question 4 answerable — a reviewer can see *why* a patient was placed.
**Constraint:** every piece of evidence must support an evaluation.

## Description organization and rationale

Descriptions are split by *who owns the content and when it changes*, not by convenience:

| File | Pattern | Owner / lifecycle |
|---|---|---|
| `definition.oml` | 1 & 2 | the researcher/clinician; changes per study |
| `terminology.oml` | 3 | the informatician; changes with terminology versions |
| `data.oml` | 3 | the data steward; changes per institution |
| `cohort.oml` | 4 | per run of the phenotype against a dataset |

Keeping terminology and data separate from the definition means a site can swap datasets, or a
terminology version can move, without touching the researcher's phenotype — and the analysis layer
can still join across them through the bundle. The alternative (one file per phenotype) was
rejected because it couples authorship that in practice belongs to different people and moves on
different clocks.

## Editor workflow and reuse

Each pattern's editor lives once, in the method, as a `compose` template. Project pages under
*Authoring* are three lines each: they set an `ontology` context and compose the template. The same
templates would serve any other phenotype project unchanged — the methodology owns the authoring
logic; a project only supplies context. This is the intended reuse: shapes are written once and
dogfooded here against the T2DM example (26 concept instances plus 5 reified evaluations, all
conforming to the editor shapes).

## Business rules

Two derivation rules live in the vocabulary because they encode methodology decisions, not project
data:

- **`CohortExclusion`** derives `excludedFrom(patient, cohort)` when a patient satisfies an
  *exclusion* criterion of the phenotype. It exists because exclusion is monotone — meeting any one
  exclusion criterion is sufficient — so it is safe to derive, unlike inclusion (which is
  conjunctive over all criteria and is therefore *not* auto-derived here on purpose). Keeping this
  in the method means no one hand-maintains exclusion lists.
- **`CriterionEvaluable`** derives `evaluableIn(criterion, dataset)` when the criterion's concept
  has a data element the dataset provides. It turns the "can this run here?" question into a fact
  the analysis layer and the per-criterion view can read directly.

The editors add prescriptive `sh:sparql` constraints (the per-pattern rules above). Those *enforce*
authoring; the two OML rules *derive* new facts. Both belong to the method so that every project
gets the same behavior.

## Alternatives, uncertainty, open issues

- **Inclusion not derived.** I deliberately did not write a rule that adds a patient to the cohort
  from a single satisfied inclusion criterion — that would be wrong, since inclusion needs *all*
  criteria and no exclusions. Cohort membership is left to be adjudicated and recorded, not
  inferred from one link. This is a modeling choice, not an oversight.
- **Inclusion/exclusion as subtypes, not a flag.** A criterion's polarity is its type
  (`InclusionCriterion` / `ExclusionCriterion`) rather than a property, so the reasoner enforces
  disjointness. The cost is that the realization editor targets the parent type; choosing the
  concrete subtype is a small manual step.
- **Terminology-version drift is not modeled.** Concepts record a `sourceVersion`, but the pattern
  does not represent a mapping that is valid in one version and not another. So Question 3 is only
  half-answerable: the *dataset* dimension is computable, the *terminology-version* dimension is a
  diagnosed gap (see ANALYSIS.md). Closing it would mean reifying the mapping with a version and
  validity — deferred because the example has a single version and I did not want to add machinery
  the questions here cannot yet exercise.
- **Relation-entity editing.** `Evaluation` is a reified relation authored in OML and shown as a
  graph; the adjudication editor edits patients and evidence but not the evaluation endpoints
  directly, which is a limitation of table-editing reified relations rather than a modeling choice.
