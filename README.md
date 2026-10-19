# Clinical Phenotyping Ontology (SIE 502 Project Deliverable 2)

[![Release](https://img.shields.io/github/v/release/dmaughan1/clinical-phenotype-project?sort=semver)](https://github.com/dmaughan1/clinical-phenotype-project/releases) [![Live Site](https://img.shields.io/badge/live%20site-GitHub%20Pages-blue)](https://dmaughan1.github.io/clinical-phenotype-project/)

**Live site (v1.0.0):** https://dmaughan1.github.io/clinical-phenotype-project/

An [OML](https://www.modelware.io/) model of the system described in Project Deliverable 1: a tool
that lets a clinical researcher state, in plain language, the patient population they want to
study, and returns the matching records from an authorized clinical dataset â€” while keeping the
whole chain of reasoning explicit, from prose clinical **intent**, through **computable
criteria**, down to **terminology concepts**, **data elements**, **datasets**, and finally the
**patients** and the **cohort** they produce.

The model is deliberately minimal and question-driven: every term exists to help answer one of the
five business questions from Deliverable 1 (see [Business questions](#business-questions)).

## What the system is

* **In scope:** interpreting phenotype intent, representing intended and computable criteria,
  mapping criteria onto terminology concepts and institutional data, identifying matching
  patients, and the traceability among all of these.
* **Out of scope (referenced, not modeled):** collecting the EHR data, judging record accuracy,
  clinical treatment decisions, and the maintenance of SNOMED CT itself (used only as an external
  knowledge source).

## Repository layout

The professor's method/model split is used: the **method** (the vocabulary â€” *how* we describe
phenotypes) is separated from the **model** (the description â€” *a specific* phenotype and its
data).

```
clinical-phenotype-project/
â”œâ”€â”€ .oml/settings.yml                       # sources: src/method and src/model
â”œâ”€â”€ README.md
â”œâ”€â”€ METHOD.md                               # D4: what the methodology prescribes and why
â”œâ”€â”€ ANALYSIS.md                             # D5: each Module 1 question -> evidence -> finding
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ method/
â”‚   â”‚   â”œâ”€â”€ oml/www.example.com/phenotype/
â”‚   â”‚   â”‚   â”œâ”€â”€ vocabulary.oml               # concepts, properties, relations, 2 rules
â”‚   â”‚   â”‚   â””â”€â”€ vocabulary-bundle.oml        # vocabulary bundle -> fires disjointness closure
â”‚   â”‚   â”œâ”€â”€ md/www.example.com/phenotype/    # methodology templates (editors + analysis views)
â”‚   â”‚   â”‚   â”œâ”€â”€ intent.md realization.md     # pattern editors (compose)
â”‚   â”‚   â”‚   â”œâ”€â”€ terminology.md datasets.md
â”‚   â”‚   â”‚   â”œâ”€â”€ adjudication.md
â”‚   â”‚   â”‚   â”œâ”€â”€ dashboard.md gaps.md         # analysis views (compose)
â”‚   â”‚   â”‚   â””â”€â”€ criterion-analysis.md        # per-criterion view (navigation)
â”‚   â”‚   â””â”€â”€ py/utils.py                       # helpers for the notebook
â”‚   â””â”€â”€ model/
â”‚       â”œâ”€â”€ oml/www.example.com/phenotype/description/
â”‚       â”‚   â”œâ”€â”€ data.oml terminology.oml     # datasets/elements; concepts + is-a + mappings
â”‚       â”‚   â”œâ”€â”€ definition.oml               # phenotype: intent + computable criteria
â”‚       â”‚   â”œâ”€â”€ cohort.oml                    # patients, evaluations, evidence
â”‚       â”‚   â””â”€â”€ bundle.oml                    # description bundle -> gathers all instances
â”‚       â””â”€â”€ md/T2DM Phenotype/
â”‚           â”œâ”€â”€ Authoring/                    # dogfooding pages (compose the editors)
â”‚           â””â”€â”€ Analysis/                     # Dashboard, Gaps, Notebook
â””â”€â”€ build/                                    # generated OWL/html/course (git-ignored)
```

* **Vocabularies** (the method) live under `src/method/oml`. Start at `vocabulary.oml`.
* **Descriptions** (the model) live under `src/model/oml`. Start at `bundle.oml`.
* **Methodology templates** live under `src/method/md`: the five pattern editors, the analysis
  dashboard, the gap report, and the per-criterion navigation view. Project pages under
  `src/model/md/T2DM Phenotype` compose them by supplying an `ontology` context.
* The two **bundles** drive the reasoning: the *vocabulary bundle* triggers the taxonomy-closure
  axioms (sibling disjointness), and the *description bundle* gathers every instance so
  classification and the rules see the whole model at once.
* See **METHOD.md** for the four authoring patterns and **ANALYSIS.md** for the question-by-question
  findings.

## Domain scenario

A synthetic **Type 2 Diabetes (T2DM)** phenotype: five pieces of prose intent, four computable
criteria (HbA1c â‰¥ 6.5, a recorded T2DM diagnosis, exclusion of type 1 diabetes, and an eGFR
criterion), SNOMED CT / LOINC concepts with a real is-a hierarchy, two datasets (a full EHR and a
claims extract), and four de-identified patients. The scenario is deliberately imperfect so the
analysis has something to find: one intent has no computable criterion, one concept has no data
mapping, and one criterion is evaluable at one site but not the other.

## How to build / check it

Open the folder in VS Code with the **OML Code** extension (or run `oml start` once), then, from
the project root:

```bash
oml lint       # syntax + reference checks         -> "16 OML file(s) checked"
oml reason     # consistency + entailments         -> "11 ontology file(s) checked", consistent
oml validate   # SHACL editor constraints per page -> "8 SHACL target(s) scanned"
oml course -m src -b build/course   # compile the editor/dashboard/notebook pages
oml render -m src -b build/web      # render the pages to static HTML
```

To inspect the inferences (rule-derived exclusion, defined-concept classifications, transitive
subsumption, dataset evaluability, and the bundle-generated disjointness axioms):

```bash
oml reason -o build/owl --pretty   # persists asserted + entailed OWL as Turtle under build/owl
```

The editors, dashboard, gap report, and notebook are the **methodology** (`src/method/md`); the
pages that use them are under **`src/model/md/T2DM Phenotype`**. Open those in the OML viewer to
edit instances through the shapes and to run the analysis views.

> Tip: run the CLI from the **project root** (the folder containing `.oml/`). If you `cd` into a
> subfolder first, the OML server roots itself there and will not find the vocabulary under
> `src/method`.

## Business questions

1. **(Clinician)** Is every criterion in the intended phenotype represented in the computable
   criteria, or has intent been silently dropped?
2. **(Informatician)** Which parts of the phenotype cannot be evaluated with the data and
   terminology available?
3. **(Researcher/Informatician)** Which criteria stop mapping cleanly under a different dataset or
   terminology version, and how does that change the cohort?
4. **(Researcher)** For any patient in the cohort, which criteria and evidence caused inclusion or
   exclusion?
5. **(Researcher)** Which patients, data elements, and other criteria are affected when one
   criterion changes?

Each question maps onto specific terms and entailments: Q1 to the `RepresentedIntent` defined
concept (dropped intent stays unclassified), Q2 to `MappedConcept` (unmapped concepts stay
unclassified), Q3 to the `evaluableIn` rule (a criterion evaluable at Site A but not Site B),
Q4 to `Evaluation`/`supports` plus the `excludedFrom` rule, and Q5 to `dependsOnConcept`,
`satisfiedBy`, and `evaluableIn` (tracing what a criterion change touches).

## Author

David Maughan â€” SIE 502, Project Deliverable 2.
