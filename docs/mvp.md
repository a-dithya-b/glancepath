# MVP

## Goal

Prove that GlancePath can turn a Python repository into a useful, trustworthy local graph that answers a few high-value developer questions.

The MVP is successful if we can point it at unfamiliar Python repositories and get answers that are materially faster to understand than manually jumping through definitions and references.

## User questions in scope

The first version should answer:

1. **Where is this symbol called?**
2. **What does this symbol call?**
3. **What is the local path around this symbol?**
4. **What symbols were changed in this git diff?**
5. **What code is directly connected to those changes?**
6. **What code is potentially impacted downstream/upstream?**

## CLI shape

Working interface:

```bash
glancepath scan .
glancepath inspect package.module:symbol
glancepath impact --diff main
```

Potential follow-up commands:

```bash
glancepath callers package.module:symbol
glancepath callees package.module:symbol
glancepath path source:symbol target:symbol
```

Exact command names may change as the interaction becomes clearer.

## In scope

### Python parsing

- `.py` file discovery
- modules
- classes
- functions
- methods
- imports
- inheritance
- basic call sites
- source locations

### Graph

- stable symbol IDs
- nodes and edges
- adjacency queries
- bounded traversal
- JSON serialization

### Git impact

- compare working tree/branch against a base ref
- parse changed line ranges
- map changed lines to symbols
- mark changed nodes
- traverse direct and potential impact

### Output

v0 may print structured text/JSON. A polished visualization is deliberately deferred until the graph has proven useful.

## Explicitly out of scope for v0

- VS Code extension
- LLM integration
- accounts or cloud backend
- multiple languages
- graph database
- perfect dynamic Python resolution
- runtime tracing
- framework-specific FastAPI/Django/SQLAlchemy semantics
- test coverage integration
- GitHub PR bot
- MCP server

These are candidates only after the core graph proves itself.

## Validation repositories

Test against at least three different repository shapes:

1. Small hand-built fixture with known expected graph.
2. Medium Python application with classes/import aliases.
3. Real unfamiliar open-source Python repository.

For each repository, manually verify a sample of callers/callees and impact paths.

## Success criteria

The MVP passes if:

- symbol locations are reliably discovered,
- common local/imported calls resolve correctly,
- unresolved calls are represented honestly rather than guessed,
- changed lines map correctly to their enclosing symbols,
- impact traversal explains *why* each node was included,
- output remains useful rather than exploding into an unreadable whole-repository graph.

## First vertical slice

Build one end-to-end path before expanding analysis:

```text
sample repo
    ↓
scan
    ↓
functions registered
    ↓
CALLS edges created
    ↓
inspect one function
    ↓
print callers + callees
```

Then add git impact on top of the same model.
