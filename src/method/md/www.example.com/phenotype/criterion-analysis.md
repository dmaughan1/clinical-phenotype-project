---
template:
  id: http://www.example.com/phenotype/criterion-analysis
  name: "Criterion Analysis"
  rank: 0
  expose:
    - kind: navigation
      match:
        anyTypeOf:
          - http://www.example.com/phenotype/vocabulary#ComputableCriterion
          - http://www.example.com/phenotype/vocabulary#InclusionCriterion
          - http://www.example.com/phenotype/vocabulary#ExclusionCriterion
  params:
    - id: member
      type: iri
      defaultValue: ${context.member}
      required: true
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# [[${member}]]

A standardized read-out for whichever computable criterion is open. Because it is a `navigation`
template matched to `ComputableCriterion`, the same analysis applies to every criterion without
copying it — open any criterion and this is what you get.

## Logic

```text
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
SELECT ?logic WHERE { <${member}> ph:logicExpression ?logic . }
```

## Concepts it depends on

The terminology this criterion tests, with mapping status. An `Unmapped` row means this criterion
cannot run wherever that concept is the only route to the data (Question 2).

```table
---
columns:
  concept: { label: "Concept" }
  code: { label: "Code" }
  status: { label: "Mapping" }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?concept ?code ?status
WHERE {
  <${member}> ph:dependsOnConcept ?c .
  OPTIONAL { ?c rdfs:label ?concept }
  OPTIONAL { ?c ph:conceptCode ?code }
  OPTIONAL { ?c ph:mappingStatus ?status }
}
```

## Where it can run

Data paths this criterion has per dataset. A `0` is a dataset where the criterion cannot be
evaluated (Question 3).

```table
---
columns:
  dataset: { label: "Dataset" }
  paths: { label: "Data paths" }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?dataset (COALESCE(?n, 0) AS ?paths)
WHERE {
  ?ds a ph:Dataset ; rdfs:label ?dataset .
  OPTIONAL {
    SELECT ?dataset (COUNT(?e) AS ?n)
    WHERE {
      <${member}> ph:dependsOnConcept ?k .
      ?k ph:mappedTo ?e .
      ?e ph:availableIn ?ds2 .
      ?ds2 rdfs:label ?dataset .
    }
    GROUP BY ?dataset
  }
}
ORDER BY ?dataset
```

## Patients decided by it

Who this criterion placed, and how (Question 4). These are the patients a change to this criterion
would force you to re-adjudicate (Question 5).

```table
---
columns:
  patient: { label: "Patient" }
  status: { label: "Decision" }
---
PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
PREFIX oml: <http://opencaesar.io/oml#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?patient ?status
WHERE {
  ?eval oml:hasTarget <${member}> ; oml:hasSource ?p .
  OPTIONAL { ?p rdfs:label ?patient }
  OPTIONAL { ?eval ph:membershipStatus ?status }
}
```
