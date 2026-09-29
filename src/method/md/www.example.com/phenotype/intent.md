---
template:
  id: http://www.example.com/phenotype/intent
  name: "Phenotype Intent"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Phenotype & Intent

Pattern 1 of the methodology. Before any code, the researcher states *what population they mean*
in prose. This page captures a `Phenotype` and the `IntendedCriterion`s that make it up — one row
per clinical idea the phenotype is supposed to encode.

**Focal types.** `phenotype:Phenotype` (the named definition) and `phenotype:IntendedCriterion`
(a single piece of clinical intent, in plain language).

**Structure.** Each intended criterion is attached to its phenotype through `phenotype:partOf`
(the reverse of `comprises`), so a phenotype owns all of its intent even before any of it is made
computable. The phenotype points at the `Cohort` it is meant to produce through `phenotype:yields`.

**Why it matters.** Intent is the baseline the rest of the methodology is measured against. If a
piece of intent is never written down here, Question 1 ("was anything silently dropped?") has
nothing to check against — the drop becomes invisible. So this page is deliberately the first act.

**Rule.** Every intended criterion must state its intent text. A criterion with no text is an
empty placeholder that later steps cannot realize or review, so it is flagged.

```table-editor
---
columns: { this: { label: "Phenotype" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:PhenotypeShape
    a sh:NodeShape ;
    sh:targetClass phenotype:Phenotype ;
    sh:property [
        sh:path phenotype:id ;
        sh:name "Id" ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:order 0 ;
    ] ;
    sh:property [
        sh:path phenotype:yields ;
        sh:name "Cohort" ;
        sh:class phenotype:Cohort ;
        sh:maxCount 1 ;
        sh:order 1 ;
    ] ;
    .
```

```table-editor
---
columns: { this: { label: "Intended Criterion" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:IntendedCriterionShape
    a sh:NodeShape ;
    sh:targetClass phenotype:IntendedCriterion ;
    sh:sparql [
        sh:message "Every intended criterion must state its intent text." ;
        sh:select """
            SELECT $this WHERE {
                $this a phenotype:IntendedCriterion .
                FILTER NOT EXISTS { $this phenotype:intentText ?t }
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
        sh:path phenotype:partOf ;
        sh:name "Phenotype" ;
        sh:class phenotype:Phenotype ;
        sh:maxCount 1 ;
        sh:order 1 ;
    ] ;
    sh:property [
        sh:path phenotype:intentText ;
        sh:name "Intent" ;
        dash:editor dash:TextAreaEditor ;
        sh:maxCount 1 ;
        sh:order 2 ;
    ] ;
    .
```
