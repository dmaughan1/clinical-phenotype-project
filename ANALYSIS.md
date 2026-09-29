# ANALYSIS — answering the Module 1 questions

This is the "observe" half of the project. For each of the five original questions it names the
executable evidence, states what the current example model supports, and is honest about where the
model runs out. Numbers below are for the dogfooded T2DM example; the queries, not the numbers, are
the deliverable.

**Scope note.** Absence findings ("no X recorded") are closed-world over the analysis scope, even
though the ontology itself is open-world. They are run against the description **bundle**, which
imports every peer description; against a single leaf description they would under-report. Where I
say "none in scope" I mean exactly that.

**A standing limitation.** Everything here reports what the *model* says, not what is *clinically
true*. A green matrix, a fully-realized phenotype, and a complete audit trail establish modeled
completeness. They do not establish that the phenotype is the medically correct definition, that a
SNOMED/LOINC code is the right code, or that a patient record is accurate. `consistent → valid →
complete` is not `correct`.

---

## Q1 — Is every intended criterion realized, or was intent silently dropped?

**Evidence.** Dashboard → *Coverage of intent* table and Gaps → *dropped intent* table. Both list
`IntendedCriterion`s with no `implements` edge pointing at them (`FILTER NOT EXISTS`). The
`RepresentedIntent` defined concept reaches the same conclusion by classification.

**Finding.** One intended criterion is unrealized in the example: *"Patient is currently on
metformin therapy."* The other four intents each have an implementing computable criterion. So the
question is **answerable and currently shows one dropped criterion** — exactly the kind of silent
loss the methodology is built to surface. Limitation: this proves the intent has no *model* link,
not that the drop was a mistake; withdrawing an intent is legitimate, and the model does not record
that decision.

## Q2 — What cannot be evaluated with available data and terminology?

**Evidence.** Gaps → *unmapped concepts* (concepts with no `mappedTo`) and *criteria that cannot
run* (computable criteria with no concept→element→dataset path in any dataset). The `MappedConcept`
defined concept classifies the mappable ones.

**Finding.** `EgfrMeasurement` is unmapped, and the criterion `eGFR < 60` that depends on it cannot
run in any dataset. Everything else has a data path in at least one dataset. So the question is
**answerable**: the model pinpoints both the unevaluable concept and the criterion it sinks.
Limitation: "unmapped" is a modeling fact; the concept may be perfectly evaluable in reality once
someone records the mapping.

## Q3 — Which mappings change across datasets or terminology versions, and what happens to the cohort?

**Evidence.** Dashboard → *Evaluability across datasets* matrix. The row × column population is all
criteria × all datasets, with `COALESCE(?n, 0)` so an unavailable path is an explicit `0`, not a
missing row.

**Finding (dataset dimension — answerable at the criterion level).** `HbA1c ≥ 6.5%` is evaluable at
the EHR site (Site A) and **not** at the claims site (Site B), which has no lab values; the
diagnosis and exclusion criteria are evaluable at both. The denominator is fixed (every criterion ×
every dataset), so the zeros are real coverage gaps, not an artifact of missing rows. This
establishes *which criteria stop mapping* per dataset — the first half of the question.

**Partial cohort effect — what the model does and does not establish.** For the *effect on the
cohort* I can only go as far as the recorded evidence. The model shows that patient P0003's *only*
supporting evaluation is through `HbA1c ≥ 6.5%` (P0003 has no diagnosis-code evaluation), and that
this criterion has no data path at Site B. So the model establishes that **the sole criterion
supporting P0003's inclusion cannot be evaluated at Site B**. It does **not** establish that "P0003
is in the Site A cohort but not the Site B cohort," because the model does not represent
dataset-specific cohort executions and does not derive inclusion membership at all — there is a
single `Cohort` individual and inclusion is adjudicated by hand, not computed per dataset.

**Diagnosed gap (pattern/vocabulary).** To turn "the supporting criterion is unavailable at Site B"
into "P0003 is absent from the Site B cohort" the methodology would need to model a cohort
*execution* against a specific dataset — i.e., a cohort tied to a `Dataset`, with membership derived
from evaluations whose criteria are `evaluableIn` that dataset. That machinery does not exist here,
so the dataset-specific cohort-membership claim is out of reach and is reported as a gap rather than
asserted.

