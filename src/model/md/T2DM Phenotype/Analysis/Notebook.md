---
ontology: http://www.example.com/phenotype/description/bundle
---

# Using the methodology: walkthrough and change-impact

This notebook is the "how to drive it" companion to the editors. It walks the authoring order the
method prescribes, then runs the one analysis that genuinely needs code rather than a query — a
downstream change-impact trace for Question 5.

## Workflow

The editors are meant to be used in dependency order, because each pattern needs the previous one's
output to point at:

1. **Intent** — write the plain-language criteria first, attached to the phenotype. This is the
   baseline everything else is checked against; skip it and a dropped criterion becomes invisible.
2. **Realization** — turn each intent into an inclusion/exclusion criterion that names the concepts
   it tests. The `implements` link is what later proves nothing was dropped.
3. **Terminology + Datasets** — record the concepts (with codes and mapping status) and which
   datasets carry the data. This is usually authored by different people (informatician, data
   steward) than the phenotype itself, which is why those descriptions are kept separate.
4. **Adjudication** — record each patient's evaluation and the evidence behind it.

You do not have to author in this order, but out of order the gap report on the *Gaps* page will
light up until the links are filled — which is the point: the method makes the missing link
visible instead of letting it pass silently.

**Why a notebook and not another dashboard view.** The dashboard answers questions that are one
query wide. Change-impact is different: it is a walk over a heterogeneous graph (criterion →
concept → data; criterion ← evaluation ← patient) where the useful output is *how far* each
affected thing is from the change. A single SPARQL query can test reachability but does not carry
hop-distance or group results by kind cleanly, so the work splits as **query (pull the edges) →
compute (breadth-first walk with distance) → render (table + chart)**.

## The criteria under analysis

Before the impact walk, here are the computable criteria themselves, live through the same
`realization` editor used on the *Authoring* page. Editing a criterion here (its logic, the intent
it implements, the concepts it uses) is what the change-impact analysis below reacts to — so you
can change a criterion and immediately re-run the walk to see what it touches.

```compose
template: http://www.example.com/phenotype/realization
```

## Change impact (Question 5)

Pick a criterion; the table lists everything structurally downstream of it, with how many hops
away it is. Reachability means *potentially affected* — something a reviewer should re-check — not
proof that its clinical meaning changes.

```python
include('src/method/py/utils.py')
from collections import deque, defaultdict

# --- query: pull every downstream edge once, tagged with the role it plays ---
edge_rows = (await query("""
  PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
  PREFIX oml: <http://opencaesar.io/oml#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  SELECT ?src ?role ?dst WHERE {
    { ?eval oml:hasTarget ?src ; oml:hasSource ?dst . BIND('patient' AS ?role) }
    UNION { ?ev ph:supports ?eval . ?eval oml:hasTarget ?src . BIND('evidence' AS ?role) BIND(?ev AS ?dst) }
    UNION { ?src ph:dependsOnConcept ?dst . BIND('concept' AS ?role) }
    UNION { ?src ph:mappedTo ?dst . BIND('data element' AS ?role) }
    UNION { ?src ph:availableIn ?dst . BIND('dataset' AS ?role) }
    UNION { ?src ph:subsumes ?dst . BIND('narrower concept' AS ?role) }
    UNION { ?src ph:conceptUsedBy ?dst . BIND('other criterion' AS ?role) }
    UNION { ?src ph:partOf ?dst . BIND('phenotype' AS ?role) }
    UNION { ?src ph:yields ?dst . BIND('cohort' AS ?role) }
  }
"""))["rows"]

label_rows = (await query("""
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  SELECT ?x ?l WHERE { ?x rdfs:label ?l }
"""))["rows"]
labels = {r["x"]: r["l"] for r in label_rows}
def lbl(iri): return labels.get(iri) or frag(iri)

adj = defaultdict(list)
for r in edge_rows:
    adj[r["src"]].append((r["role"], r["dst"]))

crit_rows = (await query("""
  PREFIX ph: <http://www.example.com/phenotype/vocabulary#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  SELECT ?c WHERE { ?c a/rdfs:subClassOf* ph:ComputableCriterion }
"""))["rows"]
criteria = sorted({r["c"] for r in crit_rows}, key=lbl)

# --- compute: breadth-first walk carrying hop-distance ---
def impact(start):
    seen = {start: 0}; q = deque([start]); hits = []
    while q:
        n = q.popleft()
        for role, d in adj.get(n, []):
            if d not in seen:
                seen[d] = seen[n] + 1
                hits.append((d, role, seen[d]))
                q.append(d)
    return hits

# --- render: an interactive table (choose the criterion) ---
def render(sel=None):
    start = sel or criteria[0]
    hits = sorted(impact(start), key=lambda h: (h[2], h[1]))
    if not hits:
        display(f"<p><em>Nothing downstream of {lbl(start)} in this scope.</em></p>", id="impact")
        return
    body = "".join(f"<tr><td>{lbl(n)}</td><td>{role}</td><td>{dist}</td></tr>" for n, role, dist in hits)
    display(
        f"<p><b>{len(hits)}</b> elements are downstream of <b>{lbl(start)}</b> "
        f"(potentially affected if it changes):</p>"
        '<table class="oml-md-table"><thead><tr><th>Affected element</th>'
        f"<th>Role</th><th>Hops</th></tr></thead><tbody>{body}</tbody></table>",
        id="impact",
    )

opts = "".join(f'<option value="{c}">{lbl(c)}</option>' for c in criteria)
display(clientWidget(f'<label>Criterion: <select>{opts}</select></label>', render))
display('<div id="impact"></div>')
render(criteria[0])
```

The same walk, summarized as counts per kind of affected element for one criterion:

```python
import micropip
await micropip.install(['matplotlib'])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

subject = "http://www.example.com/phenotype/description/definition#T2dmDx"
by_role = defaultdict(int)
for _node, role, _dist in impact(subject):
    by_role[role] += 1

roles = sorted(by_role, key=lambda r: by_role[r])
counts = [by_role[r] for r in roles]

fig, ax = plt.subplots(figsize=(6, 3.2))
ax.barh(roles, counts, color="#7a6cff")
for i, c in enumerate(counts):
    ax.text(c + 0.05, i, str(c), va="center", fontsize=9)
ax.set_xlabel("count")
ax.set_title(f"Downstream of {lbl(subject)}, by kind")
plt.tight_layout()
display(image_html(fig))
```

**Open issue.** The walk treats every edge as equally impactful. In reality some edges are
"re-check" (a shared concept) and some are "must re-run" (a patient decided by this exact
criterion). A useful extension would weight edges by role and rank affected patients first. Left
out here because the weighting is a clinical judgment the model does not currently capture.
