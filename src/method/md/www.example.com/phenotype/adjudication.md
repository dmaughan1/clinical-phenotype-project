---
template:
  id: http://www.example.com/phenotype/adjudication
  name: "Cohort Adjudication"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Cohort Adjudication

Pattern 4. The per-patient record of how the phenotype was applied: which criteria a patient met
and the evidence behind each decision. This is what makes Question 4 ("why is this patient in or
out?") answerable for a reviewer.

**Focal types.** `phenotype:Patient` and `phenotype:Evidence`. The decision itself is the reified
`phenotype:Evaluation` (patient × criterion, carrying a `membershipStatus`). Evaluations are
authored in the `cohort` description as relation instances and shown on the analysis pages as a
graph; evidence and patients are table-edited here because they are ordinary individuals.

**Structure.** An `Evaluation` records that a patient `satisfies` a computable criterion with a
`membershipStatus` (Included / Excluded / Indeterminate). A piece of `Evidence` backs a decision
through `phenotype:supports` pointing at the evaluation. Exclusion membership is then *derived* by
the `CohortExclusion` rule rather than asserted by hand.

**Why it matters.** A decision with no supporting evidence is unauditable — the reviewer cannot see
why the patient was placed. Recording evidence against the evaluation, not against the patient,
keeps the rationale attached to the specific decision it justifies.

**Rule.** Every piece of evidence must support an evaluation. Free-floating evidence that backs no
decision is noise and is flagged.

```table-editor
---
columns: { this: { label: "Patient" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:PatientShape
    a sh:NodeShape ;
    sh:targetClass phenotype:Patient ;
    sh:property [
        sh:path phenotype:id ;
        sh:name "Id" ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:order 0 ;
    ] ;
    .
```

```table-editor
---
columns: { this: { label: "Evidence" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:EvidenceShape
    a sh:NodeShape ;
    sh:targetClass phenotype:Evidence ;
    sh:sparql [
        sh:message "Every piece of evidence must support an evaluation." ;
        sh:select """
            SELECT $this WHERE {
                $this a phenotype:Evidence .
                FILTER NOT EXISTS { $this phenotype:supports ?e }
            }
        """ ;
    ] ;
    sh:property [
        sh:path phenotype:id ;
        sh:name "Id" ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:order 0 ;
    ] ;
    sh:property [
        sh:path phenotype:supports ;
        sh:name "Supports evaluation" ;
        sh:class phenotype:Evaluation ;
        sh:order 1 ;
    ] ;
    .
```
