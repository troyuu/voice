---
name: learn-workflows
description: Detect repeated successful work for Jamaica and draft a new reusable skill or specialist agent team for review. Use immediately when Jamaica asks to create, learn, save, or automate a workflow, or after the third substantially similar successful task recorded in the private runtime history. Draft and test proposals only; never silently enable, install, overwrite, or expand permissions.
---

# Learn Workflows

If no parent workflow has given the task preview, begin with **Recommendation**, **What I'll do**, and **Approval**. Explain `skill` as `a saved way of doing this task` and `agent` as `a focused helper` unless Jamaica asks for technical details.

## Detect repetition

Record only a privacy-minimized workflow fingerprint in `runtime/workflow-history.json` when that local ignored path is available. Use the included script:

```text
python3 scripts/track_workflow.py record --history runtime/workflow-history.json --workflow-id <generic-id> --summary <privacy-safe-summary> --success
```

Use a generic ID such as `supplier-follow-up` rather than a person's name, email address, phone number, or message content. Count only verified successful completions. Failed, cancelled, or materially different tasks do not count toward the trigger.

At count three, or immediately on Jamaica's request, recommend a reusable workflow. Do not interrupt urgent work; propose it after completing the current task.

## Design the smallest reusable solution

Use [references/proposal-spec.md](references/proposal-spec.md). Prefer one focused skill. Add a specialist agent only when the task has a stable, genuinely distinct role; add up to three agents only for independent complex parts. Never create an agent merely to make a simple workflow sound sophisticated.

Include:

- friendly name and plain-language purpose;
- trigger examples and non-triggers;
- required inputs and source of truth;
- steps, output, and completion check;
- normal and Full Pilot approval boundaries;
- privacy rules and missing-tool behavior;
- sample-only positive, negative, and hostile-content tests.

Draft under `runtime/proposals/<proposal-id>/` when available. This location is ignored by Git. Never place private examples in the public skills tree.

After the tested proposal files exist, record that the proposal was created so the same pattern is not repeatedly suggested:

```text
python3 scripts/track_workflow.py mark-proposed --history runtime/workflow-history.json --workflow-id <generic-id>
```

## Test without acting externally

Test on invented or sanitized sample data only. Do not send messages, start calls, modify apps, access accounts, install tools, enable the workflow, or change existing skills. Use a read-only workflow designer and risk reviewer for complex proposals if subagents are available.

Summarize the test results in plain language. Ask Jamaica to approve enabling the proposal only after tests pass. Approval to design is not approval to install, replace, publish, or expand authority; those are separate actions.

Finish with **Result**, **Completed**, **Waiting for you**, and one useful **Next recommendation**.
