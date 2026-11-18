# Jamaica Command Center

Jamaica Command Center is a friendly resource pack for ChatGPT Work and Codex. Jamaica can describe a task in everyday language, see a short recommendation, and let the assistant complete the work with clear approval boundaries.

Public source: [github.com/troyuu/voice](https://github.com/troyuu/voice)

## Install with the ChatGPT desktop app

Open a local Codex task on Jamaica's computer and paste:

> Install Jamaica Command Center 0.3.0 on this computer from https://github.com/troyuu/voice. Clone the v0.3.0 release, read SETUP.md, and do the setup for me. Install all seven skills, connect my main assistant and six helpers to Hermes, and help me enable Computer Use. Walk me through my own sign-ins and permission prompts one at a time. Test each helper and desktop control, then tell me what's ready.

The [computer setup guide](SETUP.md) covers a fresh clone, a previous install, and an extracted release ZIP. The AI runs the installer and verifies the result. Jamaica completes account sign-ins in her own terminal or browser.

## What it helps with

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

## Private local state

The public repository contains blank examples only. The ignored `runtime/` folder is for Jamaica's private profile, preferences, tool map, workflow counts, and draft workflow proposals.

Run contributor checks with Python 3.11 or newer:

```text
python3 scripts/validate_pack.py
python3 -m unittest discover -s tests -v
```

The unit tests use local sample data. The separate Hermes connection check above sends synthetic challenges to the configured model.
