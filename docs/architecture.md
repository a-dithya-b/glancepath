# Architecture

## Overview

GlancePath should separate repository analysis from editor presentation.

```text
Python source
    │
    ▼
Parser / symbol discovery
    │
    ▼
Reference resolution
    │
    ▼
Deterministic code graph
    │
    ├── inspect queries
    ├── path queries
    └── impact analysis
            │
            ▼
       CLI / VS Code / CI / agents
```

The first implementation is a standalone Python library and CLI. VS Code is a consumer of the graph engine, not the place where analysis logic lives.

## Graph model

### Nodes

Initial node kinds:

- `module`
- `class`
- `function`
- `method`

Each node should contain at least:

```text
id
name
kind
file
start_line
end_line
module
parent_id (optional)
```

Stable IDs are important because git diffs, editor navigation, caches, and future agent APIs all need a consistent symbol identity.

Example:

```text
src.services.recon:ReconService.execute
```

### Edges

Initial relationships:

- `CONTAINS`
- `IMPORTS`
- `CALLS`
- `INHERITS`

Later relationships may include:

- `READS_FROM`
- `WRITES_TO`
- `ROUTES_TO`
- `EMITS`
- `CONSUMES`
- `TESTS`

Edges should carry provenance where practical so GlancePath can explain why a relationship exists.

Example:

```text
source: src.services.recon:ReconService.execute
target: src.matching.engine:MatchingEngine.match
type: CALLS
file: src/services/recon.py
line: 52
```

## Parsing strategy

For Python v0, use the standard-library `ast` module first.

The analyzer should make multiple passes:

1. Discover Python modules.
2. Parse files into ASTs.
3. Register classes, functions, and methods.
4. Build import aliases and local symbol tables.
5. Extract call sites and inheritance expressions.
6. Resolve references where confidence is sufficient.
7. Record unresolved references rather than guessing.

Static Python call resolution is inherently imperfect because of dynamic dispatch, decorators, monkey patching, runtime imports, and metaprogramming. The system should therefore preserve confidence/provenance rather than pretend the graph is complete.

## Query layer

The graph engine should support operations such as:

```text
get_symbol(id)
get_callers(id)
get_callees(id)
get_neighbors(id)
get_path(source, target)
get_reachable(id, direction, depth)
```

The CLI initially exposes those capabilities through higher-level developer questions rather than raw graph terminology.

## Impact engine

Impact analysis begins with git changes.

```text
git diff
   │
   ▼
changed files + line ranges
   │
   ▼
map ranges to graph symbols
   │
   ▼
changed symbol set
   │
   ▼
graph traversal
   │
   ▼
directly connected + potentially impacted symbols
```

GlancePath must clearly distinguish source facts from inference.

Suggested categories:

- `changed`
- `direct`
- `potential`

## Persistence

For v0, keep persistence simple. The graph may be serialized to a local JSON file under a GlancePath cache directory. Avoid introducing a graph database until repository scale or query performance proves it necessary.

## VS Code boundary

The eventual extension should:

- identify the symbol under the cursor,
- invoke/query the local GlancePath engine,
- render a small interactive graph,
- open source locations when nodes are selected,
- surface developer questions such as callers, callees, paths, and impact.

It should not duplicate Python parsing logic in TypeScript.

## Future AI boundary

LLMs may eventually:

- translate natural-language questions into graph queries,
- summarize a path,
- explain why a change might matter,
- name higher-level architectural concepts.

They should consume graph evidence and relevant source rather than invent repository structure from an ungrounded repository prompt.
