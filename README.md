# Jamaica Command Center

Jamaica Command Center is a friendly resource pack for ChatGPT Work and Codex. Jamaica can describe a task in everyday language, see a short recommendation, and let the assistant complete the work with clear approval boundaries.

Public source: [github.com/troyuu/voice](https://github.com/troyuu/voice)

## Install with the ChatGPT desktop app

Jamaica does not need to use Terminal or understand plugins. In a new Codex task in the ChatGPT desktop app, she can paste:

```text
Install Jamaica Command Center from https://github.com/troyuu/voice for my future tasks. You may complete the local setup for me. Add the Jamaica Tools marketplace, install the jamaica-command-center plugin, and verify that all seven skills are available. Also check that the official Computer Use plugin is installed and enabled; if it is missing, install or enable it for me. Explain any permission or sign-in I must handle in simple language. Do not edit the downloaded skills. Tell me when setup is complete and ask me to start a new task.
```

The app assistant should perform and verify the equivalent command-center setup:

```text
codex plugin marketplace add troyuu/voice
codex plugin add jamaica-command-center@jamaica-tools
codex plugin list --json
```

After a successful install, start a new task so the plugin is loaded. Computer Use is an official, separate plugin; access to email, calendar, calling, CRM, and desktop apps is also connected separately. Jamaica should handle only permission dialogs, passwords, and 2FA.

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

## One-time app setup

This repository is the source package. It does not install itself and contains no credentials.

1. Install or open the current ChatGPT desktop app and sign in to Jamaica's Max account.
2. Use **Work locally** for tasks that need apps or files on her computer.
3. Install and enable the **Computer Use** plugin. On macOS, allow Screen Recording and Accessibility when prompted. On Windows, keep the target app visible on the active desktop.
4. Install and sign in to the email and calendar plugins Jamaica actually uses, such as Gmail/Google Calendar or Outlook Email/Outlook Calendar. Connect CRM or calling tools separately when available.
5. Use the friendly install prompt above. The assistant should add the public marketplace, install the plugin, verify it, and ask Jamaica to start a new task.
6. A technical administrator may copy `plugins/jamaica-command-center/runtime.example/` to a private local `runtime/` folder when persistent preferences are wanted. Never put passwords, API keys, contact exports, recordings, or real messages in the repository.

Jamaica does not need to manage the specialist files. ChatGPT Work can delegate suitable complex tasks from the skill instructions. The package also includes optional specialist definitions under `plugins/jamaica-command-center/.codex/agents/` for supported local Codex environments; do not ask Jamaica to manage those files herself.

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
