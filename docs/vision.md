# Vision

## The problem

Code generation is getting faster, but code comprehension is not.

Developers increasingly spend time understanding code they did not write personally, including code produced by other engineers, frameworks, migrations, generators, and coding agents. Common questions are simple to state but expensive to answer:

- Where is this function called?
- What does it call?
- How does a request reach this code?
- What depends on this symbol?
- What changes if I edit this?
- Which tests cover this path?

Today, answering those questions often means jumping across definitions, references, search results, git diffs, and multiple editor tabs while mentally reconstructing the relationships.

## The idea

GlancePath turns those questions into small visual answers directly inside the editor.

The product should not begin with a giant repository graph. It should begin with the code the developer is currently looking at and the question they are trying to answer.

> Start with a question, not a graph.

The graph exists underneath the product as a deterministic model of the repository.

## Core interaction

A developer selects or places the cursor inside a symbol and invokes GlancePath.

The product can answer:

- **Where is this called?**
- **What does this call?**
- **How do I get here?**
- **What happens after this?**
- **What depends on this?**
- **What might this change affect?**

Each answer should show the smallest useful neighborhood around the symbol rather than the entire repository.

## Change impact

Change impact is a major use case, but it is not the entire product.

When a function changes, GlancePath should distinguish between:

- **Changed** — source lines in the symbol were modified.
- **Directly connected** — a caller, callee, import, inheritance, or other relationship can be established directly.
- **Potentially impacted** — a symbol is reachable through the repository graph and may be affected.

GlancePath should avoid claiming semantic breakage that static analysis cannot prove.

## Why now

Coding agents lower the cost of producing and modifying code. That shifts the bottleneck toward review, verification, navigation, and understanding.

A useful code-comprehension tool should therefore help both:

1. Humans understand unfamiliar or rapidly changing code.
2. Eventually, coding agents query the same deterministic repository graph rather than repeatedly reconstructing it through search and shell commands.

## Long-term direction

The same graph engine could eventually support:

- VS Code contextual visual exploration.
- PR and git-diff change maps.
- CI impact reports.
- Framework-aware paths such as HTTP route → service → repository → database.
- Test coverage relationships.
- Agent-facing tools such as `get_callers`, `get_callees`, `get_path`, and `get_impact`.
- Natural-language questions grounded in the deterministic graph.

AI should explain and query the graph, not replace deterministic analysis where source relationships can be established directly.
