# Rules for editing ADA plans

Inherit the repository's root AGENTS.md. Read STANDARDS.md and CURRENT-STATE.md
before changing a phase's scope or dependencies.

- These documents describe future work; reading them does not authorize implementation.
- Preserve actual Phase 0–2 history. Do not renumber already released milestones.
- Keep planned, implemented, locally checked and target-verified states distinct.
- Every phase needs concrete inputs, checkpoints, data/interfaces, failures, tests
  and exit criteria. Compilation alone does not prove a product flow works.
- A UI control must map to an implemented API or be explicitly deferred.
- Resolve prerequisite changes in README.md and STATUS.md as well as the phase file.
- Preserve privacy, model trust, immutable evidence and persona/permission separation.
- Never put credentials, raw private conversations or hidden model reasoning here.
- Do not invent commands for applications that have not been scaffolded. Proposed
  commands must be labeled and verified when their implementation is created.
- Include a reproducible migration and validation route when changing a released schema.
