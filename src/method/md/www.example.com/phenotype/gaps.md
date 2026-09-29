---
template:
  id: http://www.example.com/phenotype/gaps
  name: "Gap Report"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Gap Report

One orphan / missing-relationship check per pattern. Each table lists the individuals that fail the
pattern's minimum, with enough context to act. These are closed-world questions over the analysis
scope: an empty table means "none **recorded** in this scope", not "none exist in the world". Run
this against the description **bundle** — against a single leaf description it will under-report,
because the peer descriptions it needs are not loaded.

## Intent pattern — dropped intent

Intended criteria that no computable criterion implements. **Fix:** author a computable criterion on
the *Realization* page, or delete the intent if it was withdrawn.

```table
---
columns: { intended: { label: "Intended criterion" }, intent: { label: "Meaning" } }
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

## Realization pattern — criteria that cannot run

Computable criteria with no data path in any dataset (every concept they use is unmapped or its data
element is unavailable everywhere). **Fix:** map the missing concept on the *Terminology* page, or
provide the data element on the *Datasets* page.

```table
---
columns: { crit: { label: "Criterion" }, logic: { label: "Logic" } }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?crit ?logic
WHERE {
  ?c a/rdfs:subClassOf* ph:ComputableCriterion .
  OPTIONAL { ?c rdfs:label ?crit }
  OPTIONAL { ?c ph:logicExpression ?logic }
  FILTER NOT EXISTS {
    ?c ph:dependsOnConcept ?k . ?k ph:mappedTo ?e . ?e ph:availableIn ?d .
  }
}
```

## Mapping pattern — unmapped concepts

Clinical concepts with no data element. A criterion depending only on these cannot be evaluated.
**Fix:** add a `mappedTo` on the *Terminology* page, or record why the concept is unmapped.

```table
---
columns: { concept: { label: "Concept" }, code: { label: "Code" }, status: { label: "Status" } }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?concept ?code ?status
WHERE {
  ?c a ph:ClinicalConcept .
  OPTIONAL { ?c rdfs:label ?concept }
  OPTIONAL { ?c ph:conceptCode ?code }
  OPTIONAL { ?c ph:mappingStatus ?status }
  FILTER NOT EXISTS { ?c ph:mappedTo ?e }
}
```

## Mapping pattern — orphan data elements

Data elements provided by no dataset. Anything mapped to them is effectively unreachable. **Fix:**
declare an `availableIn` on the *Datasets* page. (Expected empty.)

```table
---
columns: { element: { label: "Data element" } }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?element
WHERE {
  ?e a ph:DataElement .
  OPTIONAL { ?e rdfs:label ?element }
  FILTER NOT EXISTS { ?e ph:availableIn ?d }
}
```

## Adjudication pattern — unsupported decisions

Evaluations with no supporting evidence — an inclusion/exclusion no reviewer can audit. **Fix:**
attach an `Evidence` on the *Adjudication* page. (Expected empty.)

```table
---
columns: { evaluation: { label: "Evaluation" }, status: { label: "Decision" } }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?evaluation ?status
WHERE {
  ?eval a ph:Evaluation .
  OPTIONAL { ?eval rdfs:label ?evaluation }
  OPTIONAL { ?eval ph:membershipStatus ?status }
  FILTER NOT EXISTS { ?ev ph:supports ?eval }
}
```
