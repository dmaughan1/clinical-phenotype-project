---
template:
  id: http://www.example.com/phenotype/terminology
  name: "Terminology Concepts"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Terminology Concepts

Pattern 3, terminology half. The `ClinicalConcept`s that the computable criteria test, arranged in
their is-a hierarchy and bound to the institutional data that carries them. Concepts are references
to an external terminology (SNOMED CT, LOINC, …); the methodology does not reproduce that
terminology, it only records the codes it uses and how they map onto data.

**Focal type.** `phenotype:ClinicalConcept`.

**Structure.** The tree is built from `phenotype:subsumedBy` (child concept → parent concept), the
reverse of the transitive `subsumes` relation, so specialising a concept is a single edit and
ancestor subsumption is then inferred. Each concept records its `conceptCode`, `sourceSystem`, and
`sourceVersion`, a `mappingStatus` (how cleanly it maps), and the `DataElement`(s) it is
`mappedTo`.

**Why it matters.** `mappedTo` is what Question 2 turns on: a concept with no data element cannot
be evaluated, so a criterion depending on it cannot run. `sourceVersion` is recorded so that
version drift is at least visible, though see the open issue in ANALYSIS.md — the current pattern
does not model a mapping that is valid in one version and not another.

**Rule.** Every concept must record a mapping status. Leaving it blank hides whether the concept is
an exact match, an approximation, or unmapped — exactly the distinction Question 3 needs.

```tree-editor
---
columns:
  this: { label: "Concept" }
  code: { label: "Code" }
  status: { label: "Mapping" }
stylesheet:
  - selector: cell[col === "Mapping" && value === "Unmapped"]
    target: value
    style:
      color: "#DC2626"
      font-weight: 600
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:ClinicalConceptShape
    a sh:NodeShape ;
    sh:targetClass phenotype:ClinicalConcept ;
    sh:sparql [
        sh:message "Every clinical concept must record a mapping status." ;
        sh:select """
            SELECT $this WHERE {
                $this a phenotype:ClinicalConcept .
                FILTER NOT EXISTS { $this phenotype:mappingStatus ?s }
            }
        """ ;
    ] ;
    sh:property [
        sh:path phenotype:subsumedBy ;
        sh:name "Broader concept" ;
        sh:class phenotype:ClinicalConcept ;
        sh:maxCount 1 ;
        dash:composite true ;
        sh:order 0 ;
    ] ;
    sh:property [
        sh:path phenotype:conceptCode ;
        sh:name "Code" ;
        sh:maxCount 1 ;
        sh:order 1 ;
    ] ;
    sh:property [
        sh:path phenotype:sourceSystem ;
        sh:name "System" ;
        sh:maxCount 1 ;
        sh:order 2 ;
    ] ;
    sh:property [
        sh:path phenotype:sourceVersion ;
        sh:name "Version" ;
        sh:maxCount 1 ;
        sh:order 3 ;
    ] ;
    sh:property [
        sh:path phenotype:mappingStatus ;
        sh:name "Mapping" ;
        sh:maxCount 1 ;
        sh:order 4 ;
    ] ;
    sh:property [
        sh:path phenotype:mappedTo ;
        sh:name "Data element" ;
        sh:class phenotype:DataElement ;
        sh:order 5 ;
    ] ;
    .
```
