# Jamaica Command Center

Jamaica Command Center is a friendly resource pack for ChatGPT Work and Codex. Jamaica can describe a task in everyday language, see a short recommendation, and let the assistant complete the work with clear approval boundaries.

Public source: [github.com/troyuu/voice](https://github.com/troyuu/voice)

It helps with:

- Email and text-message triage, drafts, replies, and follow-ups
- Approved bulk outreach
- Call preparation, dialing assistance, notes, outcomes, and follow-ups
- Calendar, CRM, browser, data-entry, file, and research tasks
- Task-scoped computer control through explicit or inferred **Pilot mode**
- Turning repeated work into reviewed skills or specialist agent teams

## What Jamaica can say

```text
Help me answer these emails. Tell me which ones are urgent first.
```

```text
Prepare me for my call with this supplier. When I say Ready, open the call.
```

```text
Take care of today's confirmed appointments in the CRM and calendar.
```

The assistant starts with:

```text
Recommendation: ...
What I'll do: ...
Approval: ...
```

Routine work then continues automatically. Important actions still pause for Jamaica.

## Friendly operating rules

- Jamaica is the task owner. Her latest direct instruction controls the task.
- The assistant leads with the approach it believes will work best and briefly explains a better alternative when needed.
- The assistant uses plain language and asks only one question at a time.
- Recommendations help Jamaica decide; they never silently replace her instruction.
- Normal mode asks before sending, dialing, submitting, publishing, or deleting.
- Jamaica does not need a magic phrase. Clear completion commands such as `send this email`, `schedule the meeting`, or `update the CRM`, and instructions such as `handle this`, `take care of it`, `do what is needed`, or `finish this for me`, allow routine actions for that one task.
- The preview says when the assistant is treating a request as Pilot mode and names the outcome it will own.
- Requests for advice, a draft, a review, preparation, or `show me first` remain in normal mode. If Jamaica asks to review before an action, that instruction overrides inferred Pilot mode.
- Pilot mode does not bypass passwords, security prompts, payments, contracts, permissions, destructive actions, privacy, consent, or other high-risk boundaries.
- Every bulk outreach batch needs one final approval.
- Every live call needs Jamaica to say **Ready** before dialing; Jamaica remains the speaker.

## Setup on Jamaica's computer

This repository is the source package. It does not install itself and contains no credentials.

1. Install or open the current ChatGPT desktop app and sign in to Jamaica's Max account.
2. Use **Work locally** for tasks that need apps or files on her computer.
3. Install and enable the **Computer Use** plugin. On macOS, allow Screen Recording and Accessibility when prompted. On Windows, keep the target app visible on the active desktop.
4. Install and sign in to the email and calendar plugins Jamaica actually uses, such as Gmail/Google Calendar or Outlook Email/Outlook Calendar. Connect CRM or calling tools separately when available.
5. After this package is published as a plugin, install it from the Plugins directory and start a new chat. For local Codex-only development, open this folder as the project; its `AGENTS.md`, skills, and project-scoped agent definitions will be available there.
6. Copy `runtime.example/` to `runtime/` and fill in only the preferences Jamaica wants saved locally. Never put passwords, API keys, contact exports, recordings, or real messages in the repository.

Jamaica does not need to manage the specialist files. ChatGPT Work can delegate suitable complex tasks from the skill instructions. For local Codex use outside this folder, a technical administrator may optionally copy `.codex/agents/*.toml` into Jamaica's user agent directory; do not ask Jamaica to perform that setup herself.

On a Max account, use Ultra for difficult tasks with independent parts when available. Routine emails, calls, and data entry stay single-agent so they remain quick and simple.

Computer Use can operate only apps Jamaica approves. ChatGPT may still show permission or security prompts, and Jamaica must handle passwords and 2FA herself.

## Private local state

The public repository contains blank examples only. The ignored `runtime/` folder is for Jamaica's private profile, preferences, tool map, workflow counts, and draft workflow proposals.

Run contributor checks with Python 3.11 or newer:

```text
python3 scripts/validate_pack.py
python3 -m unittest discover -s tests -v
```

No test sends messages, starts calls, changes accounts, or uses the network.
