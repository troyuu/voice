# Jamaica Command Center

Jamaica Command Center is a friendly resource pack for ChatGPT Work and Codex. Jamaica can describe a task in everyday language, see a short recommendation, and let the assistant complete the work with clear approval boundaries.

Public source: [github.com/troyuu/voice](https://github.com/troyuu/voice)

## Install with the ChatGPT desktop app

Save `Jamaica-Command-Center-v0.3.1.zip` on Jamaica's computer. In the ChatGPT desktop app, open a Work task with local computer access and paste:

> Please install Jamaica Command Center v0.3.1 on my computer from the ZIP I was given. If you can’t see it, ask me to select it. Unzip it into a folder I can keep, check that it’s version 0.3.1, and follow SETUP.md. Use this copy; don’t clone the project from GitHub. Install all seven skills, connect my main assistant and six helpers to Hermes, and help me turn on Computer Use for the apps I choose. Guide me one step at a time when I need to sign in or approve something. Never ask me to paste a password or code into chat. Test with sample data only, then tell me what’s ready and what still needs me.

The [computer setup guide](SETUP.md) starts from the ZIP; no GitHub account is needed. Internet access is needed for missing tools and Hermes sign-in and verification. Jamaica completes sign-ins in her own terminal or browser.

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

### Learning a routine in v0.3.1

Jamaica can say **“Make me a helper that drafts reminders for suppliers who haven't replied.”** The assistant can also offer one after it helps her finish the same kind of task three times. It counts completed tasks, not screen activity, and she can say “don't track this.” Nothing runs in the background.

The assistant tests the helper on made-up examples, shows Jamaica what it does, and asks before turning it on. Each new helper uses an existing Hermes specialist and must get a test reply before installation. It needs no new sign-in if that specialist is already connected. Counts and drafts default to `.local/share/jamaica-command-center/runtime` under her user folder, outside the repository.

Run contributor checks with Python 3.11 or newer:

```text
python3 scripts/validate_pack.py
python3 -m unittest discover -s tests -v
```

The unit tests use local sample data. The separate Hermes connection check above sends synthetic challenges to the configured model.
