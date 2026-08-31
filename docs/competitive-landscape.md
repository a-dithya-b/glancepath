# Competitive landscape

GlancePath enters an existing code-intelligence and visualization space. The goal is not to reproduce a generic dependency graph; the wedge is the interaction model: **a developer question becomes a small contextual visual answer inside the editor.**

## Closest products/projects

### Travsr

Strengths:

- deterministic local code graph,
- callers/dependencies/execution-path style queries,
- change/blast-radius capabilities,
- agent/MCP-oriented access.

Takeaway for GlancePath: graph construction alone is not differentiation. GlancePath should optimize for the developer's immediate question and present the smallest useful visual answer.

### ImpactLens

Strengths:

- git/PR-oriented change impact,
- affected files/functions/routes,
- test suggestions,
- strong Python/FastAPI relevance.

Takeaway: change impact is valuable, but GlancePath should make it one contextual question rather than the entire product.

### CodeRipple

Strengths:

- visualizes how AI/Copilot edits ripple through a codebase,
- change-focused visual flow.

Takeaway: AI-generated change review validates the timing of the problem, but GlancePath should work equally well for any code and any developer question.

### CodeSee

Strengths:

- repository maps,
- dependency visualization,
- PR/review maps,
- prior editor-based function-map experiments.

Takeaway: whole-repository maps are useful but can become overwhelming. GlancePath should default to local context around the code currently being inspected.

### AtomicViz / similar call-hierarchy visualizers

Strengths:

- interactive call hierarchy and architecture/dependency views,
- editor-native visualization.

Takeaway: visual call graphs are not enough. The product must map human questions to purpose-built views.

## Differentiation hypothesis

GlancePath is not primarily:

- a graph browser,
- an architecture diagram generator,
- a PR impact report,
- an AI chat interface.

It is a **visual code-comprehension interaction**.

The developer starts from a symbol and asks something naturally:

```text
Where is this called?
What happens after this?
How does execution get here?
What might my edit affect?
```

GlancePath translates that question into deterministic graph queries and renders a focused answer.

## Product principles implied by the landscape

1. Do not make users reason about graph terminology unless they want advanced controls.
2. Do not default to an entire repository graph.
3. Make provenance and uncertainty visible.
4. Keep analysis local and fast.
5. Treat change impact as an overlay on the same underlying mental model.
6. Build the graph engine independently so humans, CI, and agents can all consume it later.

## Open validation questions

- Are contextual visual answers materially faster than IDE references/call hierarchy for real developers?
- Which question is the strongest first hook: callers, execution path, or change impact?
- At what graph size does the visual stop helping?
- How much Python call resolution is necessary before users trust the product?
- Does the product need framework semantics early, or is language-level structure enough to create value?
