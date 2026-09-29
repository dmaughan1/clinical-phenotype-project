---
template:
  id: http://www.example.com/phenotype/datasets
  name: "Datasets & Data Elements"
  rank: 0
  expose:
    - kind: compose
  params:
    - id: ontology
      type: iri
      defaultValue: ${context.ontology}
      required: true
---
# Datasets & Data Elements

Pattern 3, data half. The authorized datasets and the data elements they expose. This is reference
data owned by the data steward and kept separate from the terminology so that either can change
without disturbing the other.

**Focal types.** `phenotype:Dataset` and `phenotype:DataElement`.

**Structure.** A data element declares which datasets provide it through `phenotype:availableIn`.
Concepts point *into* these elements (via `mappedTo` on the terminology page), so the join
"concept → element → dataset" is what tells us whether a criterion can actually run against a given
dataset (Question 3).

**Why it matters.** The same data element is not present in every dataset — a claims extract has no
lab values. Recording `availableIn` per element is what lets the analysis layer show a criterion
that is evaluable at one site and not another instead of assuming data is everywhere.

**Rule.** Every data element must be available in at least one dataset. An element provided by no
dataset is unreachable and any concept mapped to it is effectively unmapped.

```table-editor
---
columns: { this: { label: "Data Element" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:DataElementShape
    a sh:NodeShape ;
    sh:targetClass phenotype:DataElement ;
    sh:sparql [
        sh:message "Every data element must be available in at least one dataset." ;
        sh:select """
            SELECT $this WHERE {
                $this a phenotype:DataElement .
                FILTER NOT EXISTS { $this phenotype:availableIn ?d }
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
        sh:path phenotype:availableIn ;
        sh:name "Available in" ;
        sh:class phenotype:Dataset ;
        sh:order 1 ;
    ] ;
    .
```

```table-editor
---
columns: { this: { label: "Dataset" } }
---
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix phenotype: <http://www.example.com/phenotype/vocabulary#> .

phenotype:DatasetShape
    a sh:NodeShape ;
    sh:targetClass phenotype:Dataset ;
    sh:property [
        sh:path phenotype:id ;
        sh:name "Id" ;
        sh:datatype xsd:string ;
        sh:maxCount 1 ;
        sh:order 0 ;
    ] ;
    .
```
