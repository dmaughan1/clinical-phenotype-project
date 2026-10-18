# phenotype-report generator

A reusable OML generator that renders a **Phenotype Specification & Data-Readiness Report**
(`Phenotype-Readiness.md`) from any model built with the clinical phenotyping vocabulary.

## Files

- `phenotype-report.oml` — `PhenotypeReportSpec` (`codegen:Spec`, a SPARQL CONSTRUCT with a `path`
  parameter) and `ReportTemplate` (`codegen:Template`, a nunjucks body).

Both are packaged with the method, so a consumer resolves them from
`deps/<method-package>/oml/www.example.com/phenotype/codegen/phenotype-report.oml`.

## Usage

In the consuming project, add a `codegen:Config` that binds the installed spec to your model
bundle (this config stays in the consumer; it is not part of the package):

```oml
description <http://example.org/mymodel/codegen#> as codegenConfigs {
    uses <http://opencaesar.io/codegen#> as codegen
    extends <http://www.example.com/phenotype/codegen/phenotype-report#> as report

    instance phenotypeReport : codegen:Config [
        codegen:spec report:PhenotypeReportSpec
        codegen:context "http://example.org/mymodel/bundle"   // your description bundle IRI, no '#'
        codegen:binding [ codegen:key "path" codegen:value "build/docs" ]
    ]
}
```

Then run:

```
oml codegen -c phenotypeReport
```

The report is written to `<path>/Phenotype-Readiness.md`.

## What it reads

For each `phenotype:Phenotype` it joins `comprises`, `implements`, `dependsOnConcept`, `mappedTo`,
`availableIn`, and the reified `Evaluation`/`supports` chain. Output: phenotype overview, intended
criteria (and whether each is realized), computable realization, the concept→data-element→dataset
trace, coverage gaps, and a patient-evidence summary.

## Notes

- Queries only **asserted** forward relations; it does not depend on the reasoner. Computable
  criteria are matched by having an asserted `implements` (so subclass typing is irrelevant).
- The gap section is a **closed-world** enumeration (`FILTER NOT EXISTS`): it reports what is not
  modeled, which is not an open-world proof of absence.