**Diagnosed gap (terminology-version dimension).** The methodology records each concept's
`sourceVersion` but has no way to say a mapping is valid in one version and not another, so it
*cannot* answer the version half of Q3 at all. **Gap type: vocabulary/pattern.** Closing it would
mean reifying the mapping (concept → element) with a version and validity window, then a query could
diff evaluability across versions the way the matrix diffs across datasets. Deferred deliberately:
the example has one terminology version, so adding the machinery now would be untestable.

## Q4 — For a patient, which criteria and evidence caused inclusion/exclusion?

**Evidence.** Dashboard → *Why each patient was placed* table (evaluation joined to patient,
criterion, `membershipStatus`, and supporting `Evidence`), and the per-criterion *Patients decided
by it* table in the `criterion-analysis` navigation view. Exclusion membership is derived by the
`CohortExclusion` rule.

**Finding.** Every one of the five evaluations has a recorded decision and supporting evidence: e.g.
P0001 is included via both the HbA1c and diagnosis criteria (HbA1c 7.8%; coded 44054006), P0002 is
excluded via the type-1 criterion (coded 46635009). The question is **answerable with a full audit
trail in scope.** Limitation: the trail shows the recorded rationale, not that the evidence is
factually correct — the model cannot tell a correct code from a miscoded one.

## Q5 — If one criterion changes, what is affected downstream?

**Evidence.** Notebook → *Change impact* (a breadth-first walk carrying hop-distance:
query the edges → compute the walk → render a table and a per-kind bar chart) and Dashboard →
*Traceability backbone* graph.

**Finding.** For `T2dmDx`, the walk reaches 9 downstream elements: the concept it uses (1 hop), that
concept's data element (2) and datasets (3), a narrower concept beneath it (2), the two patients it
placed and their evidence (1). So the question is **answerable as a reachable set with distances.**
Important limitation, stated in the view: reachability means *potentially affected* — a reviewer
should re-check these — not that each one's clinical meaning necessarily changes. "Other criteria
affected" is empty here because no two criteria share a concept in the example; that is a finding
about this data, not a guarantee.

---

## Orphan / missing-relationship checks (one per pattern)

Implemented on the Gaps page; each returns which elements fail, with context, and the prose gives
the corrective action. Verified that each query *can* expose absence by removing the relevant
triples in a scratch copy and confirming the rows appear.

| Pattern | Check | Result in scope |
|---|---|---|
| Intent | intended criteria not implemented | 1 (metformin) |
| Realization | computable criteria with no data path | 1 (eGFR) |
| Mapping (terminology) | concepts with no `mappedTo` | 1 (eGFR concept) |
| Mapping (data) | data elements in no dataset | 0 |
| Adjudication | evaluations with no evidence | 0 |

The zeros are genuine "clean in scope" findings, not vacuous: the same queries return the orphans
immediately when a link is deleted.

## Coverage analysis

The evaluability matrix (Q3) is the coverage view, built the safe way: the criterion × dataset
population is constructed first and actual data paths are counted into it with `COALESCE(..., 0)`,
so a criterion that maps nowhere shows a row of zeros instead of disappearing. The denominator
(every criterion, every dataset) is explicit, so the matrix cannot look "100% covered" by dropping
the failures.

## Computed analysis

The change-impact walk (Q5) is the script-based analysis. It is not a count SPARQL could do: it is
a breadth-first traversal over a heterogeneous, multi-predicate edge set that carries hop-distance
and groups results by role. SPARQL pulls the edges (graph-aware selection); Python does the walk
and the aggregation (algorithmic computation); matplotlib renders it. The derived distances are
kept in the view and not written back into the ontology, so they cannot go stale.

## Reusable view template

`criterion-analysis` is a `navigation` template matched to `ComputableCriterion`. Opening any
criterion runs the same four-part read-out (logic, concepts + mapping status, evaluability per
dataset, patients decided) — one template, reused across all four computable criteria with no
copying. The editor and dashboard/gaps templates are `compose` templates reused the same way: the
methodology owns the logic, each project page supplies only an `ontology` context, so a second
phenotype project would reuse them unchanged.
