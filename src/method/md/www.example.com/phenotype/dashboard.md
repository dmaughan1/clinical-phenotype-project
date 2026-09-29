---
template:
  id: http://www.example.com/phenotype/dashboard
  name: "Phenotype Analysis Dashboard"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Phenotype Analysis

This dashboard observes the model the editors produced. Each section is *Question → Evidence →
Interpretation*: the prose states the stable meaning, the live view supplies the changing numbers.

A standing caveat applies to everything below. These views report what the **model** says, not what
is **clinically true**. "Every intended criterion is realized" means the modeling is complete, not
that the phenotype is the medically correct definition, that a code is the right code, or that a
patient record is accurate. Those judgments live outside the model.

## Coverage of intent (Question 1)

**Question.** Is every intended clinical criterion realized by a computable criterion, or was some
intent silently dropped? **Evidence:** intended criteria with no `implements` edge pointing at them.

```table
---
columns:
  intended: { label: "Dropped intent" }
  intent: { label: "What it meant" }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?intended ?intent
WHERE {
  ?i a ph:IntendedCriterion .
  OPTIONAL { ?i rdfs:label ?intended }
  OPTIONAL { ?i ph:intentText ?intent }
  FILTER NOT EXISTS { ?c ph:implements ?i }
}
```

**Interpretation.** Rows here are intent the phenotype claims but does not compute. An empty table
would mean full realization *in this scope*; a non-empty table names exactly what to go build.

## Why each patient was placed (Question 4)

**Question.** For a patient, which criteria and evidence caused inclusion or exclusion? **Evidence:**
every evaluation, joined to its patient, the criterion, the recorded decision, and the evidence
backing it.

```table
---
columns:
  patient: { label: "Patient" }
  criterion: { label: "Criterion" }
  status: { label: "Decision" }
  evidence: { label: "Evidence" }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX oml: <http://opencaesar.io/oml#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT ?patient ?criterion ?status ?evidence
WHERE {
  ?eval a ph:Evaluation ; oml:hasSource ?p ; oml:hasTarget ?c .
  OPTIONAL { ?p rdfs:label ?patient }
  OPTIONAL { ?c rdfs:label ?criterion }
  OPTIONAL { ?eval ph:membershipStatus ?status }
  OPTIONAL { ?ev ph:supports ?eval . OPTIONAL { ?ev dc:description ?evidence } }
}
ORDER BY ?patient ?criterion
```

**Interpretation.** This is the audit trail a reviewer asks for: each row is one decision and the
evidence behind it. Exclusion is also *derived* — the `CohortExclusion` rule marks a patient
`excludedFrom` the cohort as soon as they meet an exclusion criterion, so the "Excluded" rows here
are the asserted evaluations behind that inference. The table shows the model's recorded rationale;
it does not certify the evidence is clinically accurate.

## Evaluability across datasets (Question 3)

**Question.** When the same phenotype is applied to different datasets, which criteria stop mapping,
and how does that change who can be found? **Evidence:** a criterion × dataset matrix; the value is
the number of concept→element→dataset data paths the criterion has in that dataset. Zero means the
criterion cannot run there. The population is built from *all* criteria × *all* datasets first, so
missing paths appear as an explicit `0` rather than vanishing.

```matrix
---
rowColumnLabel: Criterion / Dataset
stylesheet:
  - selector: cell [Number(value) === 0]
    style:
      background-color: "#FCA5A5"
  - selector: cell [Number(value) > 0]
    style:
      background-color: "#BBF7D0"
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?row ?column (COALESCE(?n, 0) AS ?value)
WHERE {
  ?crit a/rdfs:subClassOf* ph:ComputableCriterion ; rdfs:label ?row .
  ?ds a ph:Dataset ; rdfs:label ?column .
  OPTIONAL {
    SELECT ?row ?column (COUNT(?e) AS ?n)
    WHERE {
      ?crit a/rdfs:subClassOf* ph:ComputableCriterion ; rdfs:label ?row ; ph:dependsOnConcept ?k .
      ?k ph:mappedTo ?e .
      ?e ph:availableIn ?ds .
      ?ds rdfs:label ?column .
    }
    GROUP BY ?row ?column
  }
}
ORDER BY ?row ?column
```

**Interpretation.** A red cell is a criterion the dataset cannot support. In the example, the HbA1c
criterion is green at the EHR site and red at the claims site (no lab values there). A patient whose
only supporting criterion is HbA1c (P0003 in this data) therefore loses that support at the claims
site. That is as far as this view goes — it shows *which criteria stop mapping*, not the resulting
cohort membership, because the model has one cohort and does not run it per dataset (see ANALYSIS.md
for that diagnosed gap). The denominator is fixed (every criterion × every dataset), so a fully
green matrix would be real, not an artifact of missing rows.

## Mapping quality (Question 2 / 3)

**Question.** How clean are the terminology mappings the phenotype relies on? **Evidence:** the
distribution of `mappingStatus` over the clinical concepts in scope.

```chart
---
type: bar
data:
  labels: status
  datasets:
    - label: Concepts
      data: count
options:
  indexAxis: y
  plugins:
    title: { display: true, text: "Concepts by mapping status" }
    legend: { display: false }
  scales:
    x: { beginAtZero: true }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>

SELECT ?status (COUNT(?c) AS ?count)
WHERE {
  ?c a ph:ClinicalConcept ; ph:mappingStatus ?status .
}
GROUP BY ?status
ORDER BY DESC(?count)
```

**Interpretation.** `Unmapped` and `Broader` bars are where Question 2 bites: an unmapped concept
cannot be evaluated at all, and a broader mapping means the criterion is testing something coarser
than the intent. Counts are a triage signal, not a quality guarantee — an `Exact` label is still a
human claim the model takes on trust.

## Terminology hierarchy (context)

**Question.** How specific are the concepts the phenotype uses, and what sits beneath them?
**Evidence:** the asserted `subsumes` is-a hierarchy (ancestor links are additionally inferred by the
transitive relation).

```tree
---
columns: { this: { label: "Concept" } }
containment: [ ph:subsumes ]
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>

CONSTRUCT { ?parent ph:subsumes ?child . }
WHERE { ?parent ph:subsumes ?child . }
```

**Interpretation.** Depth matters clinically: choosing a broad parent concept pulls in everything
beneath it. Seeing the tree is how an author decides whether the phenotype should include a concept's
descendants — a decision the prose definition usually leaves unstated.

## Traceability / change-impact backbone (Question 5)

**Question.** If a criterion changes, what is structurally downstream of it? **Evidence:** the
criterion → concept → data element → dataset chain, rendered as a graph.

```graph
---
layout: { mode: force, running: true, fit: true, padding: 24 }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  ?crit ph:dependsOnConcept ?k .
  ?k ph:mappedTo ?e .
  ?e ph:availableIn ?d .
}
WHERE {
  ?crit a/rdfs:subClassOf* ph:ComputableCriterion ; ph:dependsOnConcept ?k .
  OPTIONAL { ?k ph:mappedTo ?e . OPTIONAL { ?e ph:availableIn ?d . } }
}
```

**Interpretation.** Reachability here means *potentially affected*, not *certainly changed*: if the
HbA1c criterion is edited, the HbA1c concept, its data element, and the EHR dataset are the things a
reviewer should re-check — but the graph does not prove any of them actually needs to change. The
per-patient side of impact (which patients were decided by a criterion) is computed in the notebook,
where hop-distance is easier to carry.
