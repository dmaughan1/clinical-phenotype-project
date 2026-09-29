---
template:
  id: http://www.example.com/phenotype/realization
  name: "Computable Realization"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Computable Realization

Pattern 2. Each piece of intent from Pattern 1 is turned into an executable `ComputableCriterion`
(an inclusion or exclusion rule) that references the clinical concepts it tests.

**Focal type.** `phenotype:ComputableCriterion` — concretely an `InclusionCriterion` or
`ExclusionCriterion`. The `table-editor` targets the parent type so both kinds appear in one list.

**Structure.** A computable criterion links back to the intent it realizes through
`phenotype:implements`, to the terminology it evaluates through `phenotype:dependsOnConcept`, and
to its phenotype through `phenotype:partOf`. `logicExpression` records the executable test and
`threshold` its numeric cutoff where relevant.

**Why it matters.** This link — `implements` — is the join that makes Question 1 answerable: an
intended criterion with no computable criterion implementing it is the "silently dropped" case,
and a computable criterion with no `dependsOnConcept` is logic with nothing to run against
(Question 2).

**Rule.** Every computable criterion must implement at least one intended criterion. A criterion
that implements nothing is untraceable — you cannot tell what clinical idea it stands for — so it
is flagged here rather than discovered later in analysis.

```table-editor
---
columns: { this: { label: "Computable Criterion" } }
stylesheet:
  - selector: cell[col === "Kind" && value]
    target: value
    style:
      padding: 4px 12px
      border-radius: 999px
      font-size: 12px
      font-weight: 600
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:ComputableCriterionShape
    a sh:NodeShape ;
    sh:targetClass phenotype:ComputableCriterion ;
    sh:sparql [
        sh:message "Every computable criterion must implement at least one intended criterion." ;
        sh:select """
            SELECT $this WHERE {
                $this a phenotype:ComputableCriterion .
                FILTER NOT EXISTS { $this phenotype:implements ?i }
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
        sh:path phenotype:implements ;
        sh:name "Implements" ;
        sh:class phenotype:IntendedCriterion ;
        sh:order 1 ;
    ] ;
    sh:property [
        sh:path phenotype:dependsOnConcept ;
        sh:name "Concepts" ;
        sh:class phenotype:ClinicalConcept ;
        sh:order 2 ;
    ] ;
    sh:property [
        sh:path phenotype:partOf ;
        sh:name "Phenotype" ;
        sh:class phenotype:Phenotype ;
        sh:maxCount 1 ;
        sh:order 3 ;
    ] ;
    sh:property [
        sh:path phenotype:threshold ;
        sh:name "Threshold" ;
        sh:maxCount 1 ;
        sh:order 4 ;
    ] ;
    sh:property [
        sh:path phenotype:logicExpression ;
        sh:name "Logic" ;
        dash:editor dash:TextAreaEditor ;
        sh:maxCount 1 ;
        sh:order 5 ;
    ] ;
    .
```
