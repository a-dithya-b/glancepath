# GlancePath

**Visual answers for the questions developers already have about code.**

Code is increasingly cheap to generate, but understanding code is not.

As coding agents produce more code, developers spend more time reconstructing relationships they did not personally create: where a function is used, what it calls, how a request moves through the system, what depends on a piece of code, and what a change might affect.

GlancePath aims to turn those questions into immediate visual answers directly inside the editor.

## Product thesis

> Start with a question, not a graph.

The graph is an implementation detail. The user experience should begin with developer questions such as:

- Where is this function called?
- What does this function call?
- How does execution reach this code?
- Where does data go next?
- Which tests cover this path?
- What might this change affect?

Instead of forcing developers to jump through definitions, references, grep results, tabs, and files, GlancePath should present a small contextual visual answer.

## Example

Given:

```python
async def process_payment(...):
    ...
```

GlancePath should be able to show something like:

```text
                  checkout()
                      │
                      ▼
              process_payment()
               ← YOU ARE HERE
                ╱     │      ╲
               ▼      ▼       ▼
          validate  charge   save
                      │
                      ▼
                StripeClient
```

And answer questions like:

```text
Where is this called?
What happens after this?
What depends on this?
What might change if I edit this?
```

## Initial scope

The first version targets **Python only** and focuses on a deterministic local analysis engine.

Initial commands:

```bash
glancepath scan .
glancepath inspect package.module:symbol
glancepath impact --diff main
```

The first milestone is intentionally small:

1. Parse Python files.
2. Discover modules, classes, functions, and methods.
3. Resolve imports and basic symbol references.
4. Build call and inheritance relationships.
5. Map git diff line ranges to affected symbols.
6. Traverse the graph to surface possible impact.
7. Prove the result on several unfamiliar real-world Python repositories.

No LLM is required for this phase.

## Design principles

- **Questions before graphs** — the UI should answer a developer question rather than expose graph internals.
- **Context over completeness** — show the smallest useful neighborhood, not an overwhelming whole-repo graph.
- **Deterministic first** — static analysis should establish relationships that can be proven from source.
- **Explicit uncertainty** — distinguish direct relationships from possible downstream impact.
- **Local-first** — code analysis should work without uploading a repository.
- **Editor-native** — the eventual VS Code experience should start from the code currently being read.

## Repository layout

```text
src/glancepath/
├── parser/
├── graph/
├── impact/
└── cli.py

tests/
└── fixtures/

docs/
├── vision.md
├── architecture.md
├── mvp.md
└── competitive-landscape.md
```

## Status

Very early experiment. The immediate goal is to prove that GlancePath can build a useful and trustworthy Python code graph before investing in the VS Code visualization layer.
