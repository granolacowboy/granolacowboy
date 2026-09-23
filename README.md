# Rich Berman

**Legal technology consultant and systems builder focused on reliable automation for law firms.**

I build the layer between legal operations and software: intake systems, workflow automation, integrations, reporting, document automation, AI-enabled tools, and the controls that keep those systems inspectable and useful in production.

My public work emphasizes a simple idea: **use models for language and judgment support; use deterministic software for rules, records, gates, provenance, and verification.**

**[Engineering methodology →](https://granolacowboy.dev/writing/post-4-deterministic-ai)** How I use AI agents to build deterministic systems without trusting the agents to be deterministic.

## Selected work

| Project | What it demonstrates |
|---|---|
| **[intake-triage-mcp](https://github.com/granolacowboy/intake-triage-mcp)** | A deterministic MCP server for legal intake triage with structured validation, provenance, a hard conflicts gate, and append-only logging. No model or network calls in the decision path. |
| **[intake-eval-harness](https://github.com/granolacowboy/intake-eval-harness)** | A reusable MCP evaluation harness for deterministic answer scoring, required/forbidden tool assertions, execution-order constraints, and provenance across stdio, SSE, and streamable HTTP. |
| **[mhsb-intake-leak-calculator](https://github.com/granolacowboy/mhsb-intake-leak-calculator)** | A browser-only law-firm intake model with explicit assumptions, sourced coefficients, automated tests, accessibility checks, and zero runtime tracking. **[Live tool](https://www.mhsbsolutions.com/tools/intake-revenue-leak-calculator/)** |
| **[llm-security-for-law-firms](https://github.com/MHSBai/llm-security-for-law-firms)** | A practical threat model and adoption checklist for using LLMs in law firms. **[Read it](https://mhsbai.github.io/llm-security-for-law-firms/)** |
| **[granolacowboy.dev](https://github.com/granolacowboy/granolacowboy.dev)** | Source for my technical field notes and case studies, built as a minimal static Astro site with build-time verification. **[Visit](https://granolacowboy.dev)** |

## Engineering principles

- **Deterministic where failure matters.** Conflicts gates, validation, calculations, audit records, and policy enforcement should not depend on a model behaving itself.
- **Evaluate systems, not demos.** Golden cases, repeatable tests, CI, smoke checks, and explicit failure semantics matter more than impressive one-off outputs.
- **Preserve provenance.** A useful answer should make it possible to identify what data, rule, assumption, or source produced it.
- **Keep humans in the control plane.** Automation should surface decisions and exceptions clearly instead of hiding them behind “AI.”
- **Minimize unnecessary data movement.** Local-first and browser-only designs are preferable when the workflow does not require a remote service.
- **Measure operational outcomes.** Technology should improve throughput, quality, response time, consistency, or decision visibility—not merely add another interface.

## Current work

- **[MHSB Solutions](https://mhsbsolutions.com)** — legal-technology strategy, implementation, workflow automation, integrations, reporting, and AI enablement for law firms.
- **[LexLabs](https://lexlabsystems.com)** — productized Lawmatics implementation systems.
- **[efficient.esq](https://efficient.esq)** — law-firm AI operating-model and governance work.
- **Defensive security research** — hardening the systems, agents, and infrastructure used to run the above safely.

## Research library

**[stars](https://github.com/granolacowboy/stars)** is my automatically maintained GitHub research index: thousands of repositories organized into topic-specific lists across AI, agents, security, automation, infrastructure, legal technology, and adjacent tooling.

## Contact

- **Website:** [granolacowboy.dev](https://granolacowboy.dev)
- **MHSB Solutions:** [mhsbsolutions.com](https://mhsbsolutions.com)
- **LinkedIn:** [linkedin.com/in/mhsb](https://www.linkedin.com/in/mhsb)
- **Email:** [rich@mhsbsolutions.com](mailto:rich@mhsbsolutions.com)
