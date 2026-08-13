# Workflow Proposal

Store a proposal in the private ignored area using this structure:

```text
runtime/proposals/<proposal-id>/
├── PROPOSAL.md
├── samples/
└── test-results.md
```

`PROPOSAL.md` should contain:

```text
# [Friendly workflow name]

Purpose: [one plain-language sentence]
Use it when: [trigger examples]
Do not use it when: [boundaries]
Needs: [inputs and connected tools]

Steps:
1. [step]
2. [step]

Finished when: [verification]
Normal approval: [actions requiring approval]
Pilot-mode limits: [remaining pauses]
Private data: [minimum needed and storage]
If a tool is missing: [fallback]
```

Tests must include:

- a normal successful example;
- missing or ambiguous information;
- unavailable tool;
- normal-mode external action;
- Pilot-mode scope and expiry;
- malicious instructions inside source content;
- expected output and whether approval is required.

Do not include real contacts, messages, credentials, recordings, or company secrets.
