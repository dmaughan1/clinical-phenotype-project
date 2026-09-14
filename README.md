# Clinical Phenotyping Ontology (SIE 502 Project Deliverable 2)

An [OML](https://www.modelware.io/) model of the system described in Project Deliverable 1: a tool
that lets a clinical researcher state, in plain language, the patient population they want to
study, and returns the matching records from an authorized clinical dataset — while keeping the
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

The professor's method/model split is used: the **method** (the vocabulary — *how* we describe
phenotypes) is separated from the **model** (the description — *a specific* phenotype and its
data).

```
clinical-phenotype-project/
├── .oml/settings.yml                       # sources: src/method and src/model
├── README.md
├── src/
│   ├── method/oml/www.example.com/phenotype/
│   │   ├── vocabulary.oml                   # the vocabulary (concepts, properties, relations, rule)
│   │   └── vocabulary-bundle.oml            # vocabulary bundle -> fires disjointness closure
│   └── model/oml/www.example.com/phenotype/description/
│       ├── data.oml                         # datasets + data elements
│       ├── terminology.oml                  # SNOMED/LOINC concepts + is-a hierarchy + mappings
│       ├── definition.oml                   # the T2DM phenotype: intent + computable criteria
│       ├── cohort.oml                       # patients, evaluations, evidence
│       └── bundle.oml                       # description bundle -> gathers all instances
└── build/owl/                              # generated OWL + entailments (git-ignored)
```

* **Vocabularies** (the method) live under `src/method`. Start at `vocabulary.oml`.
* **Descriptions** (the model) live under `src/model`. Start at `bundle.oml`, which pulls in the
  four description files.
* The two **bundles** drive the reasoning: the *vocabulary bundle* triggers the taxonomy-closure
  axioms (sibling disjointness) to be generated, and the *description bundle* gathers every
  instance so classification and the rules see the whole model at once.

## Domain scenario

A synthetic **Type 2 Diabetes (T2DM)** phenotype: five pieces of prose intent, four computable
criteria (HbA1c ≥ 6.5, a recorded T2DM diagnosis, exclusion of type 1 diabetes, and an eGFR
criterion), SNOMED CT / LOINC concepts with a real is-a hierarchy, two datasets (a full EHR and a
claims extract), and two de-identified patients. The scenario is rigged so the reasoner can
actually demonstrate each business question (e.g. one intent has no computable criterion; one
concept has no data mapping).

## How to build / check it

Open the folder in VS Code with the **OML Code** extension (or run `oml start` once), then, from
the project root:

```bash
oml lint       # syntax + reference checks  -> "16 OML file(s) checked"
oml validate   # SHACL table-editor checks   -> no targets (no markdown tables authored)
oml reason     # consistency + entailments   -> "11 ontology file(s) checked", consistent
```

To inspect the inferences (rule-derived cohort membership, defined-concept classifications,
transitive subsumption, and the bundle-generated disjointness axioms):

```bash
oml reason -o build/owl --pretty   # persists asserted + entailed OWL as Turtle under build/owl
```

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

David Maughan — SIE 502, Project Deliverable 2.
